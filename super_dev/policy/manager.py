"""
开发：Excellent（11964948@qq.com）
功能：流水线策略管理器
作用：管理治理策略（default/balanced/enterprise 预设）
创建时间：2025-12-30
最后修改：2026-03-20
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from ..catalogs import CICD_PLATFORM_IDS, HOST_TOOL_IDS
from ..config import ProjectConfig
from ..utils import get_logger


@dataclass
class PipelinePolicy:
    """流水线治理策略"""

    require_redteam: bool = True
    require_quality_gate: bool = True
    require_rehearsal_verify: bool = True
    min_quality_threshold: int = 80
    allowed_cicd_platforms: list[str] = field(default_factory=lambda: list(CICD_PLATFORM_IDS))
    require_host_profile: bool = False
    required_hosts: list[str] = field(default_factory=list)
    enforce_required_hosts_ready: bool = False
    min_required_host_score: int = 80


class PipelinePolicyManager:
    """加载/保存/校验 pipeline policy"""

    POLICY_FILE = ".super-dev/policy.yaml"

    DEFAULT_POLICY = PipelinePolicy()
    PRESET_NAMES = ("default", "balanced", "enterprise")

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        self.policy_path = self.project_dir / self.POLICY_FILE
        self.logger = get_logger("policy_manager")

    def load(self) -> PipelinePolicy:
        if not self.policy_path.exists():
            return self._default_copy()

        try:
            loaded = yaml.safe_load(self.policy_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            self.logger.warning(f"策略文件 YAML 解析失败: {e}")
            return self._default_copy()
        except Exception as e:
            self.logger.warning(f"策略文件加载失败: {e}")
            return self._default_copy()

        raw = loaded if isinstance(loaded, dict) else {}
        merged = {**asdict(self.DEFAULT_POLICY), **raw}
        return self._from_raw(merged)

    def save(self, policy: PipelinePolicy) -> Path:
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        self.policy_path.write_text(
            yaml.dump(asdict(policy), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return self.policy_path

    def ensure_exists(self, *, preset: str = "default", force: bool = False) -> Path:
        if self.policy_path.exists() and not force:
            return self.policy_path
        return self.save(self.build_preset(preset))

    def build_preset(self, name: str) -> PipelinePolicy:
        preset = name.strip().lower()
        if preset == "default":
            return self._default_copy()
        if preset == "balanced":
            return PipelinePolicy(
                require_redteam=True,
                require_quality_gate=True,
                min_quality_threshold=82,
                allowed_cicd_platforms=list(CICD_PLATFORM_IDS),
                require_host_profile=True,
                required_hosts=[],
                enforce_required_hosts_ready=False,
                min_required_host_score=80,
            )
        if preset == "enterprise":
            return PipelinePolicy(
                require_redteam=True,
                require_quality_gate=True,
                min_quality_threshold=85,
                allowed_cicd_platforms=["github", "gitlab", "azure"],
                require_host_profile=True,
                required_hosts=["codex-cli", "claude-code"],
                enforce_required_hosts_ready=True,
                min_required_host_score=85,
            )
        raise ValueError(f"未知策略预设: {name}，可选: {', '.join(self.PRESET_NAMES)}")

    def validate_pipeline_args(self, args: Any, config: ProjectConfig) -> list[str]:
        policy = self.load()
        violations: list[str] = []

        if policy.require_redteam and bool(getattr(args, "skip_redteam", False)):
            violations.append("policy.require_redteam=true，不允许使用 --skip-redteam")

        if policy.require_quality_gate and bool(getattr(args, "skip_quality_gate", False)):
            violations.append("policy.require_quality_gate=true，不允许使用 --skip-quality-gate")

        if policy.require_rehearsal_verify and bool(getattr(args, "skip_rehearsal_verify", False)):
            violations.append("policy.require_rehearsal_verify=true，不允许使用 --skip-rehearsal-verify")

        requested_threshold = getattr(args, "quality_threshold", None)
        effective_threshold = (
            int(requested_threshold)
            if isinstance(requested_threshold, int)
            else int(config.quality_gate)
        )
        if effective_threshold < int(policy.min_quality_threshold):
            violations.append(
                f"质量阈值过低: {effective_threshold} < policy.min_quality_threshold({policy.min_quality_threshold})"
            )

        requested_cicd = str(getattr(args, "cicd", "all") or "all")
        if policy.allowed_cicd_platforms and requested_cicd not in policy.allowed_cicd_platforms:
            violations.append(
                f"当前 CI/CD 平台 {requested_cicd} 不在策略允许范围: {', '.join(policy.allowed_cicd_platforms)}"
            )

        if policy.require_host_profile:
            targets = [item for item in config.host_profile_targets if item]
            if not targets:
                violations.append("policy.require_host_profile=true，但 super-dev.yaml 未配置 host_profile_targets")
            elif policy.required_hosts:
                missing = [item for item in policy.required_hosts if item not in targets]
                if missing:
                    violations.append(f"host_profile_targets 缺少策略要求宿主: {', '.join(missing)}")

        if policy.required_hosts and policy.enforce_required_hosts_ready:
            compatibility_hosts = self._load_latest_host_compatibility_hosts()
            if compatibility_hosts is None:
                violations.append(
                    "策略要求 required_hosts 必须 ready，但未找到宿主兼容报告。请先执行: super-dev detect --auto --save-profile"
                )
            else:
                min_score = max(0, min(100, int(policy.min_required_host_score)))
                for host in policy.required_hosts:
                    host_data = compatibility_hosts.get(host)
                    if not isinstance(host_data, dict):
                        violations.append(f"策略要求宿主 {host} 未出现在最新兼容报告中")
                        continue
                    score = self._coerce_float(host_data.get("score"), default=0.0)
                    ready = bool(host_data.get("ready", False))
                    if not ready or score < float(min_score):
                        violations.append(
                            f"策略要求宿主 {host} ready 且 score >= {min_score}，当前 ready={ready}, score={score:.2f}"
                        )

        return violations

    def _from_raw(self, raw: dict[str, Any]) -> PipelinePolicy:
        require_redteam = bool(raw.get("require_redteam", True))
        require_quality_gate = bool(raw.get("require_quality_gate", True))
        require_rehearsal_verify = bool(raw.get("require_rehearsal_verify", True))
        min_quality_threshold = self._coerce_int(raw.get("min_quality_threshold"), default=80)
        min_quality_threshold = max(0, min(100, min_quality_threshold))
        allowed_cicd = self._normalize_list(raw.get("allowed_cicd_platforms"))
        allowed_cicd = [item for item in allowed_cicd if item in CICD_PLATFORM_IDS]
        if not allowed_cicd:
            allowed_cicd = list(CICD_PLATFORM_IDS)

        require_host_profile = bool(raw.get("require_host_profile", False))
        required_hosts = [item for item in self._normalize_list(raw.get("required_hosts")) if item in HOST_TOOL_IDS]
        enforce_required_hosts_ready = bool(raw.get("enforce_required_hosts_ready", False))
        min_required_host_score = self._coerce_int(raw.get("min_required_host_score"), default=80)
        min_required_host_score = max(0, min(100, min_required_host_score))

        return PipelinePolicy(
            require_redteam=require_redteam,
            require_quality_gate=require_quality_gate,
            require_rehearsal_verify=require_rehearsal_verify,
            min_quality_threshold=min_quality_threshold,
            allowed_cicd_platforms=allowed_cicd,
            require_host_profile=require_host_profile,
            required_hosts=required_hosts,
            enforce_required_hosts_ready=enforce_required_hosts_ready,
            min_required_host_score=min_required_host_score,
        )

    def _default_copy(self) -> PipelinePolicy:
        return PipelinePolicy(**asdict(self.DEFAULT_POLICY))

    def _normalize_list(self, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    def _coerce_int(self, value: object, default: int) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return default

    def _coerce_float(self, value: object, default: float) -> float:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return default
            try:
                return float(text)
            except ValueError:
                return default
        return default

    def _load_latest_host_compatibility_hosts(self) -> dict[str, Any] | None:
        output_dir = self.project_dir / "output"
        if not output_dir.exists():
            return None
        candidates = list(output_dir.glob("*-host-compatibility.json"))
        history_dir = output_dir / "host-compatibility-history"
        if history_dir.exists():
            candidates.extend(history_dir.glob("*-host-compatibility-*.json"))
        if not candidates:
            return None
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self.logger.warning(f"宿主兼容性报告解析失败: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"宿主兼容性报告加载失败: {e}")
            return None
        if not isinstance(payload, dict):
            return None
        compatibility = payload.get("compatibility", {})
        if not isinstance(compatibility, dict):
            return None
        hosts = compatibility.get("hosts", {})
        if not isinstance(hosts, dict):
            return None
        return hosts
