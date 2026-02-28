# Super Dev

<div align="center">


# 顶级 AI 开发战队
### God-Tier AI Development Team

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-black-2024%20informational)](https://github.com/psf/black)
[![Type Checks](https://img.shields.io/badge/type%20checks-mypy-success)](https://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/tests-59%20passing-brightgreen)](tests/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-success)](.github/workflows/ci.yml)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://code.claude.com)

[English](README_EN.md) | 简体中文

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [AI 工具集成](#-ai-工具集成) • [完整教程](#-完整教程) • [命令参考](#-命令参考) • [文档](#-文档) • [示例](#-示例)

</div>

---

## 什么是 Super Dev?

**Super Dev** 是一个商业级 AI 辅助开发工具，专注于 **规范驱动开发 (SDD)**。它从一句话需求出发，自动生成完整的项目文档、规范说明，直至 CI/CD 配置和数据库迁移脚本。

```
想法 → 文档 → 规范 → 审查 → AI 实现 → 部署
```

### 双重架构

**Super Dev** 采用 **CLI 工具 + Agent Skills** 的双重架构：

| 形态 | 用途 | 触发方式 |
|:---|:---|:---|
| **CLI 工具** | 生成 PRD、架构、UI/UX 文档 | 终端执行 `super-dev` |
| **Agent Skills** | 增强 Claude Code 的开发能力 | 自动调用或手动触发 |

**Agent Skills 工作原理**：
- 当你在 Claude Code 中描述相关任务时，Claude 会自动检测并加载 Super Dev Skill
- 例如："帮我设计一个电商平台的架构" → 自动激活架构师专家
- 例如："帮我评审这段代码的安全性" → 自动激活安全专家

### 核心价值

| 能力 | 说明 |
|:---|:-----|
| **双重架构** | CLI 工具 + Claude Code Agent Skills，灵活适配不同工作流 |
| **规范驱动开发** | 类似 OpenSpec 的工作流，在编码前达成规范共识 |
| **需求增强 + 11 阶段流水线（含第 0 阶段）** | 需求增强 → 文档 → 前端骨架 → Spec → 实现骨架 → 红队审查 → 质量门禁 → 代码审查 → AI 提示 → CI/CD → 数据库迁移 |
| **10 位专家系统** | PM/架构/UI/UX/安全/代码/DBA/QA/DevOps/RCA 协作 |
| **设计智能引擎** | 企业级设计能力：100+ UI 风格、150+ 配色、80+ 字体组合、BM25+ 语义搜索 |
| **知识库注入** | 6 个业务领域 + 4 个平台的专业知识自动注入 |
| **质量门禁** | 场景化质量门禁：1-N+1 默认 80 分，0-1 自动放宽（可通过 `--quality-threshold` 覆盖） |
| **开箱即用** | CLI 工具，一键生成完整项目资产 |

---

## 功能特性

### 1. 完整开发流水线

Super Dev 提供从想法到部署的 11 阶段自动化流水线（含第 0 阶段）：

```
┌──────────────────────────────────────────────────────────────┐
│                    Super Dev 完整流水线                       │
├──────────────────────────────────────────────────────────────┤
│  第 0 阶段  │  需求增强 (联网检索 + 本地知识库)               │
│  第 1 阶段  │  生成专业文档 (PRD + 架构 + UI/UX)              │
│  第 2 阶段  │  前端可演示骨架 (先前端后系统)                   │
│  第 3 阶段  │  创建 Spec 规范 (OpenSpec 风格)                  │
│  第 4 阶段  │  前后端实现骨架 (代码目录 + API 契约)            │
│  第 5 阶段  │  红队审查 (安全 + 性能 + 架构)                   │
│  第 6 阶段  │  质量门禁 (场景化阈值，支持自定义覆盖)            │
│  第 7 阶段  │  代码审查指南                                   │
│  第 8 阶段  │  AI 提示词生成                                  │
│  第 9 阶段  │  CI/CD 配置 (5 大平台)                          │
│  第 10 阶段 │  数据库迁移脚本 (6 种 ORM)                      │
└──────────────────────────────────────────────────────────────┘
```

### 2. CLI 工具集

```bash
# ===== 核心命令 =====
super-dev "功能描述"            # 需求直达模式：自动执行完整流水线
super-dev pipeline "功能描述"    # 运行完整 11 阶段流水线（含第 0 阶段）
super-dev create "功能描述"      # 一键创建项目 (文档 + Spec + AI 提示)
super-dev spec <subcommand>      # Spec-Driven Development 管理
super-dev design <subcommand>    # 设计智能引擎
super-dev skill <action>         # Skill 安装/卸载/查看
super-dev integrate <action>     # 多平台集成配置生成

# ===== 设计智能 =====
super-dev design search "glass"       # 搜索设计资产
super-dev design generate --product SaaS --industry Fintech  # 生成完整设计系统
super-dev design tokens --primary #3B82F6  # 生成 design tokens

# ===== 项目管理 =====
super-dev init <name>            # 初始化新项目
super-dev analyze [path]         # 分析现有项目结构
super-dev config <cmd>           # 配置管理

# ===== 专家系统 =====
super-dev expert --list          # 列出所有可用专家
super-dev expert PM "提示词"     # 调用产品经理专家
super-dev expert ARCHITECT       # 调用架构师专家

# ===== 质量与部署 =====
super-dev quality --type all     # 运行质量检查
super-dev deploy --cicd github   # 生成 CI/CD 配置
super-dev preview -o output.html # 生成 UI 原型

# ===== 工作流 =====
super-dev workflow               # 运行交互式工作流
super-dev studio --port 8765    # 启动 Web 工作台
```

### 3. Spec-Driven Development (SDD)

Super Dev 内置了类似 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 的规范驱动开发工作流：

```
┌────────────────────┐
│ Draft Change       │
│ Proposal           │
└────────┬───────────┘
         │ share intent with your AI
         ▼
┌────────────────────┐
│ Review & Align     │
│ (edit specs/tasks) │◀──── feedback loop ──────┐
└────────┬───────────┘                          │
         │ approved plan                        │
         ▼                                      │
┌────────────────────┐                          │
│ Implement Tasks    │──────────────────────────┘
│ (AI writes code)   │
└────────┬───────────┘
         │ ship the change
         ▼
┌────────────────────┐
│ Archive & Update   │
│ Specs (source)     │
└────────────────────┘
```

**目录结构：**
```
.super-dev/
├── specs/          # 当前规范 (单一事实源)
│   └── auth/
│       └── spec.md
├── changes/        # 提议的变更
│   └── add-2fa/
│       ├── proposal.md
│       ├── tasks.md
│       ├── design.md
│       └── specs/
│           └── auth/
│               └── spec.md  # Delta (ADDED/MODIFIED/REMOVED)
└── archive/        # 已归档的变更
```

### 4. 专家团队

| 专家 | 专长 | 适用场景 |
|:---|:-----|:---------|
| **PM** | 需求分析、PRD 编写、用户故事 | 产品规划、功能定义 |
| **ARCHITECT** | 系统设计、技术选型、架构文档 | 架构设计、技术决策 |
| **UI** | 视觉设计、设计规范、组件库 | 界面设计、视觉规范 |
| **UX** | 交互设计、用户体验、信息架构 | 交互流程、用户体验 |
| **SECURITY** | 安全审查、漏洞检测、威胁建模 | 安全审查、渗透测试 |
| **CODE** | 代码实现、最佳实践、代码审查 | 代码实现、代码审查 |
| **DBA** | 数据库设计、SQL 优化、数据建模 | 数据库设计、性能优化 |
| **QA** | 质量保证、测试策略、自动化测试 | 测试计划、质量保证 |
| **DEVOPS** | 部署、CI/CD、容器化、监控 | 部署配置、流水线 |
| **RCA** | 根因分析、故障复盘、改进建议 | 故障分析、复盘总结 |

### 5. 知识库

#### 业务领域
- **金融科技** (fintech) - 支付、借贷、理财、保险
- **电子商务** (ecommerce) - B2C/B2B/C2C、跨境、社交电商
- **医疗健康** (medical) - 医疗信息化、健康管理
- **社交媒体** (social) - Feed 流、即时通讯、内容审核
- **物联网** (iot) - 设备管理、MQTT/CoAP、边缘计算
- **在线教育** (education) - 直播课堂、题库系统、学习分析
- **认证授权** (auth) - JWT、OAuth2、RBAC
- **内容管理** (content) - CMS、内容推荐、搜索

#### 技术平台
- **Web** - React/Vue/Angular + Node/Python/Go
- **Mobile** - React Native/Flutter
- **WeChat** - 微信小程序
- **Desktop** - Electron/Tauri

### 6. 支持的技术栈

#### 前端框架
- React, Vue, Angular, Svelte

#### 后端框架
- Node.js, Python, Go, Java

#### 数据库 ORM
- Prisma, TypeORM, Sequelize, SQLAlchemy, Django, Mongoose

#### CI/CD 平台
- GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket Pipelines

### 7. 设计智能引擎

Super Dev 内置强大的设计智能引擎，提供从设计搜索到完整设计系统生成的端到端能力：

#### 核心能力

| 能力 | 说明 |
|:---|:-----|
| **BM25+ 语义搜索** | 增强版 BM25 算法，支持字段权重、短语匹配、IDF 平滑、模糊搜索 |
| **多域搜索** | style, color, typography, component, layout, animation, ux, chart, product, stack |
| **美学方向生成** | 26+ 种独特美学方向（cyberpunk, brutalist_minimal, vaporwave, etc.） |
| **Design Tokens** | 自动生成色彩、间距、阴影、圆角等设计令牌 |
| **设计系统生成** | 完整设计系统（CSS 变量、Tailwind 配置、设计文档） |
| **AI 驱动推荐** | 基于产品类型、行业、关键词智能推荐设计系统 |

#### 设计资产库

```
100+ UI 风格    # Glassmorphism, Neumorphism, Brutalism, Bento Grid, etc.
150+ 配色方案   # 预设调色板 + 自动生成单色/类比/互补/三色配色
80+ 字体组合    # Display + Body + Accent + Mono 组合
200+ 组件库     # Button, Input, Card, Navigation, etc.
50+ 布局模式    # Grid, Masonry, Bento, Split Screen, etc.
60+ 动画效果    # Easing, Stagger, Parallax, Morphing, etc.
```

#### 美学方向 (26+ 种)

```
极简方向: brutalist_minimal, japanese_zen, scandinavian, swiss_international
极繁方向: maximalist_chaos, memphis_group, pop_art, vaporwave
复古未来: retro_futurism, cyberpunk, art_deco, steampunk
自然有机: organic_natural, biophilic, earthy, botanical
奢华精致: luxury_refined, french_elegance, italian_sophistication, artisanal
俏皮趣味: playful_toy, kawaii, whimsical, neon_pop
编辑杂志: editorial_magazine, typography_centric, grid_breaking
原始工业: raw_industrial, utilitarian, grunge, post_apocalyptic
柔和梦幻: soft_pastel, dreamy, ethereal, glass_morphism
```

#### 使用示例

```bash
# 搜索设计资产（支持多域搜索）
super-dev design search "glass" --domain style -n 5
super-dev design search "blue" --domain color -n 10
super-dev design search "minimal" --domain layout -n 3

# 生成完整设计系统
super-dev design generate \
  --product SaaS \
  --industry Fintech \
  --keywords "professional,trust,secure" \
  --platform web

# 生成 design tokens
super-dev design tokens \
  --primary #3B82F6 \
  --type monochromatic \
  --format css
```

#### 输出示例

**设计系统生成** (CSS 变量):
```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-secondary: #1E40AF;
  --color-accent: #F59E0B;
  --color-background: #FFFFFF;
  --color-surface: #F9FAFB;
  --color-text: #111827;
  --color-text-secondary: #6B7280;

  /* Typography */
  --font-display: 'Space Grotesk';
  --font-body: 'Plus Jakarta Sans';

  /* Spacing (8pt grid) */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}
```

**Tailwind 配置**:
```json
{
  "theme": {
    "extend": {
      "colors": {
        "primary": "#3B82F6",
        "secondary": "#1E40AF",
        "accent": "#F59E0B"
      },
      "fontFamily": {
        "display": ["Space Grotesk", "sans-serif"],
        "body": ["Plus Jakarta Sans", "sans-serif"]
      }
    }
  }
}
```

---

## 快速开始

> 🚀 **5 分钟上手！** 查看 [**详细快速开始指南**](docs/QUICKSTART.md) | 🎯 **不知道选什么？** 从 [从 0 到 1](#从-0-到-1全新项目) 开始

### 选择你的使用场景

| 场景 | 说明 | 适合你吗？ |
|:---|:---|:---|
| **从 0 到 1** | 全新项目，从想法到完整代码 | ✅ 新产品/新功能<br/>✅ 学习 Super Dev<br/>✅ 完整体验 |
| **从 1 到 N+1** | 现有项目，添加新功能 | ✅ 维护现有项目<br/>✅ 功能扩展<br/>✅ 团队协作 |

**👆 不确定？从 0 到 1 开始！**

### 安装（3 步完成）

**方式 1：从 GitHub 安装（最简单）** ⭐

```bash
# 1. 安装 Super Dev（一条命令搞定！）
pip install git+https://github.com/shangyankeji/super-dev.git

# 2. 验证安装
super-dev --version

# 3. 完成！
```

**方式 2：从源码安装（开发模式）**

```bash
# 1. 克隆仓库
git clone https://github.com/shangyankeji/super-dev.git
cd super-dev

# 2. 安装
pip install -e .

# 3. 验证安装
super-dev --version
```

**方式 3：使用 uv（更快，如果已发布到 PyPI）** ⚡

```bash
# 1. 安装 Super Dev（快 10-100 倍！）
uv pip install super-dev

# 2. 验证安装
super-dev --version

# 3. 完成！
```

**预期输出**：
```
Super Dev v1.0.1
```

> 💡 **提示**：推荐使用**方式 1**（从 GitHub 安装），最简单！如果你想要更快，可以用 `uv pip install` 替代 `pip install`。

### 核心使用：从想法到部署

---

#### 🌱 从 0 到 1（全新项目）

**适用场景**：新产品、新功能、独立项目

**步骤 1：生成项目文档**

```bash
super-dev create "用户认证系统" \
  --platform web \
  --frontend react \
  --backend node
```

**步骤 2：在 Claude Code 中实现**

打开 Claude Code，说：

```
我使用 Super Dev 生成了项目文档，在 output/ 目录。
请阅读所有文档并帮我实现代码。
```

**就这么简单！** Claude 会：
- ✅ 分析项目需求（PRD）
- ✅ 设计系统架构
- ✅ 实现 UI 界面
- ✅ 编写后端 API
- ✅ 配置数据库
- ✅ 编写测试

**👉 [查看详细教程](docs/QUICKSTART.md#-场景-1从-0-到-1全新项目)**

---

#### 🔄 从 1 到 N+1（现有项目）

**适用场景**：维护现有项目、功能扩展、团队协作

**步骤 1：进入项目目录**

```bash
cd /path/to/your/existing-project
```

**步骤 2：生成新功能文档**

```bash
super-dev create "添加用户个人资料编辑功能" \
  --platform web \
  --frontend react \
  --backend node
```

**步骤 3：在 Claude Code 中集成**

打开 Claude Code，说：

```
我使用 Super Dev 为现有项目生成了新功能文档，在 output/ 目录。
请阅读现有项目代码和新功能文档，帮我集成这个新功能。
```

**Claude 会**：
- ✅ 分析现有项目结构
- ✅ 理解新功能需求
- ✅ 集成新功能到现有代码
- ✅ 保持代码风格一致
- ✅ 运行测试确保不破坏现有功能

**👉 [查看详细教程](docs/QUICKSTART.md#-场景-2从-1-到-n1现有项目)**

---

### 其他使用方式

#### 完整流水线（11 阶段，含第 0 阶段）

```bash
# 一句话 → 完整项目资产 (11 阶段，含第 0 阶段)
super-dev pipeline "用户认证系统" \
  --platform web \
  --frontend react \
  --backend node \
  --cicd github \
  --quality-threshold 85
```

**自动生成**:
```
output/
├── 用户认证系统-prd.md                    # PRD 文档
├── 用户认证系统-architecture.md          # 架构设计
├── 用户认证系统-uiux.md                  # UI/UX 设计
├── 用户认证系统-redteam.md               # 红队审查报告
├── 用户认证系统-quality-gate.md          # 质量门禁报告
├── 用户认证系统-code-review.md           # 代码审查指南
├── 用户认证系统-ai-prompt.md             # AI 提示词
└── ...
```

#### 分步创建

```bash
# 1. 初始化项目
super-dev init todo-app \
  --platform web \
  --frontend react \
  --backend node

# 2. 编辑配置
vim super-dev.yaml

# 3. 运行工作流
super-dev workflow
```

---

## AI 工具集成

### 🤖 兼容所有主流 AI IDE 和 CLI 工具

**Super Dev** 不是特定平台的插件，而是**通用的 AI 辅助开发工具**。生成的文档和提示词可用于任何 AI 工具。

#### 支持的 AI 工具

**AI IDE** (推荐):
- **Cursor** ⭐⭐⭐⭐⭐ - 最流行的 AI IDE，支持 Claude 3.5 Sonnet
- **Windsurf** ⭐⭐⭐⭐⭐ - Codeium 出品，完全免费
- **Claude Code** ⭐⭐⭐⭐⭐ - Skill 深度集成
- **Continue** ⭐⭐⭐⭐ - VS Code 开源扩展
- **Tabby** ⭐⭐⭐⭐ - 开源自托管 AI IDE

**AI CLI 工具**:
- **Aider** ⭐⭐⭐⭐⭐ - 命令行 AI 编程助手
- **OpenAI Codex** ⭐⭐⭐⭐ - OpenAI CLI
- **GPT-cli** ⭐⭐⭐ - GPT 命令行工具

**Web AI 平台**:
- **ChatGPT / GPT-4** ⭐⭐⭐⭐⭐
- **Claude (Web)** ⭐⭐⭐⭐⭐
- **DeepSeek** ⭐⭐⭐⭐
- **Perplexity** ⭐⭐⭐

**代码助手**:
- **GitHub Copilot** ⭐⭐⭐⭐
- **Codeium** ⭐⭐⭐⭐
- **Sourcegraph Cody** ⭐⭐⭐⭐

#### 使用方式

```bash
# 步骤 1: 使用 Super Dev 生成项目资产
super-dev pipeline "用户认证系统" \
  --platform web \
  --frontend react \
  --backend node

# 步骤 2: 查看生成的 AI 提示词
cat output/*-ai-prompt.md

# 步骤 3: 复制提示词到任何 AI 工具

# Cursor 示例:
# 1. 按 Cmd+I 打开 Composer
# 2. 粘贴提示词
# 3. 点击 Generate

# ChatGPT 示例:
# 1. 打开 chatgpt.com
# 2. 粘贴提示词
# 3. GPT-4 生成代码

# Aider 示例:
# aider --prompt "$(cat output/*-ai-prompt.md)"
```

#### 详细集成指南

**📚 [完整 AI 工具集成指南 →](docs/INTEGRATION_GUIDE.md)**

包含:
- Cursor、Windsurf、Continue 详细配置
- Aider、ChatGPT、Claude Web 使用方法
- `.cursorrules`、`.windsurfrules` 配置模板
- 团队协作最佳实践
- 常见问题解答

---

## 完整教程

### 📚 [Super Dev 工作流完整指南](docs/WORKFLOW_GUIDE.md)

**详细教程包含**:

#### 0-1 场景：从零开始创建项目
- 项目初始化
- 生成完整项目资产（11 阶段流水线，含第 0 阶段）
- 使用 AI 提示词开发
- 质量检查和迭代优化

#### 1-N+1 场景：在现有项目上迭代
- 分析现有项目
- 创建变更提案（Spec-Driven Development）
- 添加详细需求
- 生成变更文档
- AI 辅助实现
- 归档变更

#### 11 阶段流水线详解（含第 0 阶段）
0. 需求增强（联网检索 + 本地知识库）
1. 文档生成 (PRD + 架构 + UI/UX)
2. 前端可演示骨架 (先前端后系统)
3. Spec 创建 (OpenSpec 格式)
4. 前后端实现骨架（代码目录 + API 契约）
5. 红队审查 (安全 + 性能 + 架构)
6. 质量门禁 (场景化阈值，支持自定义)
7. 代码审查指南
8. AI 提示词生成
9. CI/CD 配置
10. 数据库迁移

#### 最佳实践
- 0-1 项目最佳实践
- 1-N+1 项目最佳实践
- 团队协作最佳实践

#### 常见问题解答
- Super Dev 生成代码吗？
- 如何确保 AI 生成的代码质量？
- 可以在现有项目上使用吗？
- 更多...

**[点击查看完整教程 →](docs/WORKFLOW_GUIDE.md)**

---

## 命令参考

### pipeline - 完整流水线

```bash
super-dev pipeline "功能描述" [选项]

选项:
  -p, --platform {web,mobile,wechat,desktop}
                        目标平台 (默认: web)
  -f, --frontend {react,vue,angular,svelte,none}
                        前端框架 (默认: react)
  -b, --backend {node,python,go,java,none}
                        后端框架 (默认: node)
  -d, --domain {fintech,ecommerce,medical,social,iot,education,auth,content}
                        业务领域
  --name NAME           项目名称 (默认根据描述生成)
  --cicd {github,gitlab,jenkins,azure,bitbucket}
                        CI/CD 平台 (默认: github)
  --skip-redteam        跳过红队审查
  --skip-scaffold       跳过前后端实现骨架生成
  --skip-quality-gate   跳过质量门禁检查
  --offline             离线模式（禁用联网检索）
  --quality-threshold N 质量门禁阈值（可选；默认按场景自动判定）

示例:
  super-dev pipeline "电商购物车"
  super-dev pipeline "用户登录" --platform wechat --cicd gitlab
```

### create - 一键创建项目

```bash
super-dev create "功能描述" [选项]

选项:
  -p, --platform       目标平台
  -f, --frontend       前端框架
  -b, --backend        后端框架
  -d, --domain         业务领域
  --name NAME          项目名称
  --skip-docs          跳过文档生成，只创建 Spec
```

### spec - Spec 管理

```bash
# 初始化 SDD 目录结构
super-dev spec init

# 列出所有变更
super-dev spec list

# 显示变更详情
super-dev spec show <change-id>

# 创建变更提案
super-dev spec propose <change-id> --title "标题" --description "描述"

# 添加需求
super-dev spec add-req <change-id> <component> <requirement-id> "需求描述"

# 验证规格格式
super-dev spec validate              # 验证所有变更
super-dev spec validate <change-id>  # 验证单个变更
super-dev spec validate -v           # 显示详细信息

# 交互式仪表板
super-dev spec view                  # 显示所有规范和变更的仪表板

# 归档变更
super-dev spec archive <change-id>
```

### design - 设计智能引擎

```bash
# ===== 搜索设计资产 =====
super-dev design search "查询词" [选项]

选项:
  -d, --domain {style,color,typography,component,layout,animation,ux,chart,product,stack}
                        搜索域 (默认: 自动检测)
  -n, --max-results N   最大结果数 (默认: 5)
  --fuzzy               启用模糊匹配
  --format {table,json,detailed}
                        输出格式 (默认: table)

示例:
  super-dev design search "glass"              # 搜索 glassmorphism 风格
  super-dev design search "blue" --domain color # 搜索蓝色配色
  super-dev design search "minimal" -n 10       # 获取 10 个结果

# ===== 生成完整设计系统 =====
super-dev design generate [选项]

选项:
  --product {SaaS,Mobile,E-commerce,Dashboard,Portfolio,Landing,Blog,Marketplace}
                        产品类型 (必需)
  --industry {Fintech,Healthcare,Education,E-commerce,Social,Media,Travel,RealEstate}
                        行业领域 (必需)
  --keywords KEYWORDS   关键词 (逗号分隔)
  --platform {web,mobile,wechat,desktop}
                        目标平台 (默认: web)
  --aesthetic AESTHETIC 美学方向 (见下方列表)
  -o, --output DIR      输出目录 (默认: ./design-system)

示例:
  super-dev design generate --product SaaS --industry Fintech
  super-dev design generate --product E-commerce --industry Retail --keywords "vibrant,energetic"
  super-dev design generate --product Dashboard --industry Healthcare --aesthetic brutalist_minimal

# ===== 生成 Design Tokens =====
super-dev design tokens [选项]

选项:
  --primary COLOR       主色调 (必需，格式: #RRGGBB)
  --type {monochromatic,analogous,complementary,triadic,split_complementary,tetradic}
                        配色类型 (默认: monochromatic)
  --format {css,json,tailwind}
                        输出格式 (默认: css)
  -o, --output FILE     输出文件 (默认: stdout)

示例:
  super-dev design tokens --primary #3B82F6
  super-dev design tokens --primary #10B981 --type analogous --format tailwind
  super-dev design tokens --primary #FF6B6B --type complementary -o tokens.json

# ===== 美学方向列表 =====
可用美学方向 (26+ 种):

极简方向:
  brutalist_minimal    - 原始极简主义
  japanese_zen         - 日式禅意
  scandinavian         - 北欧风格
  swiss_international  - 瑞士国际主义

极繁方向:
  maximalist_chaos     - 极繁混乱
  memphis_group        - 孟菲斯集团
  pop_art              - 波普艺术
  vaporwave            - 蒸汽波

复古未来:
  retro_futurism       - 复古未来主义
  cyberpunk            - 赛博朋克
  art_deco             - 装饰艺术
  steampunk            - 蒸汽朋克

自然有机:
  organic_natural      - 有机自然
  biophilic            - 亲生物设计
  earthy               - 大土色调
  botanical            - 植物学

奢华精致:
  luxury_refined       - 奢华精致
  french_elegance      - 法式优雅
  italian_sophistication - 意式精致
  artisanal            - 手工艺

俏皮趣味:
  playful_toy          - 俏皮玩具
  kawaii               - 卡哇伊
  whimsical            - 异想天开
  neon_pop             - 霓虹流行

编辑杂志:
  editorial_magazine   - 编辑杂志
  typography_centric   - 排版中心
  grid_breaking        - 打破网格

原始工业:
  raw_industrial       - 原始工业
  utilitarian          - 实用主义
  grunge               - 垃圾摇滚
  post_apocalyptic     - 末日后

柔和梦幻:
  soft_pastel          - 柔和粉彩
  dreamy               - 梦幻
  ethereal             - 空灵
  glass_morphism       - 玻璃态
```

### expert - 调用专家

```bash
# 列出所有可用专家
super-dev expert --list

# 调用特定专家
super-dev expert PM "帮我写一个电商平台的 PRD"
super-dev expert ARCHITECT "设计高并发架构"
super-dev expert SECURITY "审查安全方案"
```

### 其他命令

```bash
# 初始化项目
super-dev init <name> [选项]

# 分析现有项目
super-dev analyze [path] [选项]

# 质量检查
super-dev quality --type {prd,architecture,ui,ux,code,all}

# 生成部署配置
super-dev deploy --docker --cicd {github,gitlab,jenkins,azure,bitbucket}

# 生成 UI 原型
super-dev preview -o output.html

# 运行交互式工作流
super-dev workflow [--phase ...]

# 配置管理
super-dev config {get,set,list} [key] [value]
```

---

## 示例

### 示例 1: 用户认证系统

```bash
super-dev pipeline "用户认证系统" \
  --platform web \
  --frontend react \
  --backend node \
  --cicd github
```

### 示例 2: 电商平台

```bash
super-dev pipeline "电商平台购物车" \
  --platform web \
  --frontend vue \
  --backend python \
  --domain ecommerce \
  --cicd gitlab
```

### 示例 3: 微信小程序

```bash
super-dev create "点餐小程序" \
  --platform wechat \
  --domain auth
```

### 示例 4: Spec-Driven Development

```bash
# 1. 初始化 SDD
super-dev spec init

# 2. 创建变更提案
super-dev spec propose add-user-auth \
  --title "Add User Authentication" \
  --description "Implement JWT-based user authentication"

# 3. 添加需求
super-dev spec add-req add-user-auth auth user-registration \
  "The system SHALL allow user registration with email and password"

# 4. 查看变更
super-dev spec show add-user-auth

# 5. 完成后归档
super-dev spec archive add-user-auth
```

### 示例 5: 设计智能引擎

```bash
# 搜索 Glassmorphism 风格
super-dev design search "glass" --domain style -n 5

# 生成 SaaS Fintech 设计系统
super-dev design generate \
  --product SaaS \
  --industry Fintech \
  --keywords "professional,trust,secure" \
  --platform web

# 生成单色配色 tokens
super-dev design tokens --primary #3B82F6 --type monochromatic

# 生成赛博朋克风格设计系统
super-dev design generate \
  --product Dashboard \
  --industry Gaming \
  --aesthetic cyberpunk \
  -o ./design-system
```

---


## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- **GitHub**: https://github.com/shangyankeji/super-dev
- **Issues**: https://github.com/shangyankeji/super-dev/issues
- **Email**: 11964948@qq.com

---

<div align="center">

**如果这个项目对你有帮助，请给一个 Star！**

Made with passion by [Excellent](https://github.com/shangyankeji)

</div>
