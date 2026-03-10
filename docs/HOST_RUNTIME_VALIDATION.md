# 宿主运行时验收矩阵

这份文档只回答一件事：

- 如何确认一个宿主不只是“接入文件存在”，而是真正能按 Super Dev 流水线工作。

## 验收目标

每个宿主至少要通过这 5 项：

1. 触发命令能进入 Super Dev 流水线
2. 首轮响应明确进入 `research`
3. 真实写入：
- `output/*-research.md`
- `output/*-prd.md`
- `output/*-architecture.md`
- `output/*-uiux.md`
4. 三文档后真实暂停等待确认
5. 确认后能继续进入 Spec、前端运行验证、后端与交付阶段

补充：

- `iflow` 这类宿主如果先报 `Invalid API key provided`，先修宿主鉴权，再做运行时验收。

## 推荐执行方式

先导出当前项目的宿主运行时验收矩阵：

```bash
super-dev integrate validate --auto
```

自动修当前机器已检测宿主，再导出矩阵：

```bash
super-dev integrate audit --auto --repair --force
super-dev integrate validate --auto
```

导出 JSON：

```bash
super-dev integrate validate --auto --json
```

记录某个宿主已经真人通过：

```bash
super-dev integrate validate --target codex-cli --status passed --comment "首轮先进入 research，三文档已真实落盘"
```

如果真人验收失败：

```bash
super-dev integrate validate --target trae --status failed --comment "仍然只在会话里描述流程，没有真实落盘"
```

## 当前宿主分组

### Slash 宿主

- `claude-code`
- `codebuddy`
- `codebuddy-cli`
- `cursor`
- `cursor-cli`
- `gemini-cli`
- `iflow`
- `kiro-cli`
- `opencode`
- `qoder`
- `qoder-cli`
- `windsurf`
- `antigravity`

触发方式：

```text
/super-dev 你的需求
```

### Text Trigger 宿主

- `codex-cli`
- `kimi-cli`
- `kiro`
- `trae`

触发方式：

```text
super-dev: 你的需求
```

## 运行时验收记录模板

用这张表记录每个宿主的真人会话结果，而不是只依赖静态接入审计。

| 宿主 | 触发方式 | 首轮进入 research | 三文档落盘 | 确认门生效 | resume 可用 | 当前状态 | 备注 |
|---|---|---|---|---|---|---|---|
| claude-code | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| codebuddy-cli | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| codebuddy | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| codex-cli | `super-dev:` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| cursor-cli | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| cursor | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| gemini-cli | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| iflow | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 | 先确认 `/auth` 或 API key |
| kimi-cli | `super-dev:` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| kiro-cli | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| kiro | `super-dev:` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| opencode | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| qoder-cli | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| qoder | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| windsurf | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| antigravity | `/super-dev` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |
| trae | `super-dev:` | 待验收 | 待验收 | 待验收 | 待验收 | 待验收 |  |

## 真人验收步骤

1. 在项目目录完成 `onboard` 或 `audit --repair`
2. 完全关闭宿主
3. 重新打开项目
4. 新开一个宿主会话
5. 先发 Smoke 语句
6. 确认首轮响应
7. 再发正式需求
8. 检查 `output/*` 是否真实生成
9. 检查是否在三文档后暂停等待确认

## 通过标准

1. 宿主不是只在聊天里描述流程
2. 宿主真实写入文档文件
3. 宿主真实停在确认门
4. 宿主恢复后能继续跑后续阶段
