# -*- coding: utf-8 -*-
"""
需求解析器 - 将自然语言需求转换为可执行结构
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RequirementBlueprint:
    """结构化需求"""

    spec_name: str
    req_name: str
    description: str
    scenarios: list[dict]

    def to_dict(self) -> dict:
        return {
            "spec_name": self.spec_name,
            "req_name": self.req_name,
            "description": self.description,
            "scenarios": self.scenarios,
        }


class RequirementParser:
    """将一句话需求解析为规范、阶段和前端模块"""

    _KEYWORD_RULES = [
        {
            "spec_name": "auth",
            "req_name": "secure-authentication",
            "keywords": ("登录", "注册", "认证", "oauth", "auth", "password", "账号"),
            "description": "系统应支持安全认证与会话管理。",
            "scenario": {
                "given": "用户处于未登录状态",
                "when": "提交有效凭据",
                "then": "系统完成鉴权并建立安全会话",
            },
        },
        {
            "spec_name": "profile",
            "req_name": "profile-management",
            "keywords": ("用户中心", "个人资料", "profile", "account", "设置"),
            "description": "用户应可查看和更新个人资料与偏好设置。",
            "scenario": {
                "given": "用户已经登录",
                "when": "在个人中心提交更新",
                "then": "资料变更被持久化并反馈成功状态",
            },
        },
        {
            "spec_name": "search",
            "req_name": "search-and-filter",
            "keywords": ("搜索", "筛选", "filter", "query", "检索"),
            "description": "系统应提供可组合的搜索和筛选能力。",
            "scenario": {
                "given": "列表数据可访问",
                "when": "用户输入关键词并选择筛选条件",
                "then": "系统返回符合条件的数据结果",
            },
        },
        {
            "spec_name": "workflow",
            "req_name": "workflow-orchestration",
            "keywords": ("流程", "工作流", "pipeline", "审批", "自动化", "编排"),
            "description": "系统应支持可追踪的流程编排与状态流转。",
            "scenario": {
                "given": "业务对象处于待处理状态",
                "when": "触发流程节点执行",
                "then": "状态按规则推进并记录审计信息",
            },
        },
        {
            "spec_name": "analytics",
            "req_name": "dashboard-insights",
            "keywords": ("报表", "统计", "dashboard", "分析", "指标", "图表"),
            "description": "系统应提供关键指标看板与洞察视图。",
            "scenario": {
                "given": "业务数据已入库",
                "when": "用户访问分析页面",
                "then": "系统渲染最新指标并支持维度切换",
            },
        },
        {
            "spec_name": "notification",
            "req_name": "notification-center",
            "keywords": ("通知", "消息", "提醒", "订阅", "message"),
            "description": "系统应提供通知中心和订阅推送能力。",
            "scenario": {
                "given": "触发业务事件",
                "when": "事件匹配通知规则",
                "then": "用户收到站内消息或外部通知",
            },
        },
        {
            "spec_name": "billing",
            "req_name": "payment-and-billing",
            "keywords": ("支付", "账单", "billing", "付款", "订阅计费"),
            "description": "系统应支持支付流程、账单记录与对账。",
            "scenario": {
                "given": "用户发起付费行为",
                "when": "支付网关返回交易结果",
                "then": "系统更新订单状态并生成账单条目",
            },
        },
        {
            "spec_name": "content",
            "req_name": "content-management",
            "keywords": ("内容", "文章", "帖子", "cms", "发布", "管理"),
            "description": "系统应支持内容的创建、审核与发布管理。",
            "scenario": {
                "given": "编辑已填写内容草稿",
                "when": "提交发布申请",
                "then": "内容进入审核并在通过后上线",
            },
        },
    ]

    _SOURCE_DIRS = (
        "src",
        "app",
        "backend",
        "frontend",
        "services",
        "api",
        "server",
        "client",
        "lib",
    )

    _PROJECT_FILES = (
        "package.json",
        "requirements.txt",
        "go.mod",
        "pom.xml",
        "Cargo.toml",
        "pyproject.toml",
    )

    def parse_requirements(self, description: str) -> list[dict]:
        """解析结构化需求列表"""
        text = (description or "").strip()
        lowered = text.lower()
        parsed: list[RequirementBlueprint] = []

        # 永远生成一个总览需求，确保流程可落地
        parsed.append(
            RequirementBlueprint(
                spec_name="core",
                req_name="business-core-flow",
                description=f"系统应完整支持以下业务目标：{text or '核心业务流程实现'}",
                scenarios=[
                    {
                        "given": "用户进入系统首页",
                        "when": "按业务路径完成主要操作",
                        "then": "系统成功返回结果并展示下一步引导",
                    }
                ],
            )
        )

        for rule in self._KEYWORD_RULES:
            if any(keyword.lower() in lowered for keyword in rule["keywords"]):
                parsed.append(
                    RequirementBlueprint(
                        spec_name=rule["spec_name"],
                        req_name=rule["req_name"],
                        description=rule["description"],
                        scenarios=[rule["scenario"]],
                    )
                )

        # 如果没有命中任何规则，基于描述短语生成两个通用需求
        if len(parsed) == 1:
            subject = self._extract_subject(text)
            parsed.extend(
                [
                    RequirementBlueprint(
                        spec_name="experience",
                        req_name="task-oriented-interface",
                        description=f"系统应提供围绕“{subject}”的任务导向界面。",
                        scenarios=[
                            {
                                "given": "用户进入主界面",
                                "when": "执行一个完整任务",
                                "then": "任务可在最少步骤中完成",
                            }
                        ],
                    ),
                    RequirementBlueprint(
                        spec_name="operation",
                        req_name="observability-and-maintenance",
                        description="系统应具备可观测性、日志和可维护的运维能力。",
                        scenarios=[
                            {
                                "given": "系统在生产环境运行",
                                "when": "出现异常或性能下降",
                                "then": "可通过监控与日志快速定位问题",
                            }
                        ],
                    ),
                ]
            )

        return self._deduplicate_requirements(parsed)

    def detect_scenario(self, project_dir: Path) -> str:
        """检测 0-1 / 1-N+1 场景"""
        path = Path(project_dir).resolve()
        has_source = any((path / item).exists() for item in self._SOURCE_DIRS)
        has_project_file = any((path / item).exists() for item in self._PROJECT_FILES)
        return "1-N+1" if (has_source or has_project_file) else "0-1"

    def build_execution_phases(self, scenario: str, requirements: list[dict]) -> list[dict]:
        """生成执行阶段计划"""
        req_titles = [req.get("req_name", "requirement") for req in requirements]
        focus = ", ".join(req_titles[:4])
        if len(req_titles) > 4:
            focus += " ..."

        if scenario == "0-1":
            return [
                {
                    "id": "phase-1",
                    "title": "需求对齐与文档冻结",
                    "objective": "冻结 PRD/架构/UIUX 文档并建立执行边界。",
                    "deliverables": ["PRD v1", "Architecture v1", "UIUX v1", "风险清单"],
                },
                {
                    "id": "phase-2",
                    "title": "前端先行交付",
                    "objective": "先交付可演示前端，以便快速验证业务流程。",
                    "deliverables": ["前端信息架构", "页面骨架", "设计令牌", "交互演示"],
                },
                {
                    "id": "phase-3",
                    "title": "后端与数据能力",
                    "objective": "围绕核心流程构建 API、数据模型和权限控制。",
                    "deliverables": ["API 契约", "数据库迁移", "服务模块", "鉴权策略"],
                },
                {
                    "id": "phase-4",
                    "title": "联调与质量门禁",
                    "objective": "完成端到端联调并通过质量门禁。",
                    "deliverables": ["红队审查报告", "质量门禁报告", "回归测试清单"],
                },
                {
                    "id": "phase-5",
                    "title": "上线与迭代计划",
                    "objective": "准备上线交付并规划 1-N+1 迭代路线。",
                    "deliverables": ["发布清单", "运维手册", "迭代 Backlog"],
                },
            ]

        return [
            {
                "id": "phase-1",
                "title": "增量需求与影响分析",
                "objective": "确认变更边界、兼容性和风险。",
                "deliverables": ["变更影响矩阵", "兼容性策略", "回滚方案"],
            },
            {
                "id": "phase-2",
                "title": "前端模块扩展",
                "objective": "优先扩展用户可感知模块并保持设计一致性。",
                "deliverables": ["新增页面/组件", "交互更新", "文案与埋点更新"],
            },
            {
                "id": "phase-3",
                "title": "后端能力扩展",
                "objective": "按规范增加接口与数据能力，避免破坏存量系统。",
                "deliverables": ["增量 API", "迁移脚本", "灰度开关"],
            },
            {
                "id": "phase-4",
                "title": "回归验证与发布",
                "objective": "覆盖关键链路并完成灰度/正式发布。",
                "deliverables": ["回归测试结果", "发布报告", "监控告警确认"],
            },
            {
                "id": "phase-5",
                "title": "持续优化",
                "objective": f"围绕 {focus or '核心需求'} 持续迭代优化。",
                "deliverables": ["性能优化清单", "体验优化清单", "后续版本计划"],
            },
        ]

    def build_frontend_modules(self, requirements: list[dict]) -> list[dict]:
        """生成前端优先交付模块清单"""
        modules = [
            {
                "name": "需求总览面板",
                "goal": "集中展示需求摘要、优先级和执行状态。",
                "core_elements": ["需求卡片", "优先级标签", "状态标识"],
            },
            {
                "name": "文档工作台",
                "goal": "统一管理 PRD、架构和 UIUX 文档入口。",
                "core_elements": ["文档卡片", "版本信息", "快速跳转"],
            },
            {
                "name": "执行路线图",
                "goal": "可视化 0-1 / 1-N+1 阶段任务。",
                "core_elements": ["阶段时间线", "里程碑", "风险提示"],
            },
        ]

        for req in requirements[:4]:
            modules.append(
                {
                    "name": f"{req.get('spec_name', 'core')} 模块",
                    "goal": req.get("description", "实现核心业务能力"),
                    "core_elements": [
                        f"{req.get('req_name', 'requirement')} 视图",
                        "关键交互入口",
                        "状态反馈组件",
                    ],
                }
            )

        return modules

    def _extract_subject(self, description: str) -> str:
        cleaned = re.sub(r"\s+", " ", description.strip())
        if not cleaned:
            return "核心业务"
        separators = r"[，,。.!！？;；/]+"
        segment = re.split(separators, cleaned)[0]
        return segment[:40]

    def _deduplicate_requirements(self, requirements: list[RequirementBlueprint]) -> list[dict]:
        seen = set()
        result = []
        for item in requirements:
            key = (item.spec_name, item.req_name)
            if key in seen:
                continue
            seen.add(key)
            result.append(item.to_dict())
        return result
