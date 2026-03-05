# Super Dev Wizard Onboarding 设计说明（2026-03-03）

## 背景

当前 `super-dev "需求"` 已支持直达模式，但对非技术用户仍有两个门槛：

1. 不知道可用参数（domain/backend/cicd 等）。
2. 不知道该如何选择默认技术栈与交付策略。

因此新增 `super-dev wizard`，提供零门槛引导入口。

## 目标

1. 提供可交互向导，支持逐步输入需求与技术偏好。
2. 提供可脚本化模式（`--idea` + `--quick`），便于自动化场景。
3. 与现有 `pipeline` 复用同一主链路，避免重复实现和行为漂移。

## 方案

### 命令接口

- `super-dev wizard`：交互模式。
- `super-dev wizard --idea "..." --quick`：非交互快速模式。
- 支持可选覆盖参数：`--platform --frontend --backend --domain --cicd --offline --name`。

### 执行策略

1. 向导收集参数（缺省时按默认值）。
2. 输出一次“向导结果”摘要供用户确认。
3. 组装 `argparse.Namespace` 并直接复用 `_cmd_pipeline` 执行完整流水线。

### 默认值

- platform: `web`
- frontend: `react`
- backend: `node`
- domain: `saas`
- cicd: `all`

## 错误处理

- `--quick` 且未提供 `--idea`：返回参数错误（exit code 2）。
- 非交互环境且未提供 `--idea`：提示必须显式提供需求并返回 2。
- 输入值不在可选范围：回落默认值并给出 warning。

## 测试与验收

新增集成测试：

1. `wizard --idea --quick` 可跑完整流水线并产出核心文件。
2. `wizard --quick` 无 idea 时正确失败（返回 2）。

验收标准：

- `wizard -h` 能看到完整参数说明。
- `pytest tests/integration/test_cli.py` 全通过。
- 在临时目录实跑 `wizard --idea` 可产出交付物和指标文件。
