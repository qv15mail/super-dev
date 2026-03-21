# 发布指南（2.0.12）

> 面向 Super Dev 2.x 的标准发布流程。

## 1. 发布前检查

1. 更新版本号（`pyproject.toml` 与 `super_dev/__init__.py`）。
2. 更新 `CHANGELOG.md`。
3. 确认本地预检全部通过。

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
- `uv build` 或 `python3 -m build`
- `uv publish --check-url` 前的产物校验

## 2. 构建与发布

推荐使用 `uv`：

```bash
export UV_PUBLISH_TOKEN="<your-token>"
uv build
uv publish
```

也可使用脚本：

```bash
export PYPI_API_TOKEN="<your-token>"
./scripts/publish.sh --repository pypi --yes
```

`publish.sh` 会执行：

- 预检（默认执行，可用 `--skip-preflight` 跳过）
- 自动优先使用 `uv build + uv publish`
- 未检测到 `uv` 时回退为 `python -m build + twine upload`

## 3. Git Tag 与 Release

```bash
git tag v2.0.12
git push origin v2.0.12
```

然后在 GitHub 创建 Release，关联本次变更说明。
当前仓库采用手动发布策略，不依赖 GitHub Actions 自动发布。

## 4. 发布后验证

```bash
uv tool install super-dev==2.0.12
super-dev --help

# 或 pip
pip install --no-cache-dir super-dev==2.0.12
super-dev --help
super-dev "构建一个包含登录和订单的系统"
```

## 5. 回滚/应急策略

PyPI 不支持删除已发布版本，建议：

1. 对有问题版本执行 `yank`。
2. 发布补丁版本（如 `2.0.12` 的后续补丁）。
3. 在 `CHANGELOG.md` 和 GitHub Release 明确影响范围与修复建议。

参考：[`docs/RELEASE_RUNBOOK.md`](./RELEASE_RUNBOOK.md)
