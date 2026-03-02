# Release Runbook

面向生产发布的标准流程（商业级），用于降低发布失败和回滚风险。

## 1. 发布前准备

- 确认版本号已更新：`pyproject.toml`
- 确认更新日志已更新：`CHANGELOG.md`
- 确认主分支状态与发布分支策略（建议从 `main` 发布）
- 确认 PyPI 凭证可用（`~/.pypirc` 或 CI Secret）
- GitHub Tag 发布必须配置 `PYPI_API_TOKEN`（未配置将被 CD 强制阻断）

## 2. 预检（必须通过）

运行非交互预检：

```bash
./scripts/preflight.sh
```

调试模式（工作区有未提交内容时）：

```bash
./scripts/preflight.sh --allow-dirty --skip-package
```

如需临时跳过交付门禁烟雾验证（仅本地调试）：

```bash
./scripts/preflight.sh --skip-delivery-smoke
```

预检覆盖项：

- `ruff`
- `mypy`
- `pytest`
- `scripts/check_delivery_ready.py --smoke`（交付门禁烟雾验证）
- `bandit`（`-ll`，仅阻断 medium/high）
- `pip-audit`
- `tests/benchmark.py`
- `python -m build`
- `twine check dist/*`

报告输出目录：

- `output/release/preflight-<timestamp>/summary.txt`
- 对应步骤日志和安全扫描 JSON 文件

## 3. 正式发布步骤

1. 运行预检并确保通过。
2. 构建并检查包：
   - `rm -rf dist/ build/ *.egg-info`
   - `python3 -m build`
   - `twine check dist/*`
3. 上传 PyPI：
   - `twine upload dist/*`
4. 打 Tag 并推送：
   - `git tag v<version>`
   - `git push origin v<version>`
5. 创建 GitHub Release（附变更说明和风险提示）。

## 4. 发布后验证

- `pip install --no-cache-dir super-dev==<version>`
- `super-dev --version`
- 核心命令冒烟：
  - `super-dev --help`
  - `super-dev expert --list`

## 5. 回滚策略（必须预案）

注意：PyPI 不允许删除已发布版本，推荐以下流程：

1. 若发现严重问题，先在 PyPI 对问题版本执行 `yank`。
2. 立即发布修复补丁版本（`x.y.(z+1)`）。
3. 在 GitHub Release 和 CHANGELOG 明确标注受影响版本和规避方案。

示例：

```bash
# 重新构建补丁版本
rm -rf dist/ build/ *.egg-info
python3 -m build
twine upload dist/*
```

## 6. 紧急处理

- 发现安全问题：优先发补丁版本并在 CHANGELOG 增加 `Security` 分类。
- 发现安装失败：先做 yanked，再发布修复版本并验证干净环境安装。
- 发现 CLI 关键命令回归：先阻断对外公告，修复后再发布。
