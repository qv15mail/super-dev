# Host Runtime Validation

这份文档定义的是 host runtime validation 的最小验收面。

目标不是只确认配置生成了，而是确认宿主真的会按协议执行：

- 先进入 `research`
- 先读本地知识和缓存产物
- 先产出三份核心文档
- 必须在 `super-dev review docs` 之后再继续后续阶段

## 最小检查项

1. 触发词是否与当前宿主一致
2. 首次响应是否明确声明当前阶段是 `research`
3. 是否明确承诺三文档后暂停等待确认
4. 是否在文档确认后才进入 Spec / coding
5. 是否在质量返工后要求重新执行 review 与 release 验证

## 推荐命令

```bash
super-dev integrate audit --auto
super-dev integrate smoke
super-dev review docs --status confirmed --comment "runtime validation passed"
```

## 产物

建议保留以下运行时证据：

- `output/*-host-surface-audit.md`
- `output/*-host-surface-audit.json`
- `.super-dev/review-state/host-runtime-validation.json`

如果没有这些证据，说明 host runtime validation 仍然不完整。
