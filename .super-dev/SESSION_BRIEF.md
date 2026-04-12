# Super Dev Session Brief

- 动作类型: 继续当前流程
- 当前步骤: 先做前端与运行验证
- 当前状态: missing_frontend
- 用户下一步: 先完成前端主流程和运行验证，再考虑后端和交付。
- 系统建议动作: 在宿主里说“继续当前流程，进入前端实现与运行验证”
- 推荐宿主: Claude Code
- 工作流状态 JSON: /Users/weiyou/Documents/kaifa/super-dev/.super-dev/workflow-state.json
- 最新历史快照: /Users/weiyou/Documents/kaifa/super-dev/.super-dev/workflow-history/latest.json
- 事件日志: /Users/weiyou/Documents/kaifa/super-dev/.super-dev/workflow-events.jsonl
- Hook 审计日志: /Users/weiyou/Documents/kaifa/super-dev/.super-dev/hook-history.jsonl

## 运行时 Harness 摘要
- Workflow Continuity: pass
- Framework Harness: fail
- Hook Audit Trail: fail
- 你现在可以直接说: 先做前端 / 先把页面跑起来 / 先做可演示版本 / 继续
- 自然语言示例: 先做前端, 先把页面跑起来, 先做可演示版本

## 现实场景怎么做
- 第二天回来继续开发: `回到宿主里说“继续当前流程”`
- 我只想知道现在先做什么: `回到宿主里说“现在下一步是什么”`
- 当前先推进前端实现: `在宿主里说“继续当前流程，进入前端实现与运行验证”`
- 本地流程跑到一半中断后恢复: `回到宿主里说“继续当前流程，不要重新开题”`
- 宿主第一句: /super-dev "继续当前项目“Super Dev 是一个本地 Python CLI 与宿主规则协同的 AI Coding 治理工具，用 research-first 流水线约束文档冻结、Spec 拆解、前端优先验证、质量门禁和交付证据闭环。”的 Super Dev 流程，不要当作普通聊天。先读取 .super-dev/SESSION_BRIEF.md、.super-dev/workflow-state.json、.super-dev/WORKFLOW.md、output/*、.super-dev/review-state/* 和最近的 tasks.md。当前步骤是“先做前端与运行验证”。只要仓库里还有活动的 Super Dev 上下文，后续自然语言需求默认继续当前流程，而不是切回普通聊天。"
- 原因: 当前尚未完成前端实现与运行验证。
- 依据: 缺少通过的 output/*-frontend-runtime.json

## 会话连续性规则
- 只要仓库里还有活动的 Super Dev 上下文，后续自然语言需求默认继续当前流程，而不是切回普通聊天。

## 最近流程快照
- 2026-04-12T11:37:30.216043+00:00 · 先做前端与运行验证
- 2026-04-12T11:37:30.192914+00:00 · 先做前端与运行验证
- 2026-04-12T11:37:30.184506+00:00 · 先做前端与运行验证

## 最近状态事件
- 2026-04-12T11:37:30.232126+00:00 · 流程状态已保存 · 先做前端与运行验证
- 2026-04-12T11:37:30.216043+00:00 · 流程状态已保存 · 先做前端与运行验证
- 2026-04-12T11:37:30.192914+00:00 · 流程状态已保存 · 先做前端与运行验证

## 最近关键时间线
- 2026-04-12T11:37:30.232126+00:00 · 流程快照 · 先做前端与运行验证
- 2026-04-12T11:37:30.232126+00:00 · 流程事件 · 流程状态已保存 · 先做前端与运行验证
- 2026-04-12T11:37:30.216043+00:00 · 流程快照 · 先做前端与运行验证
- 2026-04-12T11:37:30.216043+00:00 · 流程事件 · 流程状态已保存 · 先做前端与运行验证
- 2026-04-12T11:37:30.192914+00:00 · 流程快照 · 先做前端与运行验证

## 离开当前流程的唯一条件
- 用户明确说要取消当前流程。
- 用户明确说要重新开始一条新的流程。
- 用户明确说要切回普通聊天，而不是继续 Super Dev。

## 下次回来怎么继续
- 回到宿主后，直接说“继续当前流程”。
- 如果只想知道现在先做什么，就在宿主里说“现在下一步是什么”。
