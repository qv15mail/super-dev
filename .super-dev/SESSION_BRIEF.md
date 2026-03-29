# Super Dev Session Brief

- 动作类型: 继续当前流程
- 当前步骤: 继续当前流程
- 当前状态: failed
- 用户下一步: 按当前状态面板继续，不要重新开一轮普通聊天。
- 机器侧动作: super-dev run --resume
- 推荐宿主: Claude Code
- 工作流状态 JSON: /Users/weiyou/Documents/kaifa/super-dev/.super-dev/workflow-state.json
- 你现在可以直接说: 继续 / 下一步 / 按当前流程往下做
- 自然语言示例: 继续, 下一步, 按当前流程往下做
- 宿主第一句: /super-dev "继续当前项目“confirm docs --comment ok”的 Super Dev 流程，不要当作普通聊天。先读取 .super-dev/SESSION_BRIEF.md、.super-dev/workflow-state.json、.super-dev/WORKFLOW.md、output/*、.super-dev/review-state/* 和最近的 tasks.md。当前步骤是“继续当前流程”。只要仓库里还有活动的 Super Dev 上下文，后续自然语言需求默认继续当前流程，而不是切回普通聊天。"
- 原因: 当前仓库存在运行态、确认门或返工门，需要先沿当前流程继续。
- 依据: run_status=failed

## 会话连续性规则
- 只要仓库里还有活动的 Super Dev 上下文，后续自然语言需求默认继续当前流程，而不是切回普通聊天。

## 离开当前流程的唯一条件
- 用户明确说要取消当前流程。
- 用户明确说要重新开始一条新的流程。
- 用户明确说要切回普通聊天，而不是继续 Super Dev。

## 下次回来怎么继续
- 回到项目根目录后，优先执行 `super-dev resume`。
- 如果只想看系统推荐的唯一下一步，也可以执行 `super-dev next`。
