# Super Dev 集成指南

## 目录

- [核心概念](#核心概念)
- [支持的 AI 工具](#支持的-ai-工具)
- [集成方式详解](#集成方式详解)
- [各平台配置指南](#各平台配置指南)
- [最佳实践](#最佳实践)

---

## 核心概念

### Super Dev 的定位

**Super Dev** 是一个**通用的 AI 辅助开发工具**，不是特定平台的插件。它的工作原理是：

```
用户需求 → Super Dev CLI → 生成文档 + AI 提示词 → 复制到任何 AI 工具 → 代码实现
```

### 核心能力

| 能力 | 说明 | 通用性 |
|:---|:-----|:---|
| **文档生成** | PRD、架构、UI/UX 设计 | ✅ 通用 Markdown |
| **AI 提示词生成** | 结构化提示词 | ✅ 兼容所有 AI |
| **Spec 管理** | OpenSpec 格式规范 | ✅ 通用格式 |
| **质量检查** | 自动评分和建议 | ✅ 通用标准 |
| **配置生成** | CI/CD、数据库迁移 | ✅ 配置文件 |

### 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  第 1 步: 使用 Super Dev CLI 生成项目资产                   │
│                                                             │
│  $ super-dev pipeline "用户认证系统" \                      │
│    --platform web --frontend react --backend node           │
│                                                             │
│  生成:                                                      │
│  - PRD 文档 (项目需求文档)                                   │
│  - 架构文档 (技术设计)                                       │
│  - UI/UX 文档 (界面设计)                                     │
│  - AI 提示词 (结构化提示词)                                  │
│  - Spec 规范 (OpenSpec 格式)                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第 2 步: 复制 AI 提示词到你使用的 AI 工具                   │
│                                                             │
│  可选工具:                                                   │
│  - Claude Code / Cursor / Windsurf / Continue              │
│  - ChatGPT / GPT-4 / Claude (Web)                          │
│  - Aider / Cursor CLI                                       │
│  - GitHub Copilot / Tabby                                   │
│  - 任何支持文本输入的 AI 工具                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第 3 步: AI 根据详细规范生成代码                            │
│                                                             │
│  AI 生成的代码会:                                            │
│  - 遵循 PRD 中的功能需求                                     │
│  - 实现架构文档中的设计                                      │
│  - 使用 UI/UX 文档中的设计系统                               │
│  - 符合质量门禁的所有标准                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 支持的 AI 工具

### 主流 AI IDE (推荐)

| 工具 | 类型 | 集成方式 | 推荐度 |
|:---|:---|:---|:---|
| **Claude Code** | CLI/IDE | Skill 深度集成 | ⭐⭐⭐⭐⭐ |
| **Cursor** | IDE (VS Code 分支) | 复制提示词 | ⭐⭐⭐⭐⭐ |
| **Windsurf** | IDE (Codeium) | 复制提示词 | ⭐⭐⭐⭐⭐ |
| **Continue** | VS Code 扩展 | 复制提示词 | ⭐⭐⭐⭐ |
| **Tabby** | 开源 IDE | 复制提示词 | ⭐⭐⭐⭐ |

### AI CLI 工具

| 工具 | 类型 | 集成方式 | 推荐度 |
|:---|:---|:---|:---|
| **Aider** | CLI | 配合使用 | ⭐⭐⭐⭐⭐ |
| **OpenAI Codex** | CLI | 配合使用 | ⭐⭐⭐⭐ |
| **GPT-cli** | CLI | 配合使用 | ⭐⭐⭐ |

### Web AI 平台

| 工具 | 集成方式 | 推荐度 |
|:---|:---|:---|
| **ChatGPT / GPT-4** | 复制提示词 | ⭐⭐⭐⭐⭐ |
| **Claude (Web)** | 复制提示词 | ⭐⭐⭐⭐⭐ |
| **DeepSeek** | 复制提示词 | ⭐⭐⭐⭐ |
| **Perplexity** | 复制提示词 | ⭐⭐⭐ |

### 代码助手

| 工具 | 集成方式 | 推荐度 |
|:---|:---|:---|
| **GitHub Copilot** | 文档作为上下文 | ⭐⭐⭐⭐ |
| **Codeium** | 文档作为上下文 | ⭐⭐⭐⭐ |
| **Sourcegraph Cody** | 文档作为上下文 | ⭐⭐⭐⭐ |

---

## 集成方式详解

### 方式 1: Claude Code (深度集成)

**特点**: Skill 深度集成，最佳体验

#### 安装

```bash
# 方法 1: 使用多平台安装脚本（默认全部平台）
./install.sh

# 只安装指定平台
./install.sh --targets claude-code,codex-cli,cursor

# 仅生成集成配置，不安装 skill
./install.sh --targets all --no-skill

# 方法 2: 使用 CLI 命令
super-dev integrate setup --target claude-code --force
super-dev skill install super-dev --target claude-code --name super-dev-core --force
```

#### 使用

```bash
# 直接在 Claude Code 中调用
"使用 Super Dev 分析这个项目"

# 或调用特定专家
"调用 Super Dev 的 PM 专家帮我看这个需求"
"调用 Super Dev 的架构师审查这个设计"
```

**优势**:
- ✅ 无缝集成，无需复制粘贴
- ✅ 支持 10 位专家系统
- ✅ 实时市场情报
- ✅ 自动化工作流

---

### 方式 2: Cursor (推荐)

**特点**: 最流行的 AI IDE，支持 Claude 3.5 Sonnet

#### 配置

1. **创建 Cursor 配置文件**:

```bash
# 创建 .cursorrules 文件
cat > .cursorrules << 'EOF'
# Super Dev 项目规范

当生成代码时，遵循以下规范：
1. 参考 docs/ 目录下的项目文档
2. 遵循 PRD 中定义的功能需求
3. 实现架构文档中的技术设计
4. 使用 UI/UX 文档中的设计系统
5. 确保代码通过质量门禁标准

文档优先级:
- output/*-prd.md > output/*-architecture.md > output/*-uiux.md
EOF
```

2. **使用 Super Dev 生成项目**:

```bash
# 生成项目资产
super-dev pipeline "任务管理系统" \
  --platform web \
  --frontend react \
  --backend node

# 查看生成的 AI 提示词
cat output/*-ai-prompt.md
```

3. **在 Cursor 中实现**:

```bash
# 方法 A: 使用 Composer (Cmd+I / Ctrl+I)
1. 复制 AI 提示词内容
2. 在 Cursor 中按 Cmd+I 打开 Composer
3. 粘贴提示词
4. 点击 "Generate" 生成代码

# 方法 B: 使用 Chat (Cmd+L / Ctrl+L)
1. 复制 PRD + 架构文档内容
2. 在 Cursor Chat 中粘贴
3. 告诉 Claude: "根据这些文档生成代码"

# 方法 C: 使用 .cursorrules
1. 确保 .cursorrules 文件存在
2. 直接在 Composer 中说: "实现 PRD 中的所有功能"
3. Cursor 会自动读取 .cursorrules 规范
```

**优势**:
- ✅ 支持 Claude 3.5 Sonnet (最强大的代码模型)
- ✅ Composer 多文件编辑
- ✅ 代码库级别理解
- ✅ 实时代码预览

---

### 方式 3: Windsurf (Codeium)

**特点**: 免费且强大的 AI IDE

#### 配置

```bash
# 1. 生成项目资产
super-dev pipeline "电商系统" \
  --platform web \
  --frontend vue \
  --backend python

# 2. 创建 Windsurf 配置
cat > .windsurfrules << 'EOF'
# Super Dev 规范

项目文档位于 docs/ 和 output/ 目录
遵循 PRD、架构、UI/UX 文档中的所有规范
EOF

# 3. 在 Windsurf 中使用
# 打开 Windsurf → AI Chat → 粘贴 AI 提示词
```

**优势**:
- ✅ 完全免费
- ✅ 支持 Claude 和 GPT-4
- ✅ 优秀的代码补全
- ✅ 内置代码解释

---

### 方式 4: Continue

**特点**: VS Code 开源 AI 扩展

#### 安装

```bash
# 在 VS Code 中安装 Continue 扩展
code --install-extension Continue.continue
```

#### 配置

```json
// ~/.continue/config.json
{
  "contextProviders": {
    "Super Dev Docs": {
      "description": "Super Dev 生成的项目文档",
      "handler": async (context) => {
        const fs = require('fs');
        const prd = fs.readFileSync('output/*-prd.md', 'utf8');
        const arch = fs.readFileSync('output/*-architecture.md', 'utf8');
        const uiux = fs.readFileSync('output/*-uiux.md', 'utf8');
        return prd + "\n\n" + arch + "\n\n" + uiux;
      }
    }
  }
}
```

#### 使用

```bash
# 生成项目
super-dev pipeline "博客系统" --platform web

# 在 VS Code Continue 中
# 按 Cmd+Shift+L 打开 Continue Chat
# 输入: "使用 Super Dev 文档生成代码"
```

---

### 方式 5: ChatGPT / GPT-4 (Web)

**特点**: 最广泛的 AI 平台

#### 使用

```bash
# 1. 生成项目资产
super-dev pipeline "社交应用" \
  --platform mobile \
  --frontend react-native \
  --backend node

# 2. 打开 AI 提示词文件
cat output/*-ai-prompt.md

# 3. 复制全部内容到剪贴板
cat output/*-ai-prompt.md | pbcopy  # macOS
cat output/*-ai-prompt.md | xclip  # Linux

# 4. 粘贴到 ChatGPT/GPT-4 对话框
# 5. AI 会根据详细规范生成代码
```

**技巧**:
```markdown
# 最佳提示词结构

上下文:
- 我使用 Super Dev 生成了项目文档
- 项目名称: [从 PRD 中复制]
- 技术栈: [从架构文档中复制]

任务:
请实现以下功能（基于 PRD）:
1. [功能 1]
2. [功能 2]

约束条件:
- 必须遵循架构文档中的设计
- 必须使用 UI/UX 文档中的设计系统
- 必须达到质量门禁的标准

参考文档:
[粘贴 PRD 关键部分]
[粘贴架构关键部分]
[粘贴 UI/UX 关键部分]
```

---

### 方式 6: Aider (CLI 工具)

**特点**: 命令行 AI 编程助手

#### 工作流

```bash
# 1. 使用 Super Dev 生成项目
super-dev pipeline "API 服务" \
  --platform web \
  --backend python

# 2. 初始化 Git 仓库
git init
git add .

# 3. 启动 Aider
aider --model gpt-4

# 4. 在 Aider 中
# 复制 AI 提示词内容
# 粘贴到 Aider 对话框
# Aider 会自动修改代码

# 示例对话
You: 实现用户认证功能，参考 output/api服务-prd.md
Aider: [分析文档并生成代码]
```

**优势**:
- ✅ 纯命令行，适合远程服务器
- ✅ 自动 Git 提交
- ✅ 支持多文件编辑
- ✅ 代码审查模式

---

### 方式 7: GitHub Copilot

**特点**: GitHub 官方 AI 助手

#### 配置

```bash
# 1. 生成项目文档
super-dev pipeline "企业官网" \
  --platform web \
  --frontend react

# 2. 将文档放在项目根目录
mkdir -p .github
cp output/*-prd.md .github/PRD.md
cp output/*-architecture.md .github/ARCHITECTURE.md
cp output/*-uiux.md .github/UIUX.md

# 3. 在 VS Code 中使用 Copilot
# Copilot 会自动读取这些文档作为上下文
```

#### 使用技巧

```javascript
// 在代码中添加注释引导 Copilot
// TODO: 实现 PRD 第 3.2 节的用户登录功能
// 参考 .github/PRD.md 中的需求描述

function handleLogin() {
  // Copilot 会根据 PRD 内容自动补全
}
```

---

## 各平台配置指南

### Cursor 最佳配置

#### 1. 创建 .cursorrules

```bash
cat > .cursorrules << 'EOF'
# Super Dev Cursor 规范

## 项目上下文
- 文档位置: docs/ 和 output/ 目录
- PRD: output/*-prd.md
- 架构: output/*-architecture.md
- UI/UX: output/*-uiux.md

## 编码规范

### 功能实现
- 必须实现 PRD 中定义的所有功能需求
- 遵循架构文档中的技术设计
- 使用 UI/UX 文档中的设计系统

### 代码质量
- 遵循红队审查报告中的安全建议
- 达到质量门禁的所有标准
- 修复所有高危和中危问题

### 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖关键路径
- 使用项目选定的测试框架

### 提交规范
- 遵循 Conventional Commits
- 每次 commit 应该是完整的功能单元
- Commit message 引用相关需求 ID

## 优先级
1. 安全 > 性能 > 可维护性
2. 文档中的明确要求 > 一般最佳实践
3. 项目特定规范 > 通用编码规范
EOF
```

#### 2. 配置 Composer

在 Cursor Composer 中使用以下提示词模板：

```markdown
# Super Dev 项目实现

## 项目信息
- 名称: {从 PRD 复制}
- 技术栈: {从架构文档复制}

## 任务
请根据以下文档实现完整功能：

1. **功能需求** (来自 PRD):
{粘贴 PRD 关键部分}

2. **技术设计** (来自架构文档):
{粘贴架构关键部分}

3. **设计系统** (来自 UI/UX 文档):
{粘贴 UI/UX 关键部分}

## 约束条件
- 必须修复红队审查中的所有高危问题
- 必须达到当前场景的质量门禁阈值（可由 `--quality-threshold` 覆盖）
- 必须包含单元测试和集成测试
- 必须遵循项目代码规范

## 输出要求
- 完整的可运行代码
- 详细的代码注释
- 测试用例
- 部署说明
```

---

### Windsurf 最佳配置

#### 1. 创建 .windsurfrules

```bash
cat > .windsurfrules << 'EOF'
# Super Dev Windsurf 规范

项目文档位于:
- PRD: output/*-prd.md
- 架构: output/*-architecture.md
- UI/UX: output/*-uiux.md
- Spec: .super-dev/specs/

实现代码时:
1. 严格遵循 PRD 中的功能需求
2. 实现架构文档中的技术设计
3. 使用 UI/UX 文档中的设计系统
4. 达到质量门禁的所有标准

不遵守:
- 添加 PRD 中未明确的功能
- 修改架构文档中的核心技术决策
- 使用 UI/UX 文档外的设计风格
EOF
```

#### 2. 使用 AI Chat

```markdown
# 在 Windsurf AI Chat 中

步骤 1: 告诉 AI 上下文
"我使用 Super Dev 生成了项目文档，文档在 output/ 目录"

步骤 2: 描述任务
"请根据 PRD 和架构文档实现用户认证模块"

步骤 3: 提供详细说明
"具体要求:
- 实现 JWT 认证
- 支持邮箱登录
- 支持 OAuth2 第三方登录
- 参考 output/*-architecture.md 第 5 节"

步骤 4: 生成并审查
Windsurf 会生成代码，审查后确认或要求修改
```

---

### Continue 最佳配置

#### 1. 配置 config.json

```json
{
  "useDocuments": true,
  "docsToInclude": [
    "output/*-prd.md",
    "output/*-architecture.md",
    "output/*-uiux.md"
  ],
  "slashCommands": [
    {
      "name": "super-dev",
      "description": "使用 Super Dev 文档生成代码",
      "prompt": "请根据 output/ 目录中的 Super Dev 文档生成代码。严格遵循 PRD、架构和 UI/UX 文档中的所有规范。"
    }
  ]
}
```

#### 2. 使用自定义命令

```bash
# 在 VS Code Continue Chat 中
# 输入 /super-dev
# Continue 会自动加载所有 Super Dev 文档作为上下文
```

---

## 最佳实践

### 1. 文档管理

```bash
# 推荐的项目结构
project/
├── docs/                          # Super Dev 文档
│   ├── WORKFLOW_GUIDE.md          # 工作流指南
│   └── INTEGRATION_GUIDE.md       # 集成指南
├── output/                        # 生成的项目资产
│   ├── 项目名-prd.md
│   ├── 项目名-architecture.md
│   ├── 项目名-uiux.md
│   ├── 项目名-ai-prompt.md        # 核心：AI 提示词
│   └── 项目名-spec.md
├── .super-dev/                    # Super Dev 配置
│   ├── specs/                     # 规范定义
│   └── changes/                   # 变更提案
├── .cursorrules                   # Cursor 规则
├── .windsurfrules                 # Windsurf 规则
└── README.md
```

### 2. 迭代工作流

```bash
# 1-N+1 场景：在现有项目上添加功能

# 步骤 1: 创建变更提案
super-dev spec propose add-payment \
  --title "添加支付功能" \
  --description "集成 Stripe 支付"

# 步骤 2: 添加详细需求
super-dev spec add-req add-payment payment stripe \
  "系统 SHALL 集成 Stripe Payment Intent API"

# 步骤 3: 生成变更文档
super-dev create "添加支付功能" \
  --platform web \
  --domain ecommerce \
  --output output/add-payment

# 步骤 4: 复制新的 AI 提示词到你的 AI 工具
cat output/add-payment/*-ai-prompt.md | pbcopy

# 步骤 5: AI 实现代码

# 步骤 6: 归档变更
super-dev spec archive add-payment
```

### 3. 团队协作

```bash
# 团队成员 1: 产品经理
super-dev expert PM "帮我写一个电商平台的 PRD"

# 团队成员 2: 架构师
super-dev expert ARCHITECT "设计高并发架构"

# 团队成员 3: 开发者（使用 Cursor）
# 复制 AI 提示词到 Cursor
# Cursor 生成代码

# 团队成员 4: QA
super-dev quality --type all

# 团队成员 5: DevOps
super-dev deploy --cicd github
```

### 4. 多 AI 工具组合

```bash
# 最佳组合: Super Dev + Cursor + Aider

# 阶段 1: 文档生成（Super Dev CLI）
super-dev pipeline "用户系统" \
  --platform web \
  --frontend react \
  --backend node

# 阶段 2: 代码生成（Cursor）
# 复制 AI 提示词到 Cursor Composer
# Cursor 生成大部分代码

# 阶段 3: 细节优化（Aider）
aider --model gpt-4
# 在 Aider 中进行细节调整和 bug 修复

# 阶段 4: 质量检查（Super Dev）
super-dev quality --type all
```

### 5. 提示词优化技巧

```markdown
# ✅ 好的提示词（结构化）

上下文:
项目: 电商平台
技术栈: React + Node.js + PostgreSQL
文档: 已使用 Super Dev 生成

任务:
实现购物车功能，具体要求：
1. 添加商品到购物车
2. 修改商品数量
3. 删除商品
4. 计算总价

约束条件:
- 遵循 output/ecommerce-prd.md 第 4 节
- 实现架构文档中的 REST API 设计
- 使用 UI/UX 文档中的组件库
- 处理所有错误情况
- 添加单元测试（覆盖率 > 80%）

参考文档:
[粘贴 PRD 相关部分]
[粘贴架构相关部分]

# ❌ 差的提示词（模糊）

"帮我写一个购物车"
```

---

## 常见问题

### Q1: Super Dev 支持哪些 AI 模型？

**A**: Super Dev 本身是模型无关的，生成的提示词可用于任何 AI 模型：
- **Claude 3.5 Sonnet** (推荐，代码能力强)
- **GPT-4 / GPT-4 Turbo**
- **Claude 3 Opus**
- **DeepSeek V3**
- 其他支持长上下文的模型

### Q2: 哪个 AI IDE 最适合与 Super Dev 配合使用？

**A**: 根据场景选择：

| 场景 | 推荐工具 | 原因 |
|:---|:---|:---|
| **最佳体验** | Cursor | Claude 3.5 + Composer |
| **免费使用** | Windsurf | 完全免费，功能强大 |
| **深度集成** | Claude Code | Super Dev Skill 原生支持 |
| **VS Code 用户** | Continue | 轻量级扩展 |
| **命令行爱好者** | Aider | 纯 CLI，自动化 |
| **Web 用户** | ChatGPT/Claude | 最广泛支持 |

### Q3: 生成的文档可以用在多个 AI 工具中吗？

**A**: 可以！文档是通用的 Markdown 格式：
```bash
# 同一份文档可用于不同工具

# Cursor
cat output/*-ai-prompt.md | pbcopy
# 粘贴到 Cursor Composer

# ChatGPT
cat output/*-ai-prompt.md | pbcopy
# 粘贴到 ChatGPT

# Aider
aider --prompt "$(cat output/*-ai-prompt.md)"
```

### Q4: 如何在团队中推广使用？

**A**: 建议的推广策略：
```bash
# 1. 创建团队模板
git init team-templates
cd team-templates
super-dev init team-standard

# 2. 生成示例项目
super-dev pipeline "示例项目" \
  --platform web \
  --frontend react

# 3. 编写团队使用指南
cat > docs/TEAM_GUIDE.md << 'EOF'
# 团队使用 Super Dev 规范

## 必须使用 Super Dev 的场景
- 新功能开发
- 架构变更
- 重大重构

## 工作流程
1. 使用 Super Dev 生成文档
2. 团队评审文档
3. 使用 Cursor 实现代码
4. 代码审查
5. 归档变更
EOF

# 4. 培训团队成员
# 组织一次团队培训，演示完整流程
```

### Q5: 可以和现有的 CI/CD 集成吗？

**A**: 可以！Super Dev 生成的 CI/CD 配置支持所有主流平台：
```bash
# GitHub Actions
super-dev deploy --cicd github

# GitLab CI
super-dev deploy --cicd gitlab

# Jenkins
super-dev deploy --cicd jenkins
```

---

## 快速参考

### 常用命令

```bash
# 生成项目（0-1）
super-dev pipeline "描述" [选项]

# 添加功能（1-N+1）
super-dev spec propose <id>
super-dev spec add-req <id> ...
super-dev create "描述"

# 质量检查
super-dev quality --type all

# 部署配置
super-dev deploy --cicd github

# 分析项目
super-dev analyze
```

### AI 工具速查

| 工具 | 安装 | 配置文件 | 快捷键 |
|:---|:---|:---|:---|
| **Cursor** | cursor.com | `.cursorrules` | Cmd+I (Composer) |
| **Windsurf** | codeium.com/windsurf | `.windsurfrules` | Cmd+L (AI Chat) |
| **Continue** | continue.dev | `config.json` | Cmd+Shift+L |
| **Aider** | pip install aider | 无 | 直接命令行 |
| **Claude Code** | claude.ai/code | `.claude/` | /super-dev |

### 提示词模板

```markdown
# 标准提示词模板

## 上下文
- 项目名称: {name}
- 技术栈: {stack}
- 文档位置: output/

## 任务
{具体任务描述}

## 参考文档
{粘贴相关文档部分}

## 约束条件
- 遵循 PRD: {prd-reference}
- 实现架构: {arch-reference}
- 使用设计: {uiux-reference}
- 达到质量标准: 满足当前质量门禁阈值
```

---

**需要帮助？**
- GitHub: https://github.com/shangyankeji/super-dev
- Issues: https://github.com/shangyankeji/super-dev/issues
- Email: 11964948@qq.com
