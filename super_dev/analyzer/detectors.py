"""
Super Dev 项目类型检测器
"""

import json
import re
from pathlib import Path

# 尝试导入 TOML 解析库
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ImportError:
        tomllib = None

from .models import (
    ArchitecturePattern,
    Dependency,
    FrameworkType,
    ProjectCategory,
    TechStack,
)


def detect_project_type(project_path: Path) -> ProjectCategory:
    """
    检测项目类型

    Args:
        project_path: 项目根目录路径

    Returns:
        ProjectCategory: 项目类型
    """
    project_path = Path(project_path).resolve()

    # 检查关键文件
    package_json = project_path / "package.json"
    requirements_txt = project_path / "requirements.txt"
    pyproject_toml = project_path / "pyproject.toml"
    go_mod = project_path / "go.mod"
    cargo_toml = project_path / "Cargo.toml"
    pom_xml = project_path / "pom.xml"
    build_gradle = project_path / "build.gradle"
    gemfile = project_path / "Gemfile"
    composer_json = project_path / "composer.json"

    # 检测前后端项目
    if package_json.exists():
        return _detect_node_project_type(project_path)

    if requirements_txt.exists() or pyproject_toml.exists():
        return _detect_python_project_type(project_path)

    if go_mod.exists():
        return ProjectCategory.BACKEND

    if cargo_toml.exists():
        return ProjectCategory.BACKEND

    if pom_xml.exists() or build_gradle.exists():
        return ProjectCategory.BACKEND

    if gemfile.exists():
        return ProjectCategory.BACKEND

    if composer_json.exists():
        # 可能是前端或后端
        return _detect_php_project_type(project_path)

    # 检查是否有 Android/iOS 项目
    if (project_path / "android").exists() or (project_path / "ios").exists():
        return ProjectCategory.MOBILE

    # 检查 Electron 项目
    if package_json.exists():
        try:
            with open(package_json, encoding="utf-8") as f:
                data = json.load(f)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})

                if "electron" in deps or "electron" in dev_deps:
                    return ProjectCategory.DESKTOP
        except (OSError, json.JSONDecodeError):
            pass

    return ProjectCategory.UNKNOWN


def _detect_node_project_type(project_path: Path) -> ProjectCategory:
    """检测 Node.js 项目类型"""
    package_json = project_path / "package.json"

    try:
        with open(package_json, encoding="utf-8") as f:
            data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})

            all_deps = {**deps, **dev_deps}

            # 检测前端框架
            frontend_frameworks = [
                "react", "react-dom", "vue", "vue-router", "@angular/core",
                "angular", "svelte", "next", "nuxt", "@remix-run/react",
            ]

            has_frontend = any(fw in all_deps for fw in frontend_frameworks)

            # 检测后端框架
            backend_frameworks = [
                "express", "fastify", "koa", "nest", "@nestjs/common",
                "hapi", "feathers", "socket.io",
            ]

            has_backend = any(bw in all_deps for bw in backend_frameworks)

            if has_frontend and has_backend:
                return ProjectCategory.FULLSTACK
            elif has_frontend:
                return ProjectCategory.FRONTEND
            elif has_backend:
                return ProjectCategory.BACKEND

            # 检查是否是 serverless
            if "serverless" in all_deps or "aws-lambda" in all_deps:
                return ProjectCategory.SERVERLESS

            return ProjectCategory.BACKEND  # 默认为后端

    except (OSError, json.JSONDecodeError):
        return ProjectCategory.UNKNOWN


def _detect_python_project_type(project_path: Path) -> ProjectCategory:
    """检测 Python 项目类型"""
    requirements_txt = project_path / "requirements.txt"
    pyproject_toml = project_path / "pyproject.toml"

    dependencies = set()

    if requirements_txt.exists():
        try:
            with open(requirements_txt, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # 提取包名
                        match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                        if match:
                            dependencies.add(match.group(1).lower())
        except OSError:
            pass

    if pyproject_toml.exists() and tomllib is not None:
        try:
            with open(pyproject_toml, "rb") as f:
                data = tomllib.load(f)
                deps = data.get("project", {}).get("dependencies", [])
                dependencies.update(d.lower().split(">=")[0].split("==")[0] for d in deps)
        except Exception:
            dependencies.update(set())

    # 检测 Web 框架
    web_frameworks = {
        "django", "flask", "fastapi", "starlette", "tornado",
        "aiohttp", "sanic", "quart",
    }

    has_web = any(fw in dependencies for fw in web_frameworks)

    # 检测前端相关
    frontend_related = {
        "webpack", "vite", "rollup", "parcel",
        "react", "vue", "angular",
    }

    has_frontend = any(fr in dependencies for fr in frontend_related)

    if has_frontend and has_web:
        return ProjectCategory.FULLSTACK
    elif has_web:
        return ProjectCategory.BACKEND

    return ProjectCategory.BACKEND


def _detect_php_project_type(project_path: Path) -> ProjectCategory:
    """检测 PHP 项目类型"""
    composer_json = project_path / "composer.json"

    try:
        with open(composer_json, encoding="utf-8") as f:
            data = json.load(f)
            deps = data.get("require", {})

            # Laravel/Symfony 等通常是后端
            if any(fw in deps for fw in ["laravel/framework", "symfony/http-kernel"]):
                return ProjectCategory.BACKEND

    except (OSError, json.JSONDecodeError):
        pass

    return ProjectCategory.BACKEND


def detect_tech_stack(project_path: Path) -> TechStack:
    """
    检测技术栈

    Args:
        project_path: 项目根目录路径

    Returns:
        TechStack: 技术栈信息
    """
    project_path = Path(project_path).resolve()
    category = detect_project_type(project_path)

    package_json = project_path / "package.json"
    requirements_txt = project_path / "requirements.txt"
    pyproject_toml = project_path / "pyproject.toml"
    go_mod = project_path / "go.mod"

    # Node.js 项目
    if package_json.exists():
        return _detect_node_tech_stack(project_path, category)

    # Python 项目
    if requirements_txt.exists() or pyproject_toml.exists():
        return _detect_python_tech_stack(project_path, category)

    # Go 项目
    if go_mod.exists():
        return _detect_go_tech_stack(project_path, category)

    # 默认返回
    return TechStack(
        category=category,
        language="unknown",
        framework=FrameworkType.UNKNOWN,
    )


def _detect_node_tech_stack(project_path: Path, category: ProjectCategory) -> TechStack:
    """检测 Node.js 技术栈"""
    package_json = project_path / "package.json"

    try:
        with open(package_json, encoding="utf-8") as f:
            data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})

            all_deps = {**deps, **dev_deps}

            # 检测框架
            framework = FrameworkType.UNKNOWN
            if "next" in all_deps:
                framework = FrameworkType.NEXTJS
            elif "nuxt" in all_deps:
                framework = FrameworkType.NUXT
            elif "@remix-run/react" in all_deps:
                framework = FrameworkType.REMIX
            elif "react" in all_deps or "react-dom" in all_deps:
                framework = FrameworkType.REACT
            elif "vue" in all_deps:
                framework = FrameworkType.VUE
            elif "@angular/core" in all_deps or "angular" in all_deps:
                framework = FrameworkType.ANGULAR
            elif "svelte" in all_deps:
                framework = FrameworkType.SVELTE
            elif "express" in all_deps:
                framework = FrameworkType.EXPRESS

            # 检测 UI 库
            ui_library = ""
            ui_libraries = [
                "@mui/material", "@chakra-ui/react", "@mantine/core",
                "antd", "react-bootstrap", "tailwindcss",
                "element-plus", "vuetify", "antd-mobile",
            ]
            for lib in ui_libraries:
                if lib in all_deps:
                    ui_library = lib
                    break

            # 检测状态管理
            state_management = ""
            state_libs = [
                "redux", "@reduxjs/toolkit", "zustand", "jotai",
                "recoil", "mobx", "pinia", "vuex",
            ]
            for lib in state_libs:
                if lib in all_deps:
                    state_management = lib
                    break

            # 检测构建工具
            build_tool = ""
            build_tools = [
                "vite", "webpack", "rollup", "parcel",
                "esbuild", "turbo",
            ]
            for tool in build_tools:
                if tool in all_deps:
                    build_tool = tool
                    break

            # 检测测试框架
            testing_framework = ""
            test_frameworks = [
                "jest", "vitest", "@testing-library/react",
                "mocha", "chai", "jasmine",
            ]
            for fw in test_frameworks:
                if fw in all_deps:
                    testing_framework = fw
                    break

            # 解析依赖
            dependencies = []
            for name, version in deps.items():
                dependencies.append(
                    Dependency(
                        name=name,
                        version=str(version),
                        type="prod",
                    )
                )

            return TechStack(
                category=category,
                language="javascript" if framework != FrameworkType.NEXTJS else "typescript",
                framework=framework,
                ui_library=ui_library,
                state_management=state_management,
                build_tool=build_tool,
                testing_framework=testing_framework,
                dependencies=dependencies,
            )

    except (OSError, json.JSONDecodeError):
        return TechStack(
            category=category,
            language="javascript",
            framework=FrameworkType.UNKNOWN,
        )


def _detect_python_tech_stack(project_path: Path, category: ProjectCategory) -> TechStack:
    """检测 Python 技术栈"""
    requirements_txt = project_path / "requirements.txt"

    dependencies = []
    framework = FrameworkType.UNKNOWN
    testing_framework = ""

    # 解析依赖
    if requirements_txt.exists():
        try:
            with open(requirements_txt, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # 解析 requirement
                        match = re.match(r"^([a-zA-Z0-9_-]+)([>=<~]+(.+))?", line)
                        if match:
                            name = match.group(1)
                            version = match.group(3) or ""
                            dependencies.append(
                                Dependency(
                                    name=name,
                                    version=version,
                                    type="prod",
                                )
                            )
        except OSError:
            pass

    # 检测框架
    dep_names = {d.name.lower() for d in dependencies}

    if "django" in dep_names:
        framework = FrameworkType.DJANGO
    elif "fastapi" in dep_names:
        framework = FrameworkType.FASTAPI
    elif "flask" in dep_names:
        framework = FrameworkType.FLASK

    # 检测测试框架
    test_frameworks = ["pytest", "unittest", "nose2"]
    for fw in test_frameworks:
        if fw in dep_names:
            testing_framework = fw
            break

    return TechStack(
        category=category,
        language="python",
        framework=framework,
        testing_framework=testing_framework,
        dependencies=dependencies,
    )


def _detect_go_tech_stack(project_path: Path, category: ProjectCategory) -> TechStack:
    """检测 Go 技术栈"""
    go_mod = project_path / "go.mod"

    dependencies = []

    try:
        with open(go_mod, encoding="utf-8") as f:
            content = f.read()
            # 解析 require 部分
            require_match = re.search(r"require \((.*?)\)", content, re.DOTALL)
            if require_match:
                for line in require_match.group(1).split("\n"):
                    line = line.strip()
                    match = re.match(r"^([^\s]+)\s+([^\s]+)", line)
                    if match:
                        dependencies.append(
                            Dependency(
                                name=match.group(1),
                                version=match.group(2),
                                type="prod",
                            )
                        )

        # 检测框架
        dep_names = {d.name.lower() for d in dependencies}

        framework = FrameworkType.UNKNOWN
        if "github.com/gin-gonic/gin" in dep_names:
            framework = FrameworkType.GIN
        elif "github.com/labstack/echo/v4" in dep_names:
            framework = FrameworkType.ECHO

        return TechStack(
            category=category,
            language="go",
            framework=framework,
            dependencies=dependencies,
        )

    except OSError:
        return TechStack(
            category=category,
            language="go",
            framework=FrameworkType.UNKNOWN,
        )


def detect_architecture_pattern(project_path: Path) -> ArchitecturePattern | None:
    """
    检测架构模式

    Args:
        project_path: 项目根目录路径

    Returns:
        ArchitecturePattern | None: 架构模式
    """
    project_path = Path(project_path).resolve()
    package_json = project_path / "package.json"

    # 检查目录结构
    dirs = [d.name for d in project_path.iterdir() if d.is_dir()]

    # 微服务架构
    if "services" in dirs or "microservices" in dirs:
        return ArchitecturePattern.MICROSERVICES

    # 检查 Node.js 项目架构
    if package_json.exists():
        return _detect_node_architecture(project_path, dirs)

    # 分层架构（默认）
    if any(d in dirs for d in ["src", "lib", "app", "server"]):
        return ArchitecturePattern.LAYERED

    return None


def _detect_node_architecture(project_path: Path, dirs: list[str]) -> ArchitecturePattern | None:
    """检测 Node.js 项目架构"""
    src_dir = project_path / "src"

    if src_dir.exists():
        src_dirs = [d.name for d in src_dir.iterdir() if d.is_dir()]

        # MVC/MVVM 检测
        has_models = "models" in src_dirs or "entities" in src_dirs
        has_views = "views" in src_dirs or "components" in src_dirs
        has_controllers = "controllers" in src_dirs or "handlers" in src_dirs

        if has_models and has_views and has_controllers:
            return ArchitecturePattern.MVC

        # 整洁架构检测
        clean_arch_indicators = [
            "domain", "use-cases", "application", "infrastructure",
        ]
        if any(ind in src_dirs for ind in clean_arch_indicators):
            return ArchitecturePattern.CLEAN_ARCHITECTURE

    return ArchitecturePattern.LAYERED
