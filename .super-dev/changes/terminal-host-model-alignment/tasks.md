# Tasks: Terminal Host Model Alignment

## 1. Spec & State
- [x] 1.1 落盘本次变更 proposal 与 tasks
- [x] 1.2 固化终端层 / 宿主层 / 共享状态层边界

## 2. CLI 主路径
- [x] 2.1 修正裸 `super-dev` 路由，不再在主入口自动迁移
- [x] 2.2 移除 `init` 的宿主自动安装副作用
- [x] 2.3 在宿主推荐路径前做 family 级去重

## 3. 宿主迁移与识别
- [x] 3.1 为已接入宿主写入 install manifest
- [x] 3.2 迁移优先使用 manifest，保守回退到 family 级识别
- [x] 3.3 去掉迁移中的无条件 Claude hooks 安装

## 4. 运行验证
- [x] 4.1 修复宿主 runtime validation 的 host-level `updated_at`
- [x] 4.2 在 payload 中拆分 integration status 与 runtime status

## 5. 文档与官网
- [x] 5.1 README / README_EN 收敛到“终端两命令 + 宿主两触发”
- [x] 5.2 官网首页与 Docs 收敛到新的主路径叙事
- [x] 5.3 修复明显版本与 Changelog 漂移

## 6. Quality
- [x] 6.1 补齐和更新受影响测试
- [x] 6.2 执行回归验证并记录结果
