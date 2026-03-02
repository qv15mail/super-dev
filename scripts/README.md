# Scripts 目录

## 可用脚本

### `preflight.sh`

发布前非交互质量门禁脚本（推荐先跑）。

```bash
./scripts/preflight.sh
```

可选参数：

```bash
./scripts/preflight.sh --allow-dirty --skip-package --skip-benchmark --skip-delivery-smoke
```

### `check_delivery_ready.py`

交付门禁检查脚本（支持直接检查 manifest 或 smoke 全链路验证）。

```bash
# 检查当前项目最新 manifest
python3 scripts/check_delivery_ready.py --project-dir .

# 运行离线 smoke，验证 pipeline 到交付包端到端
python3 scripts/check_delivery_ready.py --smoke --project-dir .
```

### `publish.sh`

交互式发布脚本（适合手动发布流程）。

```bash
./scripts/publish.sh
```

### `release.sh`

历史发布脚本（包含 changelog/tag/upload 等步骤）。

```bash
./scripts/release.sh
```

## 推荐顺序（2.0.0）

1. `./scripts/preflight.sh`
2. `python3 -m build && twine check dist/*`
3. `twine upload dist/*`
4. `git tag v2.0.0 && git push origin v2.0.0`
