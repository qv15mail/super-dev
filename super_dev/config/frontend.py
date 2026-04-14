"""
开发：Excellent（11964948@qq.com）
功能：前端配置系统 - 商业级前端技术栈配置
作用：提供全面的前端框架、组件库、工具链配置
创建时间：2025-12-30
最后修改：2025-12-30
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FrameworkCategory(str, Enum):
    """前端框架类别"""

    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    ASTRO = "astro"
    SOLID = "solid"
    QWIK = "qwik"


class BuildTool(str, Enum):
    """构建工具"""

    VITE = "vite"
    WEBPACK = "webpack"
    ESBUILD = "esbuild"
    SWC = "swc"
    ROLLUP = "rollup"
    TURBOPACK = "turbo"


class TestingFramework(str, Enum):
    """测试框架"""

    VITEST = "vitest"
    JEST = "jest"
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    TESTING_LIBRARY = "testing-library"


class StyleSolution(str, Enum):
    """样式方案"""

    TAILWIND = "tailwind"
    CSS_MODULES = "css-modules"
    STYLED_COMPONENTS = "styled-components"
    EMOTION = "emotion"
    SCSS = "scss"
    LESS = "less"
    UNOCSS = "unocss"


class StateManagement(str, Enum):
    """状态管理"""

    # Server State
    REACT_QUERY = "react-query"
    SWR = "swr"
    VUE_QUERY = "vue-query"
    VUEUSE = "vueuse"

    # Client State
    ZUSTAND = "zustand"
    PINIA = "pinia"
    REDUX_TOOLKIT = "redux-toolkit"
    JOTAI = "jotai"
    RECOIL = "recoil"
    XSTATE = "xstate"
    VALTIO = "valtio"


# 前端框架定义
FRAMEWORKS: dict[str, dict[str, Any]] = {
    # React 生态
    "next": {
        "name": "Next.js",
        "category": FrameworkCategory.REACT,
        "description": "React 全栈框架，支持 SSR/SSG",
        "features": ["ssr", "ssg", " isr", "api-routes", "file-routing"],
        "build_tool": BuildTool.TURBOPACK,
        "recommended_for": ["seo-critical", "fullstack", "ecommerce"],
    },
    "remix": {
        "name": "Remix",
        "category": FrameworkCategory.REACT,
        "description": "专注于 Web 标准和渐进增强的 React 框架",
        "features": ["ssr", "nested-routes", "forms", "progressive-enhancement"],
        "build_tool": BuildTool.ESBUILD,
        "recommended_for": ["web-standards", "progressive-enhancement"],
    },
    "react-vite": {
        "name": "React + Vite",
        "category": FrameworkCategory.REACT,
        "description": "使用 Vite 的现代 React SPA",
        "features": ["spa", "hmr", "fast-build"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["spa", "dashboard", "admin-panel"],
    },
    "gatsby": {
        "name": "Gatsby",
        "category": FrameworkCategory.REACT,
        "description": "基于 React 的静态站点生成器",
        "features": ["ssg", "graphql", "content-aggregation"],
        "build_tool": BuildTool.WEBPACK,
        "recommended_for": ["blog", "marketing-site", "documentation"],
    },
    # Vue 生态
    "nuxt": {
        "name": "Nuxt",
        "category": FrameworkCategory.VUE,
        "description": "Vue 全栈框架，支持 SSR/SSG",
        "features": ["ssr", "ssg", "file-routing", "auto-imports"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["seo-critical", "fullstack", "universal-app"],
    },
    "vue-vite": {
        "name": "Vue + Vite",
        "category": FrameworkCategory.VUE,
        "description": "使用 Vite 的现代 Vue SPA",
        "features": ["spa", "hmr", "fast-build"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["spa", "dashboard", "admin-panel"],
    },
    # Angular
    "angular": {
        "name": "Angular",
        "category": FrameworkCategory.ANGULAR,
        "description": "Google 维护的企业级前端框架",
        "features": ["ssr", "cli", "di", "rxjs", "http-client"],
        "build_tool": BuildTool.ESBUILD,
        "recommended_for": ["enterprise", "large-scale"],
    },
    # Svelte
    "sveltekit": {
        "name": "SvelteKit",
        "category": FrameworkCategory.SVELTE,
        "description": "Svelte 全栈框架",
        "features": ["ssr", "ssg", "file-routing", "no-build-step"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["performance", "seo-critical", "universal-app"],
    },
    # 其他
    "astro": {
        "name": "Astro",
        "category": FrameworkCategory.ASTRO,
        "description": "内容优先的 Web 框架，零 JS 默认",
        "features": ["ssg", "islands", "multi-framework", "content-focused"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["blog", "documentation", "marketing", "content-site"],
    },
    "solid": {
        "name": "Solid.js",
        "category": FrameworkCategory.SOLID,
        "description": "高性能响应式库，类似 React 语法的细粒度响应式",
        "features": ["reactive", "jsx", "no-virtual-dom"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["performance-critical", "react-alternative"],
    },
    "qwik": {
        "name": "Qwik",
        "category": FrameworkCategory.QWIK,
        "description": "可_resume 的框架，极致性能优化",
        "features": ["resumable", "lazy-load-everything", "no-hydration"],
        "build_tool": BuildTool.VITE,
        "recommended_for": ["performance-critical", "edge-caching"],
    },
}

# UI 组件库
UI_LIBRARIES: dict[str, dict[str, Any]] = {
    # React 组件库
    "mui": {
        "name": "Material-UI (MUI)",
        "framework": FrameworkCategory.REACT,
        "description": "Google Material Design 实现",
        "features": ["components", "theming", "icons"],
        "bundle_size": "large",
    },
    "ant-design": {
        "name": "Ant Design",
        "framework": FrameworkCategory.REACT,
        "description": "企业级 UI 设计语言",
        "features": ["components", "templates", "pro-components"],
        "bundle_size": "large",
        "recommended_for": ["enterprise", "admin-panel"],
    },
    "chakra-ui": {
        "name": "Chakra UI",
        "framework": FrameworkCategory.REACT,
        "description": "简单、模块化、可访问的组件库",
        "features": ["components", "theming", "dark-mode", "a11y"],
        "bundle_size": "medium",
        "style": ["emotion"],
    },
    "mantine": {
        "name": "Mantine",
        "framework": FrameworkCategory.REACT,
        "description": "功能丰富的 React 组件库",
        "features": ["components", "hooks", "form", "modals"],
        "bundle_size": "medium",
        "style": ["emotion", "scss"],
    },
    "shadcn-ui": {
        "name": "shadcn/ui",
        "framework": FrameworkCategory.REACT,
        "description": "基于 Radix UI 的可复制组件",
        "features": ["components", "copy-paste", "customizable"],
        "bundle_size": "small",
        "style": ["tailwind"],
        "recommended_for": ["custom-design", "tailwind-users"],
    },
    "radix-ui": {
        "name": "Radix UI",
        "framework": FrameworkCategory.REACT,
        "description": "无样式、无障碍的原始组件",
        "features": ["a11y", "unstyled", "headless"],
        "bundle_size": "small",
        "recommended_for": ["custom-design", "a11y-critical"],
    },
    "react-aria": {
        "name": "React Aria",
        "framework": FrameworkCategory.REACT,
        "description": "Adobe 开发的无障碍组件库",
        "features": ["a11y", "internationalization", "unstyled"],
        "bundle_size": "small",
        "recommended_for": ["a11y-critical", "i18n"],
    },
    # Vue 组件库
    "element-plus": {
        "name": "Element Plus",
        "framework": FrameworkCategory.VUE,
        "description": "Vue 3 组件库",
        "features": ["components", "i18n", "theme"],
        "bundle_size": "large",
        "recommended_for": ["admin-panel", "enterprise"],
    },
    "naive-ui": {
        "name": "Naive UI",
        "framework": FrameworkCategory.VUE,
        "description": " Vue 3 组件库，TypeScript 友好",
        "features": ["components", "themes", "tree-shaking"],
        "bundle_size": "medium",
        "recommended_for": ["typescript-project"],
    },
    "vuetify": {
        "name": "Vuetify",
        "framework": FrameworkCategory.VUE,
        "description": "Material Design 组件库",
        "features": ["components", "material-design", "cli"],
        "bundle_size": "large",
        "style": ["scss"],
    },
    "primevue": {
        "name": "PrimeVue",
        "framework": FrameworkCategory.VUE,
        "description": "完整的 Vue UI 组件套件",
        "features": ["components", "themes", "icons"],
        "bundle_size": "medium",
    },
    "arco-design": {
        "name": "Arco Design",
        "framework": FrameworkCategory.VUE,
        "description": "字节跳动企业级设计系统",
        "features": ["components", "themes", "enterprise"],
        "bundle_size": "medium",
        "recommended_for": ["enterprise", "chinese-market"],
    },
    # Angular 组件库
    "angular-material": {
        "name": "Angular Material",
        "framework": FrameworkCategory.ANGULAR,
        "description": "Material Design for Angular",
        "features": ["components", "cdk", "theming"],
        "bundle_size": "medium",
    },
    "primeng": {
        "name": "PrimeNG",
        "framework": FrameworkCategory.ANGULAR,
        "description": "完整的 Angular UI 组件套件",
        "features": ["components", "themes", "templates"],
        "bundle_size": "medium",
    },
    # Svelte 组件库
    "skeleton-ui": {
        "name": "Skeleton UI",
        "framework": FrameworkCategory.SVELTE,
        "description": "Svelte 的 Tailwind CSS 组件库",
        "features": ["components", "themes", "dark-mode"],
        "bundle_size": "small",
        "style": ["tailwind"],
    },
    "svelte-material-ui": {
        "name": "Svelte Material UI",
        "framework": FrameworkCategory.SVELTE,
        "description": "Material Design for Svelte",
        "features": ["components", "material-design"],
        "bundle_size": "medium",
    },
    # 跨框架
    "tailwind": {
        "name": "Tailwind CSS",
        "framework": "any",
        "description": "实用优先的 CSS 框架",
        "features": ["utility-first", "responsive", "dark-mode"],
        "bundle_size": "small",
        "recommended_for": ["custom-design", "rapid-development"],
    },
    "daisyui": {
        "name": "DaisyUI",
        "framework": "any",
        "description": "基于 Tailwind 的组件库",
        "features": ["components", "themes", "tailwind"],
        "bundle_size": "small",
        "style": ["tailwind"],
    },
}

# 状态管理方案
STATE_MANAGEMENT_OPTIONS: dict[str, dict[str, Any]] = {
    "react-query": {
        "name": "React Query (TanStack Query)",
        "framework": FrameworkCategory.REACT,
        "type": "server-state",
        "description": "强大的服务端状态管理",
        "features": ["caching", "synchronization", "background-updates"],
        "recommended_for": ["api-heavy", "server-state"],
    },
    "swr": {
        "name": "SWR",
        "framework": FrameworkCategory.REACT,
        "type": "server-state",
        "description": "轻量级数据获取库",
        "features": ["caching", "revalidation", "stale-while-revalidate"],
        "recommended_for": ["simple-api", "lightweight"],
    },
    "zustand": {
        "name": "Zustand",
        "framework": FrameworkCategory.REACT,
        "type": "client-state",
        "description": "轻量级状态管理",
        "features": ["simple", "no-boilerplate", "devtools"],
        "recommended_for": ["client-state", "simple-store"],
    },
    "redux-toolkit": {
        "name": "Redux Toolkit",
        "framework": FrameworkCategory.REACT,
        "type": "client-state",
        "description": "Redux 官方推荐工具集",
        "features": ["immutable", "middleware", "devtools"],
        "recommended_for": ["large-scale", "complex-state"],
    },
    "jotai": {
        "name": "Jotai",
        "framework": FrameworkCategory.REACT,
        "type": "client-state",
        "description": "原始且灵活的原子状态管理",
        "features": ["atoms", "atom-families", "typescript"],
        "recommended_for": ["modular-state", "bottom-up"],
    },
    "pinia": {
        "name": "Pinia",
        "framework": FrameworkCategory.VUE,
        "type": "client-state",
        "description": "Vue 官方状态管理库",
        "features": ["composition-api", "typescript", "devtools"],
        "recommended_for": ["vue3", "typescript"],
    },
    "xstate": {
        "name": "XState",
        "framework": "any",
        "type": "client-state",
        "description": "状态机和状态图",
        "features": ["state-machines", "visualization", "actors"],
        "recommended_for": ["complex-flows", "state-machines"],
    },
}

# 测试工具
TESTING_TOOLS: dict[str, dict[str, Any]] = {
    "vitest": {
        "name": "Vitest",
        "description": "由 Vite 驱动的单元测试框架",
        "features": ["fast", "jest-compatible", "esm"],
        "recommended_for": ["unit", "vite-projects"],
    },
    "jest": {
        "name": "Jest",
        "description": "JavaScript 测试框架",
        "features": ["zero-config", "snapshot", "coverage"],
        "recommended_for": ["unit", "legacy-projects"],
    },
    "playwright": {
        "name": "Playwright",
        "description": "跨浏览器端到端测试",
        "features": ["cross-browser", "auto-waiting", "trace"],
        "recommended_for": ["e2e", "cross-browser-testing"],
    },
    "cypress": {
        "name": "Cypress",
        "description": "前端测试工具",
        "features": ["e2e", "component-testing", "time-travel"],
        "recommended_for": ["e2e", "component-testing"],
    },
    "testing-library": {
        "name": "Testing Library",
        "description": "简单且完整的 DOM 测试",
        "features": ["user-centric", "accessibility", "framework-agnostic"],
        "recommended_for": ["component", "integration"],
    },
}

# 工具链配置
DEV_TOOLS: dict[str, dict[str, Any]] = {
    "typescript": {
        "name": "TypeScript",
        "description": "JavaScript 类型系统",
        "features": ["type-checking", "intellisense", "refactoring"],
        "recommended": True,
    },
    "eslint": {
        "name": "ESLint",
        "description": "JavaScript 代码检查工具",
        "features": ["linting", "auto-fix", "plugins"],
        "recommended": True,
    },
    "prettier": {
        "name": "Prettier",
        "description": "代码格式化工具",
        "features": ["formatting", "opinionated"],
        "recommended": True,
    },
    "postcss": {
        "name": "PostCSS",
        "description": "CSS 转换工具",
        "features": ["autoprefixer", "nesting", "variables"],
        "recommended": True,
    },
}


@dataclass
class FrontendConfig:
    """前端配置"""

    # 框架
    framework: str = "next"  # 默认 Next.js
    framework_version: str = "latest"

    # UI 库
    ui_library: str | None = None
    ui_library_version: str = "latest"

    # 样式
    style_solution: list[StyleSolution] = field(default_factory=lambda: [StyleSolution.TAILWIND])

    # 状态管理
    state_management: list[StateManagement] = field(default_factory=list)

    # 构建工具
    build_tool: BuildTool | None = None

    # 测试
    testing_frameworks: list[TestingFramework] = field(default_factory=list)

    # 开发工具
    dev_tools: list[str] = field(default_factory=lambda: ["typescript", "eslint", "prettier"])

    # 性能优化
    enable_bundle_analysis: bool = True
    enable_code_splitting: bool = True
    enable_tree_shaking: bool = True
    enable_compression: bool = True

    # PWA
    enable_pwa: bool = False

    # 国际化
    enable_i18n: bool = False
    i18n_locales: list[str] = field(default_factory=lambda: ["en", "zh"])

    # 无障碍
    a11y_level: str = "aa"  # none, a, aa, aaa

    def get_framework_info(self) -> dict[str, Any]:
        """获取框架信息"""
        return FRAMEWORKS.get(self.framework, {})

    def get_ui_library_info(self) -> dict[str, Any]:
        """获取 UI 库信息"""
        if not self.ui_library:
            return {}
        return UI_LIBRARIES.get(self.ui_library, {})

    def get_recommended_stack(self) -> dict[str, Any]:
        """获取推荐的技术栈"""
        framework_info = self.get_framework_info()
        stack = {
            "framework": framework_info.get("name", self.framework),
            "build_tool": self.build_tool or framework_info.get("build_tool"),
            "recommended_for": framework_info.get("recommended_for", []),
        }

        if self.ui_library:
            ui_info = self.get_ui_library_info()
            stack["ui_library"] = ui_info.get("name", self.ui_library)

        return stack

    def validate(self) -> list[str]:
        """验证配置"""
        errors = []

        if self.framework not in FRAMEWORKS:
            errors.append(f"不支持的框架: {self.framework}")

        if self.ui_library and self.ui_library not in UI_LIBRARIES:
            errors.append(f"不支持的 UI 库: {self.ui_library}")

        framework_info = self.get_framework_info()
        if self.ui_library:
            ui_info = self.get_ui_library_info()
            framework_cat = framework_info.get("category")
            ui_framework = ui_info.get("framework")
            if ui_framework != "any" and ui_framework != framework_cat:
                errors.append(f"UI 库 {self.ui_library} 不兼容框架 {self.framework}")

        return errors


@dataclass
class MobileFrontendConfig(FrontendConfig):
    """移动端前端配置"""

    platform: str = "mobile"  # mobile, ios, android

    # 移动端框架
    mobile_framework: str = "react-native"  # react-native, flutter

    # 移动端 UI 库
    mobile_ui_library: str | None = None

    # 原生模块
    enable_native_modules: bool = False

    # 性能
    enable_hermes: bool = True  # React Native Hermes 引擎
