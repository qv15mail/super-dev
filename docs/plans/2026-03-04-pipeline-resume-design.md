# Super Dev Pipeline Resume 设计说明（2026-03-04）

## 目标

新增失败恢复入口，支持在 pipeline 失败后快速继续执行，避免每次都从第 0 阶段重跑。

## 命令设计

- `super-dev run --resume`
  - 读取 `.super-dev/runs/last-pipeline.json`
  - 最近状态为 `failed` / `running` 时触发恢复
  - 复用上次 pipeline 参数并设置 `resume=True`

## 恢复策略（当前版本）

1. pipeline 每次运行都会写入运行状态文件（running/success/failed）。
2. `--resume` 模式下读取运行状态与 metrics，恢复上下文（如 `scenario`、`change_id`、增强需求）。
3. 根据失败阶段进行“安全恢复映射”：
   - 0-4：全量重跑（保证上游上下文一致）
   - 5：从 5 继续
   - 6：默认从 5 继续（需要 redteam 输入）；若本次 `--skip-redteam` 则可从 6
   - 7-8：从失败阶段继续
   - 9-12：统一从 9 继续（保证 9-11 产物与汇总变量完整）
4. 各阶段支持 `resume 跳过` 标记，避免无意义重跑。
5. 恢复前执行工件完整性校验：
   - 当恢复起点在 5-8 阶段时，若缺少前置文档产物（research/prd/architecture/uiux/execution-plan/frontend-blueprint），自动降级到第 1 阶段重建。
   - 若未来恢复起点落在第 4 阶段且缺少 Spec 变更目录，自动降级到第 3 阶段。
6. 每次恢复都会生成审计工件：
   - `output/<project>-resume-audit.json`
   - `output/<project>-resume-audit.md`
   - 记录检测失败阶段、初始恢复点、最终恢复点、降级原因和执行结果。

## 约束与取舍

- 当前优先“安全恢复”而非“激进最小恢复”：
  - 4 阶段及以前失败，仍走全量重建。
  - 9-12 失败统一回到 9，避免后处理变量不完整。
- 恢复时允许 `running` 状态作为“中断恢复”入口，避免异常退出后无法续跑。
- 已引入上下文快照机制，后续可继续扩展到更细粒度工件级恢复。

## 验收

- 新增 `run --resume` 命令可用。
- 最近失败记录不存在时返回明确错误。
- 最近失败/中断记录存在时，能正确回放参数并进入恢复执行。
- 恢复策略映射（5/6/7/8/9-12）有自动化测试覆盖。
- 工件缺失时恢复起点自动降级，避免“恢复后半程再失败”的无效重试。
