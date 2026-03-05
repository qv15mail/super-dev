# Scripts 目录

## 可用脚本

### `../install.sh`

宿主安装向导（默认交互式，多选 CLI/IDE 宿主）。

```bash
# 交互式向导
./install.sh

# 非交互（全部宿主）
./install.sh --targets all

# 非交互（仅规则，不装 skill）
./install.sh --targets all --no-skill
```

### `preflight.sh`

发布前非交互质量门禁脚本（推荐先跑）。

```bash
./scripts/preflight.sh
```

可选参数：

```bash
./scripts/preflight.sh --allow-dirty --skip-package --skip-benchmark --skip-delivery-smoke --skip-host-compat-gate
```

### `check_delivery_ready.py`

交付门禁检查脚本（支持直接检查 manifest 或 smoke 全链路验证）。

```bash
# 检查当前项目最新 manifest
python3 scripts/check_delivery_ready.py --project-dir .

# 运行离线 smoke，验证 pipeline 到交付包端到端
python3 scripts/check_delivery_ready.py --smoke --project-dir .
```

### `check_host_compatibility.py`

宿主兼容性门禁脚本（读取 `output/*-host-compatibility.json` 并执行阈值校验）。

```bash
# 默认读取 super-dev.yaml（host_compatibility_min_score / host_compatibility_min_ready_hosts），无配置时使用 80/1
python3 scripts/check_host_compatibility.py --project-dir .

# 自定义阈值和 ready host 最低数量
python3 scripts/check_host_compatibility.py --project-dir . --min-score 85 --min-ready-hosts 1
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

## 推荐顺序（2.0.2）

1. `./scripts/preflight.sh`
2. `python3 -m build && twine check dist/*`
3. `twine upload dist/*`
4. `git tag v2.0.2 && git push origin v2.0.2`
