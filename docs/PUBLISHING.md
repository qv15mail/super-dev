# 发布指南（2.0.2）

> 面向 Super Dev 2.x 的标准发布流程。

## 1. 发布前检查

1. 更新版本号（`pyproject.toml` 与 `super_dev/__init__.py`）。
2. 更新 `CHANGELOG.md`。
3. 确认 CI 与本地均可通过。

执行强制预检：

```bash
./scripts/preflight.sh
```

预检覆盖：

- `ruff check super_dev tests`
- `mypy super_dev`
- `pytest -q`
- `python3 scripts/check_delivery_ready.py --smoke`
- `bandit -ll -r super_dev`
- `pip-audit .`
- `python3 tests/benchmark.py`
- `python3 -m build`
- `twine check dist/*`

## 2. 构建与发布

```bash
export PYPI_API_TOKEN="<your-token>"
./scripts/publish.sh --repository pypi --yes
```

`publish.sh` 会执行：

- 预检（默认执行，可用 `--skip-preflight` 跳过）
- 构建与 `twine check`
- 使用 `__token__ + PYPI_API_TOKEN` 非交互上传 PyPI

## 3. Git Tag 与 Release

```bash
git tag v2.0.2
git push origin v2.0.2
```

然后在 GitHub 创建 Release，关联本次变更说明。

注意：Tag 触发的 CD 会强制检查 `PYPI_API_TOKEN`，未配置时发布作业会失败。

## 4. 发布后验证

```bash
pip install --no-cache-dir super-dev==2.0.2
super-dev --help
super-dev "构建一个包含登录和订单的系统"
```

## 5. 回滚/应急策略

PyPI 不支持删除已发布版本，建议：

1. 对有问题版本执行 `yank`。
2. 发布补丁版本（如 `2.0.2`）。
3. 在 `CHANGELOG.md` 和 GitHub Release 明确影响范围与修复建议。

参考：[`docs/RELEASE_RUNBOOK.md`](./RELEASE_RUNBOOK.md)
