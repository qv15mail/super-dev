"""
代码审查指南生成器 - 生成项目特定的代码审查清单

开发：Excellent（11964948@qq.com）
功能：生成针对项目的代码审查指南和清单
作用：开发过程中和开发后进行代码审查
创建时间：2025-12-30
"""

from pathlib import Path


class CodeReviewGenerator:
    """代码审查指南生成器"""

    def __init__(self, project_dir: Path, name: str, tech_stack: dict):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack
        self.platform = tech_stack.get("platform", "web")
        self.frontend = tech_stack.get("frontend", "react")
        self.backend = tech_stack.get("backend", "node")
        self.domain = tech_stack.get("domain", "")

    def generate(self) -> str:
        """生成代码审查指南"""
        review_guide = f"""# {self.name} - 代码审查指南

> **生成时间**: 自动生成
> **技术栈**: 前端 {self.frontend} | 后端 {self.backend} | 平台 {self.platform}

---

## 审查流程

### 第 1 步: 自动化检查
运行以下命令，确保所有检查通过：

```bash
# Linter
npm run lint  # 或 python -m pylint .

# 类型检查
npm run type-check  # 或 mypy .

# 格式检查
npm run format:check  # 或 black --check .

# 测试
npm test  # 或 pytest
```

### 第 2 步: 功能审查
- [ ] 代码实现了需求中的所有功能
- [ ] 边界条件处理正确
- [ ] 错误处理完善
- [ ] 日志记录恰当

### 第 3 步: 安全审查
- [ ] 输入验证完整
- [ ] 输出编码正确
- [ ] 认证授权正确实现
- [ ] 敏感数据已保护

### 第 4 步: 性能审查
- [ ] 无明显性能问题
- [ ] 数据库查询优化
- [ ] 缓存使用恰当
- [ ] 资源使用合理

---

## 通用审查项

### 代码质量

**命名规范:**
- [ ] 变量/函数命名清晰，见名知意
- [ ] 类名使用 PascalCase
- [ ] 函数名使用 camelCase (前端) 或 snake_case (后端)
- [ ] 常量使用 SCREAMING_SNAKE_CASE
- [ ] 布尔值使用 is/has/should 前缀

**函数设计:**
- [ ] 函数职责单一，不超过 50 行
- [ ] 参数数量合理 (不超过 5 个)
- [ ] 避免深层嵌套 (不超过 3 层)
- [ ] 返回值类型一致
- [ ] 无重复代码 (DRY 原则)

**错误处理:**
- [ ] 所有异常被捕获
- [ ] 错误信息清晰有用
- [ ] 不吞掉异常
- [ ] 资源正确释放 (使用 try-finally 或 with)
- [ ] 不返回 `null`/`None` 给前端 (使用统一错误响应)

**注释和文档:**
- [ ] 复杂逻辑有注释说明
- [ ] 公共 API 有文档注释
- [ ] TODO 注释有跟踪 issue
- [ ] 注释与代码保持一致

### 安全性

**输入验证:**
- [ ] 所有用户输入验证
- [ ] 验证类型、长度、格式
- [ ] 使用白名单而非黑名单
- [ ] SQL/命令注入防护 (使用参数化查询)

**认证授权:**
- [ ] 敏感操作需要认证
- [ ] 权限检查正确
- [ ] Token/Session 有效期合理
- [ ] HTTPS 强制使用

**数据保护:**
- [ ] 密码使用强哈希 (bcrypt/Argon2)
- [ ] 敏感数据不记录到日志
- [ ] 敏感数据不暴露给前端
- [ ] 加密存储敏感配置

### 性能

**数据库:**
- [ ] 查询使用索引
- [ ] 避免全列查询（优先明确列名）
- [ ] 避免 N+1 查询
- [ ] 使用连接池
- [ ] 分页大数据集

**API:**
- [ ] 响应大小合理
- [ ] 实施缓存策略
- [ ] 异步处理耗时操作
- [ ] 实施速率限制

**前端:**
- [ ] 避免不必要的重渲染
- [ ] 使用 React.memo/useMemo/useCallback
- [ ] 懒加载路由和组件
- [ ] 图片优化和懒加载

### 测试

**单元测试:**
- [ ] 核心逻辑有单元测试
- [ ] 测试覆盖率 > 80%
- [ ] 边界条件有测试
- [ ] 错误情况有测试

**集成测试:**
- [ ] API 端点有集成测试
- [ ] 关键流程有测试
- [ ] 数据库操作有测试

---

## 前端特定审查 ({self.frontend.upper()})

{self._generate_frontend_review()}

---

## 后端特定审查 ({self.backend.upper()})

{self._generate_backend_review()}

---

## 领域特定审查 ({self.domain.upper() if self.domain else "通用"})

{self._generate_domain_review()}

---

## 审查清单模板

### Pull Request 审查清单

**提交前自检:**
- [ ] 代码符合团队规范
- [ ] Linter 无错误
- [ ] 所有测试通过
- [ ] 新增代码有测试
- [ ] 文档已更新

**Reviewers 检查:**
- [ ] 代码逻辑正确
- [ ] 无安全漏洞
- [ ] 无性能问题
- [ ] 错误处理完善
- [ ] 代码可维护

---

## 常见问题检查表

### 1. 空值处理
- [ ] 使用可选链 `?.` 访问属性
- [ ] 使用空值合并 `??` 提供默认值
- [ ] 函数参数验证空值
- [ ] 数据库查询结果检查空值

### 2. 异步处理
- [ ] async/await 正确使用
- [ ] Promise/异常正确处理
- [ ] 并发控制合理
- [ ] 超时处理设置

### 3. 资源管理
- [ ] 文件句柄正确关闭
- [ ] 数据库连接释放
- [ ] 订阅/监听器清理
- [ ] 定时器清理

### 4. 状态管理
- [ ] 状态不可变修改
- [ ] 状态更新正确
- [ ] 副作用隔离
- [ ] 状态持久化合理

---

## 审查工具

### 推荐工具

**前端 ({self.frontend}):**
- ESLint - 代码检查
- Prettier - 代码格式化
- TypeScript - 类型检查
- Jest - 单元测试

**后端 ({self.backend}):**
- pylint/flake8 - 代码检查
- black/autopep8 - 代码格式化
- mypy - 类型检查 (Python)
- pytest - 单元测试

### CI/CD 集成

在 CI 流水线中自动运行以下检查：

```yaml
# .github/workflows/review.yml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint
        run: npm run lint
      - name: Type Check
        run: npm run type-check
      - name: Test
        run: npm test -- --coverage
      - name: Security Scan
        run: npm audit
```

---

## 审查反馈模板

### 建设性反馈

**示例:**

> 我注意到在 `UserService.ts:45` 中，直接使用了 `user.email` 而没有检查 `user` 是否为 `null`。这可能导致运行时错误。
>
> 建议: 使用可选链 `user?.email` 或在函数开始时验证参数。
>
> 参考: https://github.com/our-team/frontend-handbook/blob/main/null-safety.md

### 需要修改的反馈

**示例:**

> [需要修改] 在 `AuthController.java:123` 中，SQL 查询使用了字符串拼接，存在 SQL 注入风险。
>
> 请修改为参数化查询:
> ```java
> // 错误：通过字符串拼接构造数据库查询语句
> String query = buildQueryByConcat(email);
>
> // 正确：使用参数占位符并绑定参数
> String query = buildPreparedQueryWithParams(email);
> ```
>
> 参考: OWASP SQL Injection Prevention Cheat Sheet

---

## 审查完成后

### 通过审查
- [ ] 批准并合并 PR
- [ ] 感谢贡献者
- [ ] 更新相关文档

### 需要修改
- [ ] 在 PR 中留下具体反馈
- [ ] 标注需要修改的文件和行号
- [ ] 提供修改建议和参考资料
- [ ] 设置修改后的截止时间

---

## 附录: 代码审查最佳实践

1. **及时响应**: 收到审查请求后 24 小时内完成审查
2. **建设性反馈**: 提供具体、可操作的改进建议
3. **尊重贡献者**: 评论针对代码而非个人
4. **讨论复杂问题**: 面对面或视频会议讨论
5. **持续学习**: 分享审查中学到的经验
"""
        return review_guide  # nosec B608

    def _generate_frontend_review(self) -> str:
        """生成前端特定审查内容"""
        if self.frontend == "react":
            return """
**React 特定:**
- [ ] 组件拆分合理 (不超过 200 行)
- [ ] Props 类型定义完整 (TypeScript/PropTypes)
- [ ] State 使用恰当 (useState/useReducer)
- [ ] Effect 依赖正确 (useEffect)
- [ ] Context 使用合理 (避免过度使用)
- [ ] 性能优化 (memo/useMemo/useCallback)
- [ ] Key 属性正确 (列表渲染)
- [ ] 事件处理函数稳定 (useCallback)

**Hooks 使用:**
- [ ] 自定义 Hook 可复用
- [ ] Hook 规则遵守 (只在顶层调用)
- [ ] Effect 依赖数组完整
- [ ] 清理函数正确返回

**状态管理:**
- [ ] 全局状态使用 Redux/Zustand
- [ ] 本地状态使用 useState
- [ ] 表单状态使用 Form 库
- [ ] 服务端状态使用 React Query/SWR
"""
        elif self.frontend == "vue":
            return """
**Vue 特定:**
- [ ] 组件拆分合理 (不超过 200 行)
- [ ] Props 类型定义完整
- [ ] Emits 事件声明完整
- [ ] Computed 使用恰当
- [ ] Watch 使用合理
- [ ] 生命周期钩子正确
- [ ] Ref/Reactive 使用正确

**Composition API:**
- [ ] `<script setup>` 语法使用
- [ ] Composable 函数可复用
- [ ] 响应式类型正确 (ref/reactive)
- [ ] 生命周期使用正确

**状态管理:**
- [ ] 全局状态使用 Pinia
- [ ] 本地状态使用 reactive/ref
- [ ] 表单状态使用 Form 库
"""
        else:
            return """
**通用前端:**
- [ ] 组件拆分合理
- [ ] Props 类型定义
- [ ] 状态管理清晰
- [ ] 事件处理正确
- [ ] 样式隔离良好
"""

    def _generate_backend_review(self) -> str:
        """生成后端特定审查内容"""
        if self.backend == "node":
            return """
**Node.js 特定:**
- [ ] 异步错误处理 (try-catch)
- [ ] Promise 正确使用
- [ ] 内存泄漏检查 (监听器清理)
- [ ] 依赖安全 (npm audit)
- [ ] 环境变量管理 (.env)
- [ ] 中间件顺序正确
- [ ] 请求体验证

**Express/NestJS:**
- [ ] 路由命名规范 (RESTful)
- [ ] 中间件职责单一
- [ ] 错误处理中间件
- [ ] 请求验证 (express-validator/class-validator)
- [ ] 响应格式统一
"""
        elif self.backend == "python":
            return """
**Python 特定:**
- [ ] 类型提示完整 (Type Hints)
- [ ] 异常处理具体
- [ ] 资源清理 (with 语句)
- [ ] 依赖安全 (pip audit)
- [ ] 虚拟环境使用
- [ ] PEP 8 规范遵守

**FastAPI/Django:**
- [ ] Pydantic 模型验证
- [ ] 路由命名规范 (RESTful)
- [ ] 中间件/装饰器使用
- [ ] 数据库会话管理
- [ ] 响应格式统一
"""
        else:
            return """
**通用后端:**
- [ ] API 设计 RESTful
- [ ] 请求验证完整
- [ ] 错误处理统一
- [ ] 日志记录恰当
- [ ] 依赖注入使用
"""

    def _generate_domain_review(self) -> str:
        """生成领域特定审查内容"""
        if self.domain == "fintech":
            return """
**金融领域特定:**
- [ ] 金额计算使用 Decimal 类型
- [ ] 货币转换正确
- [ ] 交易原子性保证
- [ ] 审计日志完整
- [ ] 合规性检查 (PCI-DSS)
- [ ] 敏感数据加密
- [ ] 防重放攻击
- [ ] 幂等性保证
"""
        elif self.domain == "medical":
            return """
**医疗领域特定:**
- [ ] HIPAA 合规性
- [ ] 患者隐私保护
- [ ] 数据加密存储
- [ ] 访问控制严格
- [ ] 审计日志完整
- [ ] 数据脱敏展示
- [ ] 紧急访问机制
"""
        elif self.domain == "ecommerce":
            return """
**电商领域特定:**
- [ ] 库存并发控制
- [ ] 订单幂等性
- [ ] 支付安全
- [ ] 价格精度处理
- [ ] 优惠券逻辑
- [ ] 促销规则验证
"""
        else:
            return """
**通用领域:**
- [ ] 业务规则正确
- [ ] 数据一致性
- [ ] 事务处理合理
- [ ] 幂等性保证
"""
