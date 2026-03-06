"""
文档生成器 - 高质量 PRD、架构、UI/UX 文档生成

开发：Excellent（11964948@qq.com）
功能：专家级文档生成
作用：生成专业、细致、完整的项目文档
创建时间：2025-12-30
最后修改：2025-01-04
"""

from datetime import datetime

from .requirement_parser import RequirementParser


class DocumentGenerator:
    """文档生成器 - 生成专家级项目文档"""

    def __init__(
        self,
        name: str,
        description: str,
        platform: str = "web",
        frontend: str = "next",
        backend: str = "node",
        domain: str = "",
        ui_library: str | None = None,
        style_solution: str | None = None,
        state_management: list[str] | None = None,
        testing_frameworks: list[str] | None = None,
        language_preferences: list[str] | None = None,
    ):
        """初始化文档生成器"""
        self.name = name
        self.description = description
        self.platform = platform
        self.frontend = frontend
        self.backend = backend
        self.domain = domain or "general"
        self.ui_library = ui_library
        self.style_solution = style_solution
        self.state_management = state_management or []
        self.testing_frameworks = testing_frameworks or []
        self.language_preferences = self._normalize_language_preferences(language_preferences)
        self.requirement_parser = RequirementParser()

    def _normalize_language_preferences(self, values: list[str] | None) -> list[str]:
        normalized: list[str] = []
        for item in values or []:
            if not isinstance(item, str):
                continue
            token = item.strip().lower()
            if token and token not in normalized:
                normalized.append(token)
        return normalized

    def _display_language_name(self, language: str) -> str:
        mapping = {
            "csharp": "C#",
            "cpp": "C++",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "objective-c": "Objective-C",
            "matlab": "MATLAB",
            "php": "PHP",
            "sql": "SQL",
            "r": "R",
        }
        if language in mapping:
            return mapping[language]
        if language in {"go", "java", "ruby", "scala", "swift", "kotlin", "rust", "dart", "elixir", "lua"}:
            return language.capitalize()
        return language.replace("-", " ").title()

    def _language_preferences_inline(self) -> str:
        if not self.language_preferences:
            return "未指定（默认支持主流语言）"
        return " / ".join(self._display_language_name(item) for item in self.language_preferences)

    def _analyze_project_for_design(self) -> dict:
        """分析项目特征用于设计推荐"""
        # 从描述中提取特征
        description_lower = self.description.lower()

        # 产品类型
        product_type = "general"
        if any(word in description_lower for word in ["dashboard", "仪表盘", "后台", "admin", "workbench", "workspace", "工作台"]):
            product_type = "dashboard"
        elif any(word in description_lower for word in ["landing", "落地页", "营销页", "官网", "官方网站", "official website", "marketing"]):
            product_type = "landing"
        elif any(word in description_lower for word in ["saas", "软件服务", "platform", "平台"]):
            product_type = "saas"
        elif any(word in description_lower for word in ["电商", "商城", "shop", "store", "mall"]):
            product_type = "ecommerce"
        elif any(word in description_lower for word in ["blog", "博客", "内容", "cms"]):
            product_type = "content"

        # 行业
        industry = "general"
        if any(word in description_lower for word in ["医疗", "健康", "health", "medical", "care"]):
            industry = "healthcare"
        elif any(word in description_lower for word in ["金融", "支付", "fintech", "金融科技", "banking"]):
            industry = "fintech"
        elif any(word in description_lower for word in ["教育", "培训", "education", "learning"]):
            industry = "education"
        elif any(word in description_lower for word in ["法律", "法务", "legal", "律师"]):
            industry = "legal"
        elif any(word in description_lower for word in ["政务", "government", "public"]):
            industry = "government"
        elif any(word in description_lower for word in ["美容", "美业", "beauty", "spa", "wellness"]):
            industry = "beauty"

        # 风格倾向
        style = "modern"
        if any(word in description_lower for word in ["极简", "minimal", "简约"]):
            style = "minimal"
        elif any(word in description_lower for word in ["专业", "商务", "business", "professional"]):
            style = "professional"
        elif any(word in description_lower for word in ["活泼", "fun", "playful", "活力"]):
            style = "playful"
        elif any(word in description_lower for word in ["奢华", "luxury", "高端", "premium"]):
            style = "luxury"

        return {
            "product_type": product_type,
            "industry": industry,
            "style": style,
            "domain": self.domain,
            "platform": self.platform,
            "frontend": self.frontend,
        }

    def _extract_tech_keywords(self) -> dict:
        """
        从描述中提取技术栈关键词

        Returns:
            dict: 包含提取的技术关键词分类
        """
        description = self.description
        keywords: dict[str, list[str]] = {
            "ai_frameworks": [],      # AI 框架：LangGraph, LangChain, Transformers 等
            "agent_tools": [],        # Agent 工具：AutoGPT, BabyAGI, CrewAI 等
            "ml_libraries": [],       # ML 库：PyTorch, TensorFlow, scikit-learn 等
            "vector_stores": [],      # 向量数据库：Pinecone, Chroma, Weaviate 等
            "orchestration": [],      # 编排工具：Airflow, Prefect, Dagster 等
            "other_keywords": [],     # 其他技术关键词
        }

        # AI 框架
        ai_frameworks = ["LangGraph", "LangChain", "LlamaIndex", "Haystack", "Semantic Kernel"]
        for framework in ai_frameworks:
            if framework in description:
                keywords["ai_frameworks"].append(framework)

        # Agent 工具
        agent_tools = ["AutoGPT", "BabyAGI", "CrewAI", "AgentOps", "E2B"]
        for tool in agent_tools:
            if tool in description:
                keywords["agent_tools"].append(tool)

        # ML 库
        ml_libraries = ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "XGBoost", "LightGBM"]
        for lib in ml_libraries:
            if lib in description:
                keywords["ml_libraries"].append(lib)

        # 向量数据库
        vector_stores = ["Pinecone", "Chroma", "Weaviate", "Qdrant", "Milvus", "FAISS"]
        for store in vector_stores:
            if store in description:
                keywords["vector_stores"].append(store)

        # 编排工具
        orchestration = ["Airflow", "Prefect", "Dagster", "Argo Workflows", "Temporal"]
        for tool in orchestration:
            if tool in description:
                keywords["orchestration"].append(tool)

        # 提取 Agent 相关关键词
        if "Agent" in description or "agent" in description or "智能体" in description:
            keywords["other_keywords"].append("Multi-Agent System")

        if "RAG" in description or "检索增强" in description:
            keywords["other_keywords"].append("RAG (Retrieval-Augmented Generation)")

        if "LLM" in description or "大语言模型" in description or "GPT" in description:
            keywords["other_keywords"].append("LLM Integration")

        return keywords


    def generate_prd(self) -> str:
        """生成高质量 PRD 文档"""
        return f"""# {self.name} - 产品需求文档 (PRD)

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **版本**: v2.0.5
> **状态**: 草稿

---

## 文档信息

| 项目 | 内容 |
|:---|:---|
| **项目名称** | {self.name} |
| **项目描述** | {self.description} |
| **目标平台** | {self.platform.upper()} |
| **业务领域** | {self.domain.upper()} |
| **语言偏好** | {self._language_preferences_inline()} |

---

## 1. 产品概述

### 1.1 产品愿景

{self._generate_vision()}

### 1.2 目标用户

{self._generate_target_users()}

### 1.3 核心价值

{self._generate_value_proposition()}

### 1.4 市场与对标结论

{self._generate_market_context()}

### 1.5 用户分层与使用场景

{self._generate_user_segment_matrix()}

---

## 2. 功能需求

### 2.1 核心功能 (MVP)

{self._generate_core_features()}

### 2.2 扩展功能 (Phase 2)

{self._generate_extended_features()}

### 2.3 用户故事

{self._generate_user_stories()}

### 2.4 功能优先级与范围边界

{self._generate_scope_priorities()}

### 2.5 边界场景与异常路径

{self._generate_edge_cases()}

---

## 3. 非功能需求

### 3.1 性能要求

- **响应时间**: API 响应时间 < 200ms (P95)
- **并发用户**: 支持 1000+ 并发用户
- **页面加载**: 首屏加载时间 < 2s

### 3.2 安全要求

- **数据加密**: 传输层 TLS 1.3+
- **身份认证**: JWT Token 认证
- **权限控制**: RBAC 角色权限
- **数据保护**: 敏感数据加密存储

### 3.3 可用性要求

- **系统可用性**: 99.9% SLA
- **容错机制**: 自动故障转移
- **数据备份**: 每日自动备份

### 3.4 兼容性要求

- **浏览器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **移动端**: iOS 14+, Android 10+
- **分辨率**: 320px - 4K

### 3.5 商业交付要求

{self._generate_delivery_requirements()}

---

## 4. 用户流程

### 4.1 主要用户旅程

{self._generate_user_journeys()}

### 4.2 页面结构

{self._generate_page_structure()}

---

## 5. 数据模型

### 5.1 核心实体

{self._generate_data_entities()}

### 5.2 关系图

```
[ER 图将在架构文档中详细说明]
```

---

## 6. 业务规则

{self._generate_business_rules()}

---

## 7. 验收标准

### 7.1 功能验收

{self._generate_acceptance_criteria()}

### 7.2 性能验收

- [ ] API 响应时间测试通过
- [ ] 并发压力测试通过
- [ ] 页面性能测试通过

### 7.3 安全验收

- [ ] 渗透测试通过
- [ ] 数据加密验证通过
- [ ] 权限控制验证通过

### 7.4 业务验收矩阵

{self._generate_acceptance_matrix()}

---

## 8. 发布计划

### 8.1 MVP (v2.0)

**时间**: 4 周
**范围**: 核心功能 + 基础架构

### 8.2 Phase 2 (v1.5)

**时间**: MVP 后 2 周
**范围**: 扩展功能 + 性能优化

### 8.3 Phase 3 (v2.0)

**时间**: Phase 2 后 4 周
**范围**: 高级功能 + 生态集成

---

## 9. 成功指标

| 指标 | 目标 | 测量方式 |
|:---|:---|:---|
| **用户增长** | 月活用户 1000+ | Analytics |
| **留存率** | 7 日留存 40%+ | Analytics |
| **满意度** | NPS 50+ | 用户调研 |
| **性能** | API 响应 < 200ms | APM |

### 9.1 经营与产品指标补充

{self._generate_business_kpis()}

---

## 10. 风险与限制

### 10.1 技术风险

{self._generate_technical_risks()}

### 10.2 业务风险

{self._generate_business_risks()}

### 10.3 依赖限制

{self._generate_dependencies()}

### 10.4 上线前置条件

{self._generate_launch_dependencies()}

---

## 附录

### A. 术语表

{self._generate_glossary()}

### B. 参考文档

{self._generate_references()}

### C. 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|:---|:---|:---|:---|
| v2.0.5 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本 | Super Dev |
"""

    def generate_architecture(self) -> str:
        """生成架构设计文档"""
        return f"""# {self.name} - 架构设计文档

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **版本**: v2.0.5
> **架构师**: Super Dev ARCHITECT 专家

---

## 1. 架构概述

### 1.1 系统目标

- **可扩展性**: 支持水平扩展，应对业务增长
- **可用性**: 99.9% 系统可用性
- **性能**: 低延迟、高吞吐
- **安全性**: 端到端安全防护

### 1.2 架构原则

1. **服务拆分**: 按业务领域拆分微服务
2. **数据库分离**: 读写分离、缓存层
3. **异步处理**: 消息队列解耦
4. **监控运维**: 全链路追踪、实时告警

### 1.3 需求到架构的落地映射

{self._generate_architecture_fit()}

---

## 2. 技术栈

### 2.0 语言工程策略

- **业务偏好语言**: {self._language_preferences_inline()}
- **落地策略**: 文档、Spec 与实现建议优先按偏好语言输出；跨模块场景可混合使用最合适语言。

### 2.1 前端技术栈

| 层级 | 技术选型 | 说明 |
|:---|:---|:---|
| **框架** | {self.frontend.title()} | 组件化开发 |
| **状态管理** | {self._get_state_management()} | 全局状态管理 |
| **UI 框架** | {self._get_ui_library()} | 组件库 |
| **构建工具** | {self._get_build_tool()} | 打包构建 |
| **HTTP 客户端** | Axios | API 请求 |
| **路由** | React Router | 页面路由 |

### 2.2 后端技术栈

| 层级 | 技术选型 | 说明 |
|:---|:---|:---|
| **运行时** | {self.backend.title()} | 服务器运行时 |
| **框架** | {self._get_backend_framework()} | Web 框架 |
| **API 规范** | RESTful | 接口设计 |
| **认证** | JWT | Token 认证 |
| **ORM** | {self._get_orm()} | 数据库 ORM |
| **验证** | Joi/Zod | 数据验证 |

{self._generate_ai_ml_stack()}

### 2.3 数据存储

| 存储 | 技术选型 | 用途 |
|:---|:---|:---|
| **主数据库** | {self._get_database()} | 持久化存储 |
| **缓存** | Redis | 缓存层 |
| **文件存储** | {self._get_file_storage()} | 文件/图片 |
| **搜索** | Elasticsearch | 全文搜索 |

### 2.4 基础设施

| 组件 | 技术选型 | 说明 |
|:---|:---|:---|
| **容器化** | Docker | 应用容器 |
| **编排** | Kubernetes | 容器编排 |
| **CI/CD** | GitHub Actions | 持续集成 |
| **监控** | Prometheus + Grafana | 指标监控 |
| **日志** | ELK Stack | 日志分析 |
| **追踪** | Jaeger | 分布式追踪 |

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                       用户层                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Web App  │  │ iOS App  │  │ Android  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼────────────┼────────────┼────────────────────────┘
        │            │            │
┌───────┼────────────┼────────────┼────────────────────────┐
│       │    CDN     │            │                      │
│  ┌────▼────────────┴────────┐    │                      │
│  │      负载均衡器          │    │                      │
│  └──────┬────────────────────┘    │                      │
└─────────┼─────────────────────────┼──────────────────────┘
          │                         │
┌─────────┼─────────────────────────┼──────────────────────┐
│         │      API 网关层         │                      │
│  ┌──────▼─────────────────────────▼──┐                   │
│  │  API Gateway (Kong / Nginx)      │                   │
│  │  - 认证授权                     │                   │
│  │  - 限流熔断                     │                   │
│  │  - 路由转发                     │                   │
│  └──────┬────────────────────────────┘                   │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────┼──────────────────────────────────────────────┐
│         │      服务层                                  │
│  ┌──────▼──────┐  ┌──────────┐  ┌──────────┐          │
│  │   API 服务  │  │ Auth 服务 │  │ User 服务 │  ...    │
│  └─────────────┘  └──────────┘  └──────────┘          │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────┼──────────────────────────────────────────────┐
│         │      数据层                                  │
│  ┌──────▼──────┐  ┌──────────┐  ┌──────────┐          │
│  │ PostgreSQL  │  │  Redis   │  │   S3     │          │
│  └─────────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 分层架构

#### 3.2.1 表现层 (Presentation Layer)

- **职责**: 用户界面、交互逻辑
- **技术**: {self.frontend.title()} + {self._get_ui_library()}
- **组件**:
  - 页面组件 (Pages)
  - 业务组件 (Components)
  - 布局组件 (Layouts)
  - 服务层 (Services)

#### 3.2.2 API 层 (API Layer)

- **职责**: 请求处理、协议转换
- **技术**: {self._get_backend_framework()}
- **组件**:
  - 路由定义
  - 中间件
  - 控制器
  - 请求验证

#### 3.2.3 业务层 (Business Layer)

- **职责**: 业务逻辑、规则引擎
- **组件**:
  - 服务
  - 领域模型
  - 业务规则
  - 工作流引擎

#### 3.2.4 数据访问层 (Data Access Layer)

- **职责**: 数据持久化、缓存管理
- **技术**: {self._get_orm()} + Redis
- **组件**:
  - Repository
  - DAO
  - Cache Manager
  - Transaction Manager

---

## 4. 核心模块设计

### 4.1 认证授权模块

{self._generate_auth_module_design()}

### 4.2 用户管理模块

{self._generate_user_module_design()}

### 4.3 业务模块

{self._generate_business_module_design()}

### 4.4 领域边界与职责拆分

{self._generate_domain_boundaries()}

---

## 5. 数据库设计

### 5.1 数据库选型

**主数据库**: PostgreSQL
- 理由: 成熟稳定、功能丰富、ACID 支持
- 版本: PostgreSQL 14+

**缓存**: Redis
- 理由: 高性能、数据结构丰富
- 用途: 会话存储、热点数据缓存

### 5.2 表结构设计

{self._generate_database_schema()}

### 5.3 索引策略

{self._generate_index_strategy()}

---

## 6. API 设计

### 6.1 RESTful 规范

```
GET    /api/resources          # 列表
GET    /api/resources/:id      # 详情
POST   /api/resources          # 创建
PUT    /api/resources/:id      # 更新
PATCH  /api/resources/:id      # 部分更新
DELETE /api/resources/:id      # 删除
```

### 6.2 核心 API 端点

{self._generate_api_endpoints()}

### 6.3 错误码规范

```
200 OK               # 成功
201 Created          # 创建成功
400 Bad Request      # 请求错误
401 Unauthorized     # 未认证
403 Forbidden        # 无权限
404 Not Found        # 不存在
422 Unprocessable   # 验证失败
500 Server Error     # 服务器错误
```

### 6.4 集成契约与版本策略

{self._generate_integration_contracts()}

---

## 7. 安全设计

### 7.1 认证机制

- **方式**: JWT (JSON Web Token)
- **流程**:
  1. 用户登录获取 Token
  2. 请求携带 Token
  3. 服务验证 Token
  4. Token 过期重新获取

### 7.2 授权机制

- **模型**: RBAC (Role-Based Access Control)
- **角色**:
  - 超级管理员
  - 管理员
  - 普通用户
  - 访客

### 7.3 数据加密

- **传输加密**: TLS 1.3
- **存储加密**: AES-256
- **密码加密**: bcrypt

### 7.4 安全防护

- **SQL 注入**: 参数化查询
- **XSS**: 输出转义
- **CSRF**: Token 验证
- **限流**: 令牌桶算法

---

## 8. 性能设计

### 8.1 性能目标

| 指标 | 目标值 |
|:---|:---|
| **API 响应时间** | P50 < 100ms, P95 < 200ms, P99 < 500ms |
| **页面加载时间** | FCP < 1.5s, LCP < 2.5s |
| **并发用户** | 1000+ 并发 |
| **QPS** | 5000+ QPS |

### 8.2 性能优化策略

{self._generate_performance_optimization()}

### 8.3 容错与降级策略

{self._generate_failure_strategy()}

---

## 9. 可观测性

### 9.1 监控指标

- **系统指标**: CPU、内存、磁盘、网络
- **应用指标**: QPS、响应时间、错误率
- **业务指标**: DAU、订单量、转化率

### 9.2 日志规范

- **格式**: JSON
- **级别**: DEBUG, INFO, WARN, ERROR
- **内容**: 时间戳、级别、消息、上下文

### 9.3 告警策略

- **告警渠道**: 邮件、钉钉、PagerDuty
- **告警级别**: P0-P4
- **响应时间**: P0 < 15min, P1 < 30min

### 9.4 审计与可追溯性

{self._generate_audit_strategy()}

---

## 10. 部署架构

### 10.1 容器化

```dockerfile
# 多阶段构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

### 10.2 Kubernetes 部署

{self._generate_k8s_config()}

### 10.3 CI/CD 流程

```yaml
# GitHub Actions
name: CI/CD
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: npm test
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: kubectl apply -f k8s/
```

### 10.4 发布与回滚策略

{self._generate_release_strategy()}

---

## 附录

### A. 技术选型对比

{self._generate_tech_comparison()}

### B. 架构决策记录 (ADR)

{self._generate_adr()}

### C. 参考文档

- [12-Factor App](https://12factor.net/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [REST API Design](https://restfulapi.net/)
"""

    def generate_uiux(self) -> str:
        """生成智能 UI/UX 设计文档（基于设计引擎推荐）"""
        # 获取智能设计推荐
        recommendations = self._get_design_recommendations()
        analysis = self._analyze_project_for_design()
        ui_intelligence = self._get_ui_intelligence(analysis)

        # 构建文档
        doc_parts = []

        # 文档头部
        doc_parts.append(f"""# {self.name} - UI/UX 设计文档

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **版本**: v2.0.5
> **设计师**: Super Dev UI/UX 专家

---

## 0. 设计分析

### 0.1 项目特征

基于需求描述，AI 分析出以下项目特征：

| 特征 | 分析结果 | 说明 |
|:---|:---|:---|
| **产品类型** | {analysis['product_type'].title()} | {self._get_product_type_desc(analysis['product_type'])} |
| **行业领域** | {analysis['industry'].title()} | {self._get_industry_desc(analysis['industry'])} |
| **风格倾向** | {analysis['style'].title()} | {self._get_style_desc(analysis['style'])} |
| **技术栈** | {self.frontend.upper()} | 前端框架 |
| **语言偏好** | {self._language_preferences_inline()} | 生成文档与实现建议的优先语言 |

### 0.2 设计推荐摘要

AI 基于项目特征，从设计数据库中为您推荐：

""")

        # 添加推荐摘要
        if recommendations.get('styles'):
            doc_parts.append(f"""**推荐风格**: {', '.join([s.get('name', s.get('Style Category', 'Unknown')) for s in recommendations['styles'][:2]])}
""")

        if recommendations.get('colors'):
            color = recommendations['colors']
            doc_parts.append(f"""**推荐配色**: {color.get('name', color.get('Palette Name', 'Standard'))}
""")

        if recommendations.get('fonts'):
            doc_parts.append(f"""**推荐字体**: {', '.join([f.get('Font Pairing Name', 'Professional') for f in recommendations['fonts'][:2]])}
""")

        doc_parts.append(f"""**推荐组件生态**: {ui_intelligence['primary_library']['name']}
""")

        doc_parts.append(f"""
---

## 1. 设计概述

### 1.1 设计理念

- **简洁**: 去除不必要的元素
- **一致**: 统一的视觉语言
- **高效**: 快速完成任务
- **愉悦**: 细节打磨体验

### 1.2 设计原则

1. **用户中心**: 以用户需求为出发点
2. **数据驱动**: 基于数据迭代设计
3. **移动优先**: 响应式设计
4. **无障碍**: 符合 WCAG 2.1 AA

### 1.3 商业级 UI 执行红线（强制）

1. **禁止 AI 模板化视觉**：禁止直接输出同质化模板页面与缺少信息层级的“拼块式 UI”。
2. **禁止紫/粉渐变主视觉**：除非品牌规范明确要求，不允许使用紫色或粉色渐变作为主品牌视觉。
3. **禁止 emoji 充当功能图标**：功能图标统一使用专业 SVG 图标库（如 Lucide/Heroicons/Tabler）。
4. **禁止默认系统字体直出**：必须在文档中明确品牌字体组合与字号层级，页面必须体现明确字重与层级节奏。
5. **必须具备可访问交互**：可见 focus 态、可读对比度、键盘可达、并兼容 reduced-motion。
6. **必须有设计 token**：颜色、间距、圆角、阴影和动效时长需以 token 形式统一管理。

### 1.4 商业级体验目标

{self._generate_ui_strategy(ui_intelligence)}

### 1.5 设计 Intelligence 结论

{self._render_ui_intelligence_summary(ui_intelligence)}

---

## 2. 设计系统

### 2.1 色彩规范

""")

        # 智能配色推荐
        if recommendations.get('colors'):
            color = recommendations['colors']
            doc_parts.append(f"""#### 推荐配色方案: {color.get('name', 'Professional Palette')}

**推荐理由**: 基于 {analysis['industry']} {analysis['product_type']} 产品的最佳实践

| 颜色 | 用途 | Hex | 备注 |
|:---|:---|:---|:---|
| **Primary** | 主要操作、强调 | {color.get('primary', color.get('Primary (Hex)', '#2563EB'))} | 主色调 |
| **Secondary** | 次要操作 | {color.get('secondary', color.get('Secondary (Hex)', '#64748B'))} | 辅助色 |
| **CTA** | 行动号召 | {color.get('accent', color.get('CTA (Hex)', '#2563EB'))} | 转化按钮 |
| **Background** | 页面背景 | {color.get('background', color.get('Background (Hex)', '#F9FAFB'))} | 背景色 |
| **Text** | 正文文本 | {color.get('text', color.get('Text (Hex)', '#111827'))} | 文本色 |
| **Border** | 边框线条 | {color.get('border', color.get('Border (Hex)', '#E5E7EB'))} | 分割线 |

**Tailwind 配置**:
```javascript
// tailwind.config.js
module.exports = {{
  theme: {{
    extend: {{
      colors: {{
        primary: '{color.get('primary', color.get('Primary (Hex)', '#2563EB'))}',
        secondary: '{color.get('secondary', color.get('Secondary (Hex)', '#64748B'))}',
        cta: '{color.get('accent', color.get('CTA (Hex)', '#2563EB'))}',
      }}
    }}
  }}
}}
```

---

""")
        else:
            # 默认配色
            doc_parts.append("""#### 主色调

| 颜色 | 用途 | Hex | RGB |
|:---|:---|:---|:---|
| **Primary** | 主要操作、强调 | #2563EB | rgb(37, 99, 235) |
| **Secondary** | 次要操作 | #64748B | rgb(100, 116, 139) |
| **Success** | 成功状态 | #10B981 | rgb(16, 185, 129) |
| **Warning** | 警告状态 | #F59E0B | rgb(245, 158, 11) |
| **Error** | 错误状态 | #EF4444 | rgb(239, 68, 68) |

---

""")

        # 智能字体推荐
        doc_parts.append("""### 2.2 字体规范
""")

        if recommendations.get('fonts'):
            doc_parts.append("""#### 推荐字体组合

""")
            for font in recommendations['fonts'][:2]:
                doc_parts.append(f"""**{font.get('name', font.get('Font Pairing Name', 'Professional'))}**
- **Heading**: {font.get('heading_font', font.get('Heading Font', 'Inter'))}
- **Body**: {font.get('body_font', font.get('Body Font', 'Roboto'))}
- **风格**: {font.get('mood', font.get('Mood/Style Keywords', 'Professional'))}
- **适用**: {font.get('best_for', font.get('Best For', 'General purpose'))}

**Google Fonts 导入**:
```html
{font.get('css_import', font.get('CSS Import', '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">'))}
```

""")
        else:
            doc_parts.append("""#### 字体家族

```css
font-family: 'Plus Jakarta Sans', 'Noto Sans SC', 'PingFang SC', 'Segoe UI', sans-serif;
```

#### 字号层级

| 用途 | 大小 | 字重 | 行高 |
|:---|:---|:---|:---|
| **H1** | 32px | 700 | 1.2 |
| **H2** | 24px | 600 | 1.3 |
| **H3** | 20px | 600 | 1.4 |
| **Body** | 16px | 400 | 1.5 |
| **Caption** | 14px | 400 | 1.4 |
| **Button** | 16px | 600 | 1 |

---

""")

        # 间距和圆角规范保持不变
        doc_parts.append(f"""### 2.3 间距规范

使用 8px 基础单位:
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px

### 2.4 圆角规范

| 元素 | 圆角 |
|:---|:---|
| **按钮** | 6px |
| **卡片** | 8px |
| **输入框** | 4px |
| **弹窗** | 12px |

### 2.5 视觉方向与品牌感

{self._generate_visual_direction()}

### 2.6 布局栅格与密度策略

{self._generate_layout_system(ui_intelligence)}

### 2.7 组件生态与实现基线

{self._render_component_ecosystem(ui_intelligence)}

---

## 3. 页面结构

### 3.1 整体布局
""")

        # 如果有 Landing 页面推荐，添加它
        if recommendations.get('landing'):
            landing = recommendations['landing']
            landing_sections = landing.get('sections', '')
            if isinstance(landing_sections, list):
                landing_sections_text = "\n".join(
                    f"- {s.get('name', s)}" if isinstance(s, dict) else f"- {s}"
                    for s in landing_sections[:8]
                )
            else:
                landing_sections_text = str(landing_sections)

            cta_strategy = landing.get('cta_strategy', {})
            if isinstance(cta_strategy, dict):
                cta_strategy_text = ", ".join(
                    f"{k}: {v}" for k, v in cta_strategy.items()
                )
            else:
                cta_strategy_text = str(cta_strategy)

            doc_parts.append(f"""
#### 推荐页面布局: {landing.get('name', 'Standard Layout')}

**布局类型**: {landing.get('category', 'classic').title()}

**页面结构**:
{landing_sections_text}

**CTA 策略**: {cta_strategy_text}

**转化优化**:
{chr(10).join(f"- {tip}" for tip in landing.get('conversion_tips', [])[:5])}

**适用场景**: {', '.join(landing.get('best_for', [])[:3])}

---

""")
        else:
            doc_parts.append("""
```
┌─────────────────────────────────────────────────┐
│  Header (Logo, Nav, User)                       │
├──────────┬──────────────────────────────────────┤
│          │                                       │
│ Sidebar  │         Main Content                 │
│ (Nav)    │                                       │
│          │                                       │
│          │                                       │
├──────────┴──────────────────────────────────────┤
│  Footer                                          │
└─────────────────────────────────────────────────┘
```

---

""")

        # 添加其他部分（保持原有的内容结构）
        doc_parts.append(f"""### 3.2 页面骨架优先级

{self._render_page_blueprints(ui_intelligence)}

### 3.3 导航结构

{self._generate_navigation_structure()}

---

## 4. 核心页面设计

### 4.1 登录页面

{self._generate_login_page_design()}

### 4.2 列表页面

{self._generate_list_page_design()}

### 4.3 详情页面

{self._generate_detail_page_design()}

### 4.4 表单页面

{self._generate_form_page_design()}

---

## 5. 组件设计

### 5.1 基础组件

{self._generate_base_components()}

### 5.2 业务组件

{self._generate_business_components()}

### 5.3 组件状态矩阵

{self._generate_component_state_matrix()}

### 5.4 图标、图表与内容模块

{self._render_visual_assets_strategy(ui_intelligence)}

---

## 6. 交互设计

### 6.1 加载状态

- **页面加载**: 骨架屏
- **按钮加载**: Spinner + 禁用
- **数据加载**: Loading 动画

### 6.2 错误处理

- **网络错误**: 友好提示 + 重试按钮
- **表单错误**: 字段级提示
- **系统错误**: 错误页面 + 返回按钮

### 6.3 空状态

- **无数据**: 空状态插图 + 引导文案
- **搜索无结果**: 提示 + 清空按钮

### 6.4 动效与反馈系统

{self._generate_motion_system(ui_intelligence)}

---

## 7. 响应式设计

### 7.1 断点定义

| 设备 | 宽度 | 说明 |
|:---|:---|:---|
| **Mobile** | < 640px | 手机竖屏 |
| **Tablet** | 640px - 1024px | 平板/手机横屏 |
| **Desktop** | 1024px - 1440px | 桌面 |
| **Large** | > 1440px | 大屏 |

### 7.2 响应式策略

- **Mobile First**: 从小屏开始设计
- **流式布局**: Flexbox + Grid
- **响应式图片**: srcset + sizes
- **响应式字体**: clamp() 函数

### 7.3 商业化与信任设计

{self._generate_trust_and_conversion_rules(ui_intelligence)}

---

## 8. 用户流程

### 8.1 主要用户旅程

{self._generate_user_journeys_ui()}

### 8.2 交互流程图

```
用户 → [页面] → [操作] → [反馈] → [下一步]
```

---

## 9. 微交互

### 9.1 按钮交互

- **悬停**: 背景色变化
- **点击**: 缩放动画
- **禁用**: 透明度降低

### 9.2 表单交互

- **聚焦**: 边框高亮
- **输入**: 实时验证
- **提交**: Loading 状态

### 9.3 列表交互

- **悬停**: 操作按钮显示
- **点击**: 选中状态
- **拖拽**: 视觉反馈

---

## 10. 设计交付物

### A. 设计资产

- Figma 设计稿链接
- 图标库 (Heroicons / Lucide)
- 图片资源 (Unsplash / Pexels)

### B. 插件资源

- {ui_intelligence['primary_library']['name']} 组件生态
- Figma 插件推荐

### C. 设计参考

- [Dribbble](https://dribbble.com/)
- [Behance](https://www.behance.net/)
- [Mobbin](https://mobbin.com/)
""")

        # 添加 UX 最佳实践部分
        if recommendations.get('ux_tips'):
            doc_parts.append("""

---

## 11. UX 最佳实践

基于项目特征，AI 为您推荐以下 UX 最佳实践：

""")
            for i, tip in enumerate(recommendations['ux_tips'][:5], 1):
                guideline = tip.get('guideline', tip)
                domain = guideline.get('domain', 'UX')
                domain_text = domain.value if hasattr(domain, 'value') else str(domain)
                complexity = guideline.get('complexity', 'medium')
                complexity_text = str(complexity).title()
                doc_parts.append(f"""### {i}. {guideline.get('topic', 'Best Practice')} ({domain_text})

**最佳实践**:
{guideline.get('best_practice', 'Follow industry standards')}

**避免**:
{guideline.get('anti_pattern', 'Common mistakes to avoid')}

**影响**: {guideline.get('impact', 'Improved user experience')}

**实施难度**: {complexity_text}

""")

        return "\n".join(doc_parts)

    def _get_product_type_desc(self, product_type: str) -> str:
        """获取产品类型描述"""
        descs = {
            'saas': 'SaaS 软件服务，需要专业可信的设计',
            'ecommerce': '电商平台，注重转化和购买体验',
            'landing': '营销落地页，强调 CTA 和转化',
            'dashboard': '管理后台，注重数据展示和操作效率',
            'content': '内容平台，注重阅读体验',
            'general': '通用产品'
        }
        return descs.get(product_type, '常规产品')

    def _get_industry_desc(self, industry: str) -> str:
        """获取行业描述"""
        descs = {
            'healthcare': '医疗健康行业，需要传递安全、专业感',
            'fintech': '金融科技，需要信任、安全的设计语言',
            'education': '教育行业，需要亲和力、专业性',
            'legal': '法律服务行业，需要权威、可信和清晰表达',
            'government': '政务/公共服务，需要高可读性与可访问性',
            'beauty': '美业/健康服务，需要品牌感、精致感与转化路径',
            'general': '通用行业'
        }
        return descs.get(industry, '常规行业')

    def _get_style_desc(self, style: str) -> str:
        """获取风格描述"""
        descs = {
            'minimal': '极简风格，去除冗余，突出核心',
            'professional': '专业风格，商务、正式',
            'playful': '活泼风格，有趣、生动',
            'luxury': '奢华风格，高端、精致',
            'modern': '现代风格，时尚、前沿'
        }
        return descs.get(style, '现代风格')

    def _get_ui_intelligence(self, analysis: dict | None = None) -> dict:
        """获取结构化 UI Intelligence 推荐"""
        analysis = analysis or self._analyze_project_for_design()
        from super_dev.design import UIIntelligenceAdvisor

        advisor = UIIntelligenceAdvisor()
        return advisor.recommend(
            description=self.description,
            frontend=self.frontend,
            product_type=analysis["product_type"],
            industry=analysis["industry"],
            style=analysis["style"],
            ui_library=self.ui_library,
        )
    def _get_state_management(self) -> str:
        """获取状态管理方案"""
        mapping = {
            "react": "Redux Toolkit / Zustand",
            "vue": "Pinia",
            "angular": "NgRx",
            "svelte": "Svelte Stores",
        }
        return mapping.get(self.frontend, "Context API")

    def _get_ui_library(self) -> str:
        """获取 UI 库"""
        return self._get_ui_intelligence()["primary_library"]["name"]

    def _get_build_tool(self) -> str:
        """获取构建工具"""
        mapping = {
            "react": "Vite",
            "vue": "Vite",
            "angular": "Angular CLI",
            "svelte": "Vite",
        }
        return mapping.get(self.frontend, "Webpack")

    def _get_backend_framework(self) -> str:
        """获取后端框架"""
        mapping = {
            "node": "Express / Fastify / NestJS",
            "python": "FastAPI / Django",
            "go": "Gin / Echo",
            "java": "Spring Boot",
            "rust": "Actix Web / Axum",
            "php": "Laravel / Symfony",
            "ruby": "Rails / Sinatra",
            "csharp": "ASP.NET Core",
            "kotlin": "Ktor / Spring Boot",
            "swift": "Vapor",
            "elixir": "Phoenix",
            "scala": "Play / Akka HTTP",
            "dart": "Shelf / Dart Frog",
        }
        return mapping.get(self.backend, "Express")

    def _get_database(self) -> str:
        """获取数据库"""
        return "PostgreSQL 14+"

    def _get_orm(self) -> str:
        """获取 ORM"""
        mapping = {
            "node": "Prisma / TypeORM",
            "python": "SQLAlchemy / Django ORM",
            "go": "GORM",
            "java": "Hibernate / JPA",
            "rust": "SeaORM / Diesel",
            "php": "Eloquent / Doctrine",
            "ruby": "Active Record",
            "csharp": "Entity Framework Core",
            "kotlin": "Exposed / Spring Data JPA",
            "swift": "Fluent",
            "elixir": "Ecto",
            "scala": "Slick / Doobie",
            "dart": "Drift / Prisma Client Dart",
        }
        return mapping.get(self.backend, "Prisma")

    def _get_file_storage(self) -> str:
        """获取文件存储"""
        return "AWS S3 / 阿里云 OSS"

    def _generate_ai_ml_stack(self) -> str:
        """生成 AI/ML 技术栈部分"""
        keywords = self._extract_tech_keywords()

        # 检查是否有任何 AI/ML 相关技术
        has_ai_content = any([
            keywords["ai_frameworks"],
            keywords["agent_tools"],
            keywords["ml_libraries"],
            keywords["vector_stores"],
            keywords["orchestration"],
            keywords["other_keywords"],
        ])

        if not has_ai_content:
            return ""  # 如果没有 AI/ML 内容，返回空字符串

        # 构建 AI/ML 技术栈部分
        lines = ["### 2.2.1 AI/ML 技术栈", "", "| 层级 | 技术选型 | 说明 |", "|:---|:---|:---|"]

        # AI 框架
        if keywords["ai_frameworks"]:
            for framework in keywords["ai_frameworks"]:
                lines.append(f"| **AI 框架** | {framework} | Agent 编排与开发 |")

        # Agent 工具
        if keywords["agent_tools"]:
            for tool in keywords["agent_tools"]:
                lines.append(f"| **Agent 工具** | {tool} | Agent 构建与管理 |")

        # ML 库
        if keywords["ml_libraries"]:
            for lib in keywords["ml_libraries"]:
                lines.append(f"| **ML 库** | {lib} | 机器学习模型 |")

        # 向量数据库
        if keywords["vector_stores"]:
            for store in keywords["vector_stores"]:
                lines.append(f"| **向量数据库** | {store} | 向量存储与检索 |")

        # 编排工具
        if keywords["orchestration"]:
            for tool in keywords["orchestration"]:
                lines.append(f"| **编排工具** | {tool} | 工作流编排 |")

        # 其他关键词
        if keywords["other_keywords"]:
            for keyword in keywords["other_keywords"]:
                lines.append(f"| **核心能力** | {keyword} | 关键技术特性 |")

        lines.append("")
        return "\n".join(lines)

    def _generate_vision(self) -> str:
        """生成产品愿景"""
        return f"""
打造一个{self.description}的{self.platform.upper()}应用，
为用户提供简单、高效、愉悦的使用体验。

我们相信：
- **用户至上**: 一切以用户价值为导向
- **简单至上**: 复杂的事情简单化
- **体验至上**: 每个细节都精益求精
"""

    def _generate_target_users(self) -> str:
        """生成目标用户"""
        return """
**主要用户群体**:

1. **核心用户** (80%)
   - 年龄: 25-40 岁
   - 职业: 白领、自由职业者
   - 特征: 熟悉互联网、追求效率

2. **次要用户** (15%)
   - 年龄: 18-25 岁 / 40-50 岁
   - 特征: 学生/资深从业者

3. **潜在用户** (5%)
   - 特征: 对新功能感兴趣
"""

    def _generate_value_proposition(self) -> str:
        """生成价值主张"""
        return f"""
**核心价值**:

1. **省时**: 比 {self.description} 传统方式节省 50% 时间
2. **省心**: 一站式解决方案，无需切换多个工具
3. **省力**: 简洁直观，零学习成本
"""

    def _generate_core_features(self) -> str:
        """生成核心功能"""
        # 从描述中提取业务领域关键词
        description_lower = self.description.lower()
        keywords = self._extract_tech_keywords()

        # 基础功能（所有应用都有）
        base_features = """
1. **用户认证与授权**
   - 注册/登录（邮箱/手机号）
   - 密码重置
   - JWT Token 认证
   - 第三方登录（可选）

2. **用户中心**
   - 个人资料管理
   - 账户安全设置
   - 偏好配置
"""

        # 根据业务领域生成核心功能
        business_features = ""

        # 求职招聘领域
        if any(word in description_lower for word in ["求职", "招聘", "job", "resume", "career", "简历", "职位"]):
            business_features = """
3. **简历管理**
   - 在线简历创建与编辑
   - 简历模板选择
   - 简历导入（上传 PDF/Word）
   - 简历预览与导出
   - 简历智能评分与优化建议

4. **职位搜索与推荐**
   - 职位搜索（关键词/地点/薪资）
   - 智能职位推荐
   - 职位收藏与对比
   - 职位订阅通知

5. **求职助手"""
            # 如果有 AI/Agent 相关技术，添加智能功能
            if keywords["ai_frameworks"] or keywords["agent_tools"] or "Multi-Agent System" in keywords["other_keywords"]:
                business_features += """
   - 多 Agent 智能求职助手：
     * **简历匹配 Agent**: JD 与简历匹配度分析，识别技能差距，提供优化建议
     * **简历优化 Agent**: 自动优化简历内容，提高匹配度
     * **职位推荐 Agent**: 基于用户画像智能推荐职位
     * **面试准备 Agent**: 模拟面试，提供问题预测和回答建议
     * **薪资谈判 Agent**: 分析市场薪资，提供谈判策略
     * **职业规划 Agent**: 基于行业趋势提供职业发展建议
   - 实时对话式求职咨询
   - 智能简历投递建议"""
            else:
                business_features += """
   - 求职进度跟踪
   - 面试提醒与日程管理
   - 求职数据分析"""

        # 电商领域
        elif any(word in description_lower for word in ["电商", "商城", "shop", "store", "mall", "购物"]):
            business_features = """
3. **商品管理**
   - 商品浏览与搜索
   - 商品分类与筛选
   - 商品详情与评价

4. **购物车与订单**
   - 购物车管理
   - 订单创建与支付
   - 物流跟踪

5. **用户中心**
   - 收藏夹
   - 浏览历史
   - 优惠券管理"""

        # 内容/社区领域
        elif any(word in description_lower for word in ["内容", "社区", "content", "community", "blog", "forum", "社交"]):
            business_features = """
3. **内容管理**
   - 内容发布与编辑
   - 富文本支持
   - 图片/视频上传

4. **社交互动**
   - 点赞/评论/分享
   - 关注作者
   - 消息通知"""

        # 教育领域
        elif any(word in description_lower for word in ["教育", "培训", "education", "learning", "课程", "学习"]):
            business_features = """
3. **课程管理**
   - 课程浏览与购买
   - 课程进度跟踪
   - 学习笔记

4. **学习互动**
   - 问答讨论
   - 作业提交
   - 在线测试"""

        # 通用默认
        else:
            business_features = f"""
3. **核心业务功能**
   - {self.description}
   - 数据管理与展示
   - 搜索与过滤
   - 数据导入/导出"""

        return base_features + business_features

    def _generate_extended_features(self) -> str:
        """生成扩展功能"""
        return """
1. **高级功能**
   - 数据导入/导出
   - 批量操作
   - 高级搜索

2. **协作功能**
   - 分享邀请
   - 权限管理
   - 活动日志

3. **分析功能**
   - 数据统计
   - 图表展示
   - 报告导出
"""

    def _generate_user_stories(self) -> str:
        """生成用户故事"""
        return """
| 作为 | 我想要 | 以便于 | 优先级 |
|:---|:---|:---|:---:|
| 用户 | 快速注册账户 | 开始使用 | P0 |
| 用户 | 登录后查看数据 | 了解情况 | P0 |
| 用户 | 搜索筛选数据 | 快速找到 | P1 |
| 用户 | 导出数据 | 离线分析 | P2 |
"""

    def _generate_data_entities(self) -> str:
        """生成数据实体"""
        return """
### 用户实体

**属性**:
- 用户 ID (UUID)
- 用户名 (string)
- 邮箱 (string, unique)
- 密码哈希 (string)
- 创建时间 (datetime)
- 更新时间 (datetime)
- 状态 (active/inactive)

### 会话实体

**属性**:
- 会话 ID (UUID)
- 用户 ID (FK)
- Token (string)
- 过期时间 (datetime)
- 创建时间 (datetime)

### 审计日志实体

**属性**:
- 日志 ID (UUID)
- 用户 ID (FK)
- 操作类型 (string)
- 操作详情 (JSON)
- IP 地址 (string)
- 时间戳 (datetime)
"""

    def _generate_user_journeys(self) -> str:
        """生成用户旅程"""
        return """
**旅程 1: 新用户注册**

```
发现产品 → 访问官网 → 点击注册 → 填写信息 → 验证邮箱 → 登录使用
```

痛点: 注册流程太长
优化: 社交登录一键注册

**旅程 2: 日常使用**

```
登录 → 浏览内容 → 搜索筛选 → 查看详情 → 执行操作 → 退出
```

关键点: 搜索响应速度、操作流畅度
"""

    def _generate_page_structure(self) -> str:
        """生成页面结构"""
        return """
**主要页面**:

1. **登录/注册页**
   - 登录表单
   - 注册表单
   - 忘记密码

2. **首页**
   - 欢迎信息
   - 快速入口
   - 数据概览

3. **列表页**
   - 搜索栏
   - 筛选器
   - 数据列表
   - 分页器

4. **详情页**
   - 详细信息
   - 相关操作
   - 返回按钮

5. **设置页**
   - 个人资料
   - 账户安全
   - 偏好设置
"""

    def _generate_business_rules(self) -> str:
        """生成业务规则"""
        return """
### 密码规则
- 最小长度 8 位
- 必须包含大小写字母、数字
- 不能包含用户名
- 90 天必须更换

### 访问规则
- 连续失败 5 次锁定 30 分钟
- Session 超时时间 2 小时
- 同时在线设备限制 5 台

### 数据规则
- 用户删除需保留 30 天
- 敏感操作需要二次验证
- 日志保留 180 天
"""

    def _generate_acceptance_criteria(self) -> str:
        """生成验收标准"""
        return """
### 功能验收
- [ ] 用户可以使用邮箱注册
- [ ] 用户可以使用密码登录
- [ ] 用户可以重置密码
- [ ] 登录状态保持 2 小时
- [ ] 所有请求需要认证（除公开接口）

### 性能验收
- [ ] 登录响应时间 < 500ms
- [ ] API 响应时间 P95 < 200ms
- [ ] 支持并发用户数 > 1000

### 安全验收
- [ ] 密码使用 bcrypt 加密
- [ ] Token 使用 JWT 签名
- [ ] 所有输入验证防注入
- [ ] 敏感操作有审计日志
"""

    def _generate_technical_risks(self) -> str:
        """生成技术风险"""
        return """
### 性能风险
- 大量用户并发登录可能导致数据库压力
- Token 验证可能成为瓶颈

**缓解方案**:
- 使用 Redis 缓存活跃 Session
- 实现无状态 JWT 验证

### 安全风险
- 密码泄露风险
- Session 劫持风险

**缓解方案**:
- 使用 bcrypt 加密存储
- 实现 CSRF 保护
- 强制 HTTPS
"""

    def _generate_business_risks(self) -> str:
        """生成业务风险"""
        return """
### 用户体验风险
- 密码复杂度要求可能导致用户流失
- 多次验证可能影响注册转化

**缓解方案**:
- 提供社交登录选项
- 优化验证流程

### 合规风险
- GDPR 数据保护要求
- 密码存储安全标准

**缓解方案**:
- 实现数据导出/删除功能
- 定期安全审计
"""

    def _generate_dependencies(self) -> str:
        """生成依赖关系"""
        return """
### 外部依赖
- 邮件服务 (SendGrid/阿里云)
- 短信服务 (可选)
- 社交登录 (OAuth2)

### 内部依赖
- 用户服务 (提供用户信息)
- 通知服务 (发送验证消息)
- 审计服务 (记录操作日志)
"""

    def _generate_glossary(self) -> str:
        """生成术语表"""
        return """
| 术语 | 定义 |
|:---|:---|
| JWT | JSON Web Token，用于身份验证的令牌 |
| Session | 用户会话，记录登录状态 |
| 2FA | 双因素认证 |
| RBAC | 基于角色的访问控制 |
| CSRF | 跨站请求伪造 |
"""

    def _generate_references(self) -> str:
        """生成参考资料"""
        return """
### 技术标准
- OWASP Top 10
- RFC 6749 (OAuth 2.0)
- RFC 7519 (JWT)

### 最佳实践
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
"""

    # ========== Architecture Document Methods ==========

    def _generate_auth_module_design(self) -> str:
        """生成认证模块设计"""
        return """
### 认证模块 (Auth Module)

**职责**:
- 用户注册/登录
- Token 签发/验证
- 密码管理

**接口**:
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/verify
```

**实现要点**:
- JWT Token 签发使用 RS256
- Refresh Token 存储在 Redis
- 密码使用 bcrypt (cost=10)
"""

    def _generate_user_module_design(self) -> str:
        """生成用户模块设计"""
        return """
### 用户模块 (User Module)

**职责**:
- 用户信息管理
- 权限验证
- 用户状态管理

**接口**:
```
GET /api/v1/users/me
PATCH /api/v1/users/me
PUT /api/v1/users/me/password
GET /api/v1/users/:id
```

**实现要点**:
- 实现乐观锁防止并发修改
- 使用 RBAC 权限模型
- 敏感操作需要二次验证
"""

    def _generate_business_module_design(self) -> str:
        """生成业务模块设计"""
        return """
### 业务模块 (Business Module)

**职责**:
- 核心业务逻辑
- 数据验证
- 业务规则执行

**接口**:
```
GET /api/v1/resources
POST /api/v1/resources
GET /api/v1/resources/:id
PATCH /api/v1/resources/:id
DELETE /api/v1/resources/:id
```

**实现要点**:
- 实现幂等性
- 数据验证使用 Pydantic/Zod
- 审计日志记录所有变更
"""

    def _generate_database_schema(self) -> str:
        """生成数据库设计"""
        return """
### 表结构

**users 表**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

**sessions 表**:
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_token (token)
);
```

**audit_logs 表**:
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```
"""

    def _generate_index_strategy(self) -> str:
        """生成索引策略"""
        return """
### 索引设计

| 表 | 索引 | 类型 | 用途 |
|:---|:---|:---|:---|
| users | idx_email | B-tree | 邮箱查询 |
| users | idx_username | B-tree | 用户名查询 |
| sessions | idx_user_id | B-tree | 用户会话查询 |
| sessions | idx_token | B-tree | Token 验证 |
| audit_logs | idx_user_id | B-tree | 用户审计日志 |
| audit_logs | idx_created_at | B-tree | 时间范围查询 |

### 查询优化
- 使用连接池 (pgbouncer)
- 实现查询缓存层
- 慢查询监控 (>100ms)
"""

    def _generate_api_endpoints(self) -> str:
        """生成 API 端点"""
        return """
### API 端点列表

#### 认证相关
```
POST   /api/v1/auth/register        # 用户注册
POST   /api/v1/auth/login           # 用户登录
POST   /api/v1/auth/logout          # 用户登出
POST   /api/v1/auth/refresh         # 刷新 Token
POST   /api/v1/auth/verify          # 验证 Token
POST   /api/v1/auth/forgot-password # 忘记密码
POST   /api/v1/auth/reset-password  # 重置密码
```

#### 用户相关
```
GET    /api/v1/users/me             # 当前用户信息
PATCH  /api/v1/users/me             # 更新用户信息
PUT    /api/v1/users/me/password    # 修改密码
GET    /api/v1/users/:id            # 用户详情 (管理员)
```

#### 业务资源
```
GET    /api/v1/resources            # 资源列表
POST   /api/v1/resources            # 创建资源
GET    /api/v1/resources/:id        # 资源详情
PATCH  /api/v1/resources/:id        # 更新资源
DELETE /api/v1/resources/:id        # 删除资源
```
"""

    def _generate_performance_optimization(self) -> str:
        """生成性能优化"""
        return """
### 后端优化

**数据库优化**:
- 连接池配置 (max_connections=100)
- 查询结果缓存 (Redis)
- 慢查询日志优化

**应用层优化**:
- 异步 I/O 处理
- 请求限流 (100 req/s)
- 响应压缩 (gzip)

**前端优化**:
- 代码分割和懒加载
- 资源 CDN 加速
- 图片优化和缓存

### 监控指标
- API 响应时间 P95 < 200ms
- 数据库查询时间 < 50ms
- 错误率 < 0.1%
"""

    def _generate_tech_comparison(self) -> str:
        """生成技术对比"""
        return """
### 技术选型对比

| 方面 | 选择 | 备选 | 理由 |
|:---|:---|:---|:---|
| 前端框架 | React | Vue, Angular | 生态成熟，组件丰富 |
| 状态管理 | Redux Toolkit | Zustand, Jotai | 标准方案，文档完善 |
| UI 库 | Ant Design | Material-UI | 设计规范完善 |
| 后端框架 | Express | Fastify, Koa | 灵活，中间件丰富 |
| ORM | Prisma | TypeORM, Sequelize | 类型安全，迁移友好 |
| 数据库 | PostgreSQL | MySQL, MongoDB | 功能强大，JSON 支持 |
| 缓存 | Redis | Memcached | 功能丰富，持久化 |
"""

    def _generate_adr(self) -> str:
        """生成架构决策记录"""
        return """
### 架构决策记录 (ADR)

#### ADR-001: 选择 JWT 作为认证方案

**状态**: 已接受

**背景**: 需要无状态的认证机制支持分布式部署

**决策**: 使用 JWT (JSON Web Token) 进行身份验证

**理由**:
- 无状态，易于横向扩展
- 标准化，跨语言支持
- 包含声明，减少数据库查询

**后果**:
- 优点: 无需 Session 存储，支持分布式
- 缺点: Token 无法撤销，需要短过期时间

#### ADR-002: 选择 PostgreSQL 作为主数据库

**状态**: 已接受

**背景**: 需要关系型数据库支持复杂查询

**决策**: 使用 PostgreSQL 作为主数据库

**理由**:
- 功能强大，支持 JSON、全文搜索
- ACID 完整，数据一致性强
- 开源免费，社区活跃

**后果**:
- 优点: 数据完整性好，扩展性强
- 缺点: 配置相对复杂
"""

    def _generate_k8s_config(self) -> str:
        """生成 Kubernetes 配置"""
        return """
### Deployment 配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### ConfigMap 配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  NODE_ENV: "production"
```

### Secret 配置

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  url: "postgresql://user:pass@host:5432/db"
```

### Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: app-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 80
```
"""

    # ========== UI/UX Document Methods ==========

    def _generate_navigation_structure(self) -> str:
        """生成导航结构"""
        return """
### 导航结构

**主导航**:
- 首页
- 功能模块
- 设置
- 帮助

**用户菜单**:
- 个人资料
- 账户安全
- 通知设置
- 退出登录

**面包屑**:
- 显示当前页面路径
- 支持快速返回上级
"""

    def _generate_login_page_design(self) -> str:
        """生成登录页设计"""
        return """
### 登录/注册页

**布局**:
- 居中卡片式设计
- 左侧品牌展示
- 右侧表单区域

**表单元素**:
- 邮箱输入框 (带验证)
- 密码输入框 (带显示/隐藏)
- 记住我复选框
- 忘记密码链接
- 登录按钮 (主操作)
- 注册链接 (次要操作)

**交互**:
- 输入框实时验证
- 登录按钮 Loading 状态
- 错误提示显示在表单顶部
"""

    def _generate_list_page_design(self) -> str:
        """生成列表页设计"""
        return """
### 列表页

**布局**:
- 顶部搜索栏
- 左侧筛选器
- 右侧数据列表
- 底部分页器

**列表项**:
- 卡片式展示
- 显示关键信息
- 操作按钮组
- 状态标签

**交互**:
- 下拉加载更多
- 搜索防抖 (300ms)
- 筛选实时更新
"""

    def _generate_detail_page_design(self) -> str:
        """生成详情页设计"""
        return """
### 详情页

**布局**:
- 顶部导航栏 (返回 + 操作)
- 主要信息区
- 相关信息区
- 操作区

**信息层级**:
- 标题 (H1)
- 摘要
- 详细内容
- 元数据

**交互**:
- 编辑/删除操作
- 相关内容推荐
- 快速导航
"""

    def _generate_form_page_design(self) -> str:
        """生成表单页设计"""
        return """
### 表单页

**布局**:
- 左侧表单
- 右侧预览 (可选)
- 底部操作按钮

**表单元素**:
- 必填项标记 (*)
- 字段提示信息
- 实时验证反馈
- 保存/取消按钮

**交互**:
- 表单验证
- 草稿自动保存
- 提交 Loading 状态
"""

    def _generate_base_components(self) -> str:
        """生成基础组件"""
        return """
### 基础组件库

**按钮 (Button)**:
- 主要按钮
- 次要按钮
- 危险按钮
- 文本按钮

**输入框 (Input)**:
- 文本输入
- 密码输入
- 数字输入
- 日期选择

**数据展示 (Data Display)**:
- 表格
- 卡片
- 列表
- 标签

**反馈 (Feedback)**:
- 消息提示
- 对话框
- 加载状态
- 空状态
"""

    def _generate_business_components(self) -> str:
        """生成业务组件"""
        return """
### 业务组件

**用户相关**:
- 用户头像
- 用户卡片
- 用户选择器

**认证相关**:
- 登录表单
- 注册表单
- 密码修改

**内容相关**:
- 内容卡片
- 内容列表
- 内容编辑器
"""

    def _generate_user_journeys_ui(self) -> str:
        """生成用户旅程 UI"""
        return """
### 用户旅程 UI 设计

**旅程 1: 新用户注册**

关键页面:
1. 访问首页 → CTA 按钮 "开始使用"
2. 注册页 → 简洁表单
3. 邮箱验证页 → 清晰提示
4. 登录页 → 自动跳转
5. 首次登录引导 → 功能介绍

**旅程 2: 日常使用**

关键页面:
1. 登录页 → 快速登录
2. 首页 → 功能概览
3. 功能页 → 核心操作
4. 设置页 → 个人配置

**交互要点**:
- 操作反馈及时
- 错误提示清晰
- 加载状态明确
"""

    def _render_ui_intelligence_summary(self, profile: dict) -> str:
        lines = [
            f"- **界面定位**: {profile['surface']}",
            f"- **信息密度**: {profile['information_density']}",
            f"- **行业语气**: {profile['industry_tone']}",
            f"- **首选组件生态**: {profile['primary_library']['name']}",
            f"- **表单基线**: {profile['component_stack']['form']}",
            f"- **数据展示基线**: {profile['component_stack']['table']} / {profile['component_stack']['chart']}",
            "",
            "**优先原则**:",
        ]
        lines.extend(f"- {item}" for item in profile["benchmark_principles"])
        lines.extend(["", "**设计知识库关键词**:"])
        lines.append("- " + " / ".join(profile["knowledge_keywords"]))
        return "\n".join(lines)

    def _render_component_ecosystem(self, profile: dict) -> str:
        primary = profile["primary_library"]
        lines = [
            f"#### 首选方案: {primary['name']}",
            "",
            f"**适用原因**: {primary['rationale']}",
            "",
            "**核心能力**:",
        ]
        lines.extend(f"- {item}" for item in primary["strengths"])
        lines.extend(
            [
                "",
                "**实现注意事项**:",
            ]
        )
        lines.extend(f"- {item}" for item in primary["notes"])
        lines.extend(
            [
                "",
                "#### 配套技术基线",
                "",
                f"- **表单与验证**: {profile['component_stack']['form']}",
                f"- **图表能力**: {profile['component_stack']['chart']}",
                f"- **表格/数据工作区**: {profile['component_stack']['table']}",
                f"- **图标体系**: {profile['component_stack']['icons']}",
                f"- **动效能力**: {profile['component_stack']['motion']}",
            ]
        )

        alternatives = profile.get("alternative_libraries", [])
        if alternatives:
            lines.extend(["", "#### 可选备选方案", ""])
            for item in alternatives:
                lines.append(f"- **{item['name']}**: {item['rationale']}")
        return "\n".join(lines)

    def _render_page_blueprints(self, profile: dict) -> str:
        lines: list[str] = []
        for blueprint in profile["page_blueprints"]:
            lines.extend(
                [
                    f"#### {blueprint['page']}",
                    "",
                    "**推荐模块顺序**:",
                ]
            )
            lines.extend(f"- {section}" for section in blueprint["sections"])
            lines.extend(
                [
                    "",
                    f"**设计重点**: {blueprint['focus']}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip()

    def _render_visual_assets_strategy(self, profile: dict) -> str:
        lines = [
            f"- **图标库**: {profile['component_stack']['icons']}，禁止 emoji 代替功能图标。",
            f"- **图表策略**: {profile['component_stack']['chart']}，图表先服务决策，再考虑视觉装饰。",
            "- **品牌/合作方 Logo**: 统一使用官方 SVG 或可信来源矢量资产，避免猜测版图形。",
            "- **截图策略**: 对外页面优先使用真实产品截图、流程图或数据示意，而不是空洞插画。",
            "",
            "**优先落地的组件模块**:",
        ]
        lines.extend(f"- {item}" for item in profile["component_priorities"])
        lines.extend(["", "**明确禁止**:"])
        lines.extend(f"- {item}" for item in profile["banned_patterns"][:6])
        return "\n".join(lines)

    def _get_design_recommendations(self) -> dict:
        """获取智能设计推荐"""
        try:
            # 导入设计引擎
            import sys
            from pathlib import Path

            # 添加项目根目录到 Python 路径
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from super_dev.design import (
                DesignIntelligenceEngine,
                get_landing_generator,
                get_ux_guide,
            )

            # 分析项目特征
            analysis = self._analyze_project_for_design()

            # 初始化引擎
            design_engine = DesignIntelligenceEngine()
            landing_gen = get_landing_generator()
            ux_guide = get_ux_guide()

            # 获取推荐
            recommendations = {}

            # 1. 风格推荐
            style_query = f"{analysis['style']} {analysis['product_type']} {analysis['industry']}"
            style_results = design_engine.search(style_query, domain="style", max_results=3)
            recommendations['styles'] = style_results.get("results", [])[:3]

            # 2. 配色推荐
            color_query = f"{analysis['industry']} {analysis['product_type']}" if analysis['industry'] != 'general' else analysis['product_type']
            color_results = design_engine.search(color_query, domain="color", max_results=1)
            recommendations['colors'] = (color_results.get("results", []) or [None])[0]

            # 3. 字体推荐
            font_query = f"{analysis['style']} professional"
            font_results = design_engine.search(font_query, domain="typography", max_results=2)
            recommendations['fonts'] = font_results.get("results", [])[:2]

            # 4. Landing 页面推荐（如果适用）
            if analysis['product_type'] in ['landing', 'saas', 'ecommerce']:
                landing_pattern = landing_gen.recommend(
                    product_type=analysis['product_type'],
                    goal='signup',
                    audience='B2C' if analysis['industry'] == 'general' else 'B2B'
                )
                recommendations['landing'] = (
                    landing_pattern.to_dict()
                    if landing_pattern and hasattr(landing_pattern, "to_dict")
                    else None
                )
            else:
                recommendations['landing'] = None

            # 5. UX 最佳实践
            ux_quick_wins = ux_guide.get_quick_wins(max_results=5)
            ux_tips = []
            for rec in ux_quick_wins:
                guideline = rec.guideline
                ux_tips.append({
                    "guideline": {
                        "domain": guideline.domain.value if hasattr(guideline.domain, "value") else str(guideline.domain),
                        "topic": guideline.topic,
                        "best_practice": guideline.best_practice,
                        "anti_pattern": guideline.anti_pattern,
                        "impact": guideline.impact,
                        "complexity": guideline.complexity,
                    },
                    "priority": rec.priority,
                    "implementation_effort": rec.implementation_effort,
                    "user_impact": rec.user_impact,
                })
            recommendations['ux_tips'] = ux_tips

            return recommendations

        except Exception as e:
            # 如果设计引擎失败，返回空推荐
            print(f"Warning: Design engine failed: {e}")
            return {
                'styles': [],
                'colors': None,
                'fonts': [],
                'landing': None,
                'ux_tips': []
            }

    def extract_requirements(self) -> list:
        """从描述提取需求列表"""
        return self.requirement_parser.parse_requirements(self.description)

    def generate_execution_plan(self, scenario: str = "0-1") -> str:
        """生成分阶段执行路线图（支持 0-1 / 1-N+1）"""
        requirements = self.extract_requirements()
        phases = self.requirement_parser.build_execution_phases(scenario, requirements)

        lines = [
            f"# {self.name} - 执行路线图",
            "",
            f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> **场景**: {scenario}",
            "> **策略**: 先前端可视化，再系统能力闭环",
            "",
            "---",
            "",
            "## 1. 需求范围",
            "",
            "| 模块 | 需求 | 说明 |",
            "|:---|:---|:---|",
        ]

        for req in requirements:
            lines.append(
                f"| {req.get('spec_name', 'core')} | {req.get('req_name', 'n/a')} | {req.get('description', '')} |"
            )

        lines.extend(
            [
                "",
                "## 2. 分阶段计划",
                "",
            ]
        )

        for idx, phase in enumerate(phases, 1):
            lines.extend(
                [
                    f"### Phase {idx}: {phase['title']}",
                    "",
                    f"**目标**: {phase['objective']}",
                    "",
                    "**交付物**:",
                ]
            )
            for item in phase["deliverables"]:
                lines.append(f"- {item}")
            lines.append("")

        lines.extend(
            [
                "## 3. 风险与控制",
                "",
                "- 需求漂移: 每个 Phase 完成后冻结版本并复核。",
                "- 前后端脱节: 在 Phase 2 开始前产出 API 契约草案。",
                "- 质量不足: 每个阶段结束前执行红队审查和质量门禁。",
                "",
                "## 4. 完成定义",
                "",
                "- 所有核心需求存在可验收场景并被实现。",
                "- 前端模块与文档一致，关键链路可演示。",
                "- 质量门禁通过，具备交付上线条件。",
                "",
            ]
        )

        return "\n".join(lines)

    def generate_frontend_blueprint(self) -> str:
        """生成前端先行的模块蓝图"""
        requirements = self.extract_requirements()
        modules = self.requirement_parser.build_frontend_modules(requirements)

        lines = [
            f"# {self.name} - 前端蓝图",
            "",
            f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> **前端框架**: {self.frontend}",
            "> **设计重点**: 先可视化业务流程，再补齐系统深度能力",
            "",
            "---",
            "",
            "## 1. 体验目标",
            "",
            "- 一次进入即可理解产品价值和关键流程。",
            "- 文档和执行状态可追踪，避免信息散落。",
            "- 关键任务路径操作链路最短、反馈明确。",
            "",
            "## 2. 模块拆分",
            "",
        ]

        for index, module in enumerate(modules, 1):
            lines.extend(
                [
                    f"### {index}. {module['name']}",
                    "",
                    f"**目标**: {module['goal']}",
                    "",
                    "**核心元素**:",
                ]
            )
            for element in module["core_elements"]:
                lines.append(f"- {element}")
            lines.append("")

        lines.extend(
            [
                "## 3. 开发顺序",
                "",
                "1. 先实现 `需求总览面板` + `文档工作台`，确保信息结构完整。",
                "2. 再实现业务模块页面，覆盖每条核心需求的主路径。",
                "3. 最后统一交互细节、动效和可访问性。",
                "",
                "## 4. 前后端契约建议",
                "",
                "- 页面只消费稳定 DTO，避免直接绑定数据库结构。",
                "- API 响应必须包含状态码、业务码和可读错误信息。",
                "- 对列表页统一分页/筛选参数结构，减少重复实现。",
                "",
            ]
        )

        return "\n".join(lines)

    def _generate_market_context(self) -> str:
        return (
            f"- 当前需求聚焦于“{self.description}”，在立项阶段必须先完成同类产品研究，避免凭空定义需求。\n"
            "- 研究输出至少覆盖：目标用户、核心功能组合、关键任务路径、页面层级、商业化表达与差异化方向。\n"
            "- PRD 不只描述“要做什么”，还需要明确“为什么这样做”以及“相较同类产品借鉴了什么、舍弃了什么”。\n"
            "- 对标研究更应关注流程、交互密度、信任表达和交付成熟度，而不是只模仿视觉表面。"
        )

    def _generate_user_segment_matrix(self) -> str:
        return (
            "| 用户分层 | 主要目标 | 关键诉求 | 设计重点 |\n"
            "|:---|:---|:---|:---|\n"
            "| 核心操作者 | 高效完成主流程 | 速度、稳定性、可追踪 | 缩短操作路径、强化状态反馈 |\n"
            "| 协作/审批角色 | 快速理解上下文并做决策 | 信息完整、风险可见 | 强化摘要、差异对比、审批反馈 |\n"
            "| 管理角色 | 掌握全局进度与质量 | 透明度、可审计性 | 仪表盘、过滤、导出、审计记录 |\n"
            "| 新用户/访客 | 理解产品价值与使用方式 | 上手门槛低、信任感强 | 首屏表达清晰、引导明确、案例可信 |"
        )

    def _generate_scope_priorities(self) -> str:
        return (
            "1. **P0 必做**: 主业务流程、关键页面、权限与状态闭环、错误处理、基础审计与测试。\n"
            "2. **P1 应做**: 搜索筛选、批量操作、运营/管理视图、埋点、性能优化、可观测性。\n"
            "3. **P2 可延后**: 高级自动化、复杂可视化、生态集成、个性化配置。\n"
            "4. **明确不在 MVP**: 任何没有用户价值验证、没有交付必要性的炫技功能不进入第一阶段。"
        )

    def _generate_edge_cases(self) -> str:
        return (
            "- 权限不足时必须提供可读解释与引导动作，而不是静默失败。\n"
            "- 异步任务、长流程、批量操作必须可见进度、可取消、可重试。\n"
            "- 网络异常、数据为空、外部依赖不可用时，页面需保留结构稳定和恢复路径。\n"
            "- 表单提交、发布、删除、审批等高风险动作必须有二次确认、撤回或审计记录。"
        )

    def _generate_delivery_requirements(self) -> str:
        return (
            "- 所有核心页面必须覆盖正常态、加载态、空态、错误态、禁用态和权限态。\n"
            "- 交付包必须可审计，文档、Spec、任务状态、测试结果与发布配置需要相互对应。\n"
            "- 前端先行，但不能只做静态壳子，至少要能演示真实任务流和关键反馈。\n"
            "- UI 必须达到商业产品完成度：有品牌感、信息层级、组件一致性和可访问性。"
        )

    def _generate_acceptance_matrix(self) -> str:
        return (
            "| 验收维度 | 必达标准 | 验证方式 |\n"
            "|:---|:---|:---|\n"
            "| 核心业务流程 | 主路径可从开始走到完成，且反馈明确 | 手测 + E2E |\n"
            "| 权限与审计 | 角色权限生效，关键动作可追踪 | 用例测试 + 日志核验 |\n"
            "| UI/UX 完成度 | 页面层级清晰、状态齐全、品牌感一致 | 设计走查 |\n"
            "| 工程质量 | Lint/Test/Build 通过 | CI + 本地验证 |\n"
            "| 上线准备 | 配置、监控、回滚说明齐备 | 发布检查单 |"
        )

    def _generate_business_kpis(self) -> str:
        return (
            "- **激活指标**: 首次完成核心流程的用户占比。\n"
            "- **效率指标**: 用户完成关键任务所需时间、步骤数与中断率。\n"
            "- **质量指标**: 错误率、异常恢复率、关键页面交互成功率。\n"
            "- **经营指标**: 试用到付费、线索到转化、复购或活跃留存。"
        )

    def _generate_launch_dependencies(self) -> str:
        return (
            "- 研究报告、PRD、架构、UIUX 与 tasks.md 版本一致。\n"
            "- 测试、质量门禁、发布配置、监控告警和回滚策略已验证。\n"
            "- 数据结构与迁移脚本已评审，关键风险有兜底方案。\n"
            "- 核心路径可现场演示，不依赖口头解释才能成立。"
        )

    def _generate_architecture_fit(self) -> str:
        return (
            "- 架构设计必须回到研究报告和 PRD 的关键流程，不能脱离实际需求做空泛微服务模板。\n"
            "- 技术选型应优先服务于当前阶段交付速度、稳定性、可维护性和团队认知成本。\n"
            "- 对高频路径优先做低延迟设计，对高风险路径优先做权限、审计、幂等和回滚设计。\n"
            "- 前后端契约应围绕页面与任务流定义，而不是围绕数据库表结构反推。"
        )

    def _generate_domain_boundaries(self) -> str:
        return (
            "- 认证授权、用户与组织、核心业务流程、通知与异步任务、审计日志应作为明确边界拆分。\n"
            "- 每个边界需要定义输入输出 DTO、权限要求、状态流转与失败补偿策略。\n"
            "- 共享能力只沉淀稳定基础设施，不把业务细节塞进“common utils”。\n"
            "- 高变化模块优先与低变化模块解耦，降低后续迭代成本。"
        )

    def _generate_integration_contracts(self) -> str:
        return (
            "- API 必须有版本策略，避免前端页面被无意破坏。\n"
            "- 外部依赖需定义超时、重试、降级、熔断与错误映射规则。\n"
            "- DTO 应稳定、可验证、可测试，避免把数据库内部字段直接暴露给前端。\n"
            "- Webhook、消息、回调类接口要有幂等键与审计记录。"
        )

    def _generate_failure_strategy(self) -> str:
        return (
            "- 关键写操作采用幂等机制，防止重复提交。\n"
            "- 第三方依赖异常时优先降级核心功能而不是整体瘫痪。\n"
            "- 任务流中断后应支持恢复、补偿或人工处理入口。\n"
            "- 前端异常要给出可执行的下一步，不允许只显示技术报错。"
        )

    def _generate_audit_strategy(self) -> str:
        return (
            "- 对登录、权限变更、关键数据修改、批量操作、发布/审批动作保留审计轨迹。\n"
            "- 日志结构需支持按用户、资源、请求链路、时间窗口检索。\n"
            "- 前后端共享 trace/request id，确保问题能跨层定位。\n"
            "- 质量门禁输出应沉淀为可回溯产物，而不是一次性终端信息。"
        )

    def _generate_release_strategy(self) -> str:
        return (
            "- 使用分环境发布策略，至少区分本地、测试、预发布、生产。\n"
            "- 高风险变更建议灰度、特性开关或分批发布。\n"
            "- 发布说明需包含数据库变更、兼容性影响、回滚步骤与监控关注项。\n"
            "- 回滚方案必须在上线前验证，不接受“出问题再看”。"
        )

    def _generate_ui_strategy(self, profile: dict | None = None) -> str:
        profile = profile or self._get_ui_intelligence()
        return (
            "- UI 的首要目标不是“好看”，而是让用户快速理解产品价值、任务状态与下一步动作。\n"
            "- 所有页面都应体现商业级完成度：品牌感、层级感、信息密度、状态完整度与信任表达。\n"
            f"- 当前项目应以“{profile['surface']}”为第一交付目标，并采用 {profile['information_density']} 密度策略组织信息。\n"
            "- 先解决页面结构、CTA、数据层级和组件一致性，再打磨视觉细节。\n"
            "- 对外页面强调品牌、信任与转化，对内页面强调效率、清晰度和低认知负担。"
        )

    def _generate_visual_direction(self) -> str:
        return (
            "- 视觉方向应基于产品定位建立明确气质：可信、克制、现代，而不是依赖泛滥渐变制造“高级感”。\n"
            "- 优先使用有辨识度的字体组合、清晰的字号节奏、稳定的留白和克制的强调色。\n"
            "- 图形、图标、插画、卡片阴影和分隔线应来自同一视觉系统，避免拼装感。\n"
            "- 页面应在首屏就体现主价值、核心证据、下一步 CTA 和品牌记忆点。"
        )

    def _generate_layout_system(self, profile: dict | None = None) -> str:
        profile = profile or self._get_ui_intelligence()
        return (
            "- 桌面端使用明确的 12 栏或等价栅格系统，控制内容宽度与节奏。\n"
            f"- 当前项目采用 {profile['information_density']} 信息密度，按页面目标决定视觉节奏与操作密度。\n"
            "- 控制不同页面的密度等级，避免同一产品里既过空又过挤。\n"
            "- 侧边栏、头部、主体区、辅助区、底部应有稳定布局规则。"
        )

    def _generate_component_state_matrix(self) -> str:
        return (
            "| 组件类型 | 必备状态 | 说明 |\n"
            "|:---|:---|:---|\n"
            "| 按钮 | 默认 / hover / active / disabled / loading | 强调动作反馈与禁用原因 |\n"
            "| 输入控件 | 默认 / focus / error / success / readonly | 错误文案与引导动作要清晰 |\n"
            "| 列表与表格 | loading / empty / normal / error / bulk-selected | 支持筛选、排序、批量动作 |\n"
            "| 卡片与模块 | default / hover / selected / warning / permission-limited | 用于强调优先级、状态变化和权限边界 |\n"
            "| 弹窗抽屉 | enter / exit / confirm / pending / failure | 需要防误操作和恢复路径 |"
        )

    def _generate_motion_system(self, profile: dict | None = None) -> str:
        profile = profile or self._get_ui_intelligence()
        return (
            "- 动效只服务于层级切换、状态反馈、焦点引导，不用作廉价装饰。\n"
            f"- 推荐实现基线: {profile['component_stack']['motion']}。\n"
            "- 列表进入、面板展开、Toast 反馈、模态切换应采用统一时长与缓动曲线。\n"
            "- 对关键提交动作提供即时反馈，对长操作提供进度提示。\n"
            "- 必须兼容 reduced-motion，必要时降级为无动画但保留状态反馈。"
        )

    def _generate_trust_and_conversion_rules(self, profile: dict | None = None) -> str:
        profile = profile or self._get_ui_intelligence()
        lines = [
            "- 对外页面应优先展示价值主张、能力边界、案例证明、客户证言、数据指标或合规信息。",
            "- CTA 不应只在 hero 区出现，关键转化节点要有连续但不过度打扰的引导。",
            "- 对内工作台则应突出当前任务、风险提示、审批状态、待办优先级和最近操作。",
            "- 所有高价值页面都应体现“用户为什么相信并继续使用这个产品”。",
            "",
            "**当前项目必须优先出现的信任/转化模块**:",
        ]
        lines.extend(f"- {item}" for item in profile["trust_modules"][:8])
        return "\n".join(lines)
