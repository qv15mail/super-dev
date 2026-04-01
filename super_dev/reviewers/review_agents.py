"""
三 Agent 并行审查框架。

使用三个并行 agent 分别审查代码复用、代码质量和效率。
Super Dev 将此模式适配到 pipeline 的 redteam 和 qa 阶段。

开发：Super Dev Team
创建时间：2026-03-31
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReviewFinding:
    """单个审查发现"""

    agent: str  # reuse / quality / efficiency / security
    category: str
    severity: str  # critical / high / medium / low
    description: str
    file_path: str = ""
    line_number: int = 0
    suggestion: str = ""
    is_false_positive: bool = False


@dataclass
class ReviewReport:
    """三 Agent 审查汇总报告"""

    findings: list[ReviewFinding] = field(default_factory=list)
    agent_summaries: dict[str, str] = field(default_factory=dict)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical" and not f.is_false_positive)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "high" and not f.is_false_positive)

    @property
    def actionable_findings(self) -> list[ReviewFinding]:
        return [f for f in self.findings if not f.is_false_positive]

    def pass_quality_gate(self, max_critical: int = 0, max_high: int = 3) -> bool:
        return self.critical_count <= max_critical and self.high_count <= max_high


# ─────────────────────────────────────────────────────────────────────
# Agent 1: 代码复用审查
# ─────────────────────────────────────────────────────────────────────

REUSE_REVIEW_PROMPT = """## Agent 1: 代码复用审查

对每个变更：

1. **搜索现有 utilities 和 helpers** 是否可以替代新写的代码。在代码库中查找类似模式——
   常见位置是 utils 目录、共享模块、以及变更文件相邻的文件。
2. **标记任何重复现有功能的新函数。** 建议使用现有函数替代。
3. **标记任何可使用现有工具的内联逻辑** — 手写的字符串处理、手动路径操作、
   自定义环境检查、临时类型守卫等是常见候选。
"""


# ─────────────────────────────────────────────────────────────────────
# Agent 2: 代码质量审查 (7 个检查维度)
# ─────────────────────────────────────────────────────────────────────

QUALITY_REVIEW_PROMPT = """## Agent 2: 代码质量审查

审查相同变更中的 hacky 模式：

1. **冗余状态**: 重复现有状态、可推导的缓存值、可以直接调用的 observer/effect
2. **参数膨胀**: 向函数添加新参数而不是泛化或重构现有参数
3. **复制粘贴微变**: 近似重复的代码块，应统一为共享抽象
4. **抽象泄漏**: 暴露应封装的内部细节，或打破现有抽象边界
5. **字符串类型化**: 在代码库已有常量、枚举（字符串联合）或品牌类型的地方使用原始字符串
6. **不必要的嵌套**: 不增加布局价值的包装元素/组件
7. **不必要的注释**: 解释代码做什么（好的命名已经做到了）、叙述变更、或引用任务/调用者的注释
"""


# ─────────────────────────────────────────────────────────────────────
# Agent 3: 效率审查 (7 个检查维度)
# ─────────────────────────────────────────────────────────────────────

EFFICIENCY_REVIEW_PROMPT = """## Agent 3: 效率审查

审查相同变更的效率问题：

1. **不必要的工作**: 冗余计算、重复文件读取、重复网络/API 调用、N+1 模式
2. **错过的并发机会**: 可并行运行的独立操作被串行执行
3. **热路径膨胀**: 在启动或每请求/每渲染的热路径上新增阻塞工作
4. **循环无操作更新**: 在轮询循环、定时器或事件处理器中无条件触发的状态/存储更新——
   添加变更检测守卫，使下游消费者在无变化时不被通知
5. **不必要的存在检查**: 操作前先检查文件/资源是否存在（TOCTOU 反模式）——
   直接操作并处理错误
6. **内存**: 无界数据结构、缺失的清理、事件监听器泄漏
7. **过度广泛的操作**: 只需要部分时读取整个文件、只需要一个时加载所有条目
"""


# ─────────────────────────────────────────────────────────────────────
# Agent 4: 安全审查
# ─────────────────────────────────────────────────────────────────────

SECURITY_REVIEW_PROMPT = """## Agent 4: 安全审查

检查变更中的安全问题：

1. **硬编码凭据**: API keys、密码、tokens、数据库连接字符串
2. **注入漏洞**: SQL 注入、命令注入、XSS、SSRF、路径遍历
3. **认证绕过**: 未受保护的端点、缺失的权限检查、JWT 配置错误
4. **敏感数据泄漏**: 日志中的密码、错误消息中的内部路径、响应中的堆栈信息
5. **依赖风险**: 已知漏洞的依赖、未锁定的版本、不可信的包源
6. **加密弱点**: 弱哈希算法、硬编码 IV/盐值、不安全的随机数生成
7. **OWASP Top 10**: 按 OWASP 2021 Top 10 逐项检查
"""


def build_parallel_review_prompt(
    change_description: str,
    files_changed: list[str] | None = None,
    diff_content: str = "",
) -> dict[str, str]:
    """构建四个并行审查 agent 的 prompt。

    Returns:
        dict 映射 agent 名到其完整 prompt
    """
    context = f"""# 并行代码审查

## 变更描述
{change_description}

## 变更文件
{chr(10).join(f'- {f}' for f in (files_changed or []))}

## Diff 内容
```
{diff_content[:5000]}
```
"""

    return {
        "reuse": context + REUSE_REVIEW_PROMPT,
        "quality": context + QUALITY_REVIEW_PROMPT,
        "efficiency": context + EFFICIENCY_REVIEW_PROMPT,
        "security": context + SECURITY_REVIEW_PROMPT,
    }


def aggregate_findings(
    agent_results: dict[str, list[ReviewFinding]],
) -> ReviewReport:
    """聚合四个 agent 的审查结果。

    Args:
        agent_results: agent 名 → 发现列表

    Returns:
        ReviewReport 汇总
    """
    report = ReviewReport()

    for agent_name, findings in agent_results.items():
        report.findings.extend(findings)
        # 为每个 agent 生成摘要
        actionable = [f for f in findings if not f.is_false_positive]
        if actionable:
            report.agent_summaries[agent_name] = (
                f"{len(actionable)} actionable findings "
                f"({sum(1 for f in actionable if f.severity == 'critical')} critical, "
                f"{sum(1 for f in actionable if f.severity == 'high')} high)"
            )
        else:
            report.agent_summaries[agent_name] = "No issues found"

    return report


# ─────────────────────────────────────────────────────────────────────
# 对抗性验证 Prompt
# ─────────────────────────────────────────────────────────────────────

ADVERSARIAL_VERIFICATION_PROMPT = """# 对抗性验证

你是验证专家。你的工作不是确认实现有效——而是尝试打破它。

## 已知失败模式

你有两个失败模式需要警惕：

**验证回避**: 面对检查时，你找到理由不运行它——阅读代码、叙述测试计划、写下 PASS。
**被前 80% 诱惑**: 看到精美 UI 或通过的测试就倾向于 PASS，没注意到按钮不工作、状态消失、后端崩溃。

## 识别你的合理化借口

- "代码看起来正确" → 阅读不是验证。运行它。
- "测试已经通过了" → 实现者是 LLM，独立验证。
- "可能没问题" → "可能"不是已验证。
- "这要花太长时间" → 不是你该做的决定。

## 通用验证步骤

1. 读取 README / 配置文件了解构建/测试命令
2. 运行构建（如果适用）。构建失败 = 自动 FAIL
3. 运行测试套件（如果有）。测试失败 = 自动 FAIL
4. 运行 lint / 类型检查（如果配置了）
5. 检查相关代码的回归

## 对抗性探测

- **并发**: 并行请求到 create-if-not-exists → 有重复吗？
- **边界值**: 0, -1, 空字符串, 超长, unicode, MAX_INT
- **幂等性**: 同一变更请求执行两次 → 重复？错误？正确无操作？
- **孤立操作**: 删除/引用不存在的 ID

## 输出格式

每个检查必须有 `Command run:` + `Output observed:` + `Result: PASS/FAIL`。
没有 Command run 的检查不是 PASS——是跳过。

最终: `VERDICT: PASS` 或 `VERDICT: FAIL` 或 `VERDICT: PARTIAL`
"""
