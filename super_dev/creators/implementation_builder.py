# -*- coding: utf-8 -*-
"""
实现骨架生成器

根据结构化需求生成前端/后端代码骨架，帮助从文档快速进入实现阶段。
"""

from __future__ import annotations

import json
from pathlib import Path


class ImplementationScaffoldBuilder:
    """项目实现骨架生成器"""

    def __init__(
        self,
        project_dir: Path,
        name: str,
        frontend: str,
        backend: str,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.frontend = frontend
        self.backend = backend

    def generate(self, requirements: list[dict]) -> dict:
        """生成前后端实现骨架"""
        result = {
            "frontend_files": [],
            "backend_files": [],
        }

        if self.frontend != "none":
            result["frontend_files"] = self._generate_frontend(requirements)

        if self.backend != "none":
            result["backend_files"] = self._generate_backend(requirements)

        return result

    def _generate_frontend(self, requirements: list[dict]) -> list[str]:
        frontend_dir = self.project_dir / "frontend"
        src_dir = frontend_dir / "src"
        modules_dir = src_dir / "modules"
        modules_dir.mkdir(parents=True, exist_ok=True)

        module_names = [req.get("spec_name", "core") for req in requirements]
        unique_modules = []
        for module_name in module_names:
            if module_name not in unique_modules:
                unique_modules.append(module_name)

        files: list[str] = []

        frontend_kind = self.frontend.lower()
        if frontend_kind == "react":
            files.extend(self._generate_react_frontend(frontend_dir, src_dir, modules_dir, unique_modules))
        elif frontend_kind == "vue":
            files.extend(self._generate_vue_frontend(frontend_dir, src_dir, modules_dir, unique_modules))
        elif frontend_kind == "svelte":
            files.extend(self._generate_svelte_frontend(frontend_dir, src_dir, modules_dir, unique_modules))
        elif frontend_kind == "angular":
            files.extend(self._generate_angular_frontend(frontend_dir, src_dir, unique_modules))
        else:
            # 默认回落到 React
            files.extend(self._generate_react_frontend(frontend_dir, src_dir, modules_dir, unique_modules))

        readme_file = frontend_dir / "README.md"
        readme_file.write_text(
            (
                "# Frontend Scaffold\n\n"
                "## Run\n\n"
                "```bash\n"
                "npm install\n"
                "npm run dev\n"
                "```\n"
            ),
            encoding="utf-8",
        )
        files.append(str(readme_file))

        return files

    def _generate_backend(self, requirements: list[dict]) -> list[str]:
        backend_dir = self.project_dir / "backend"
        src_dir = backend_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        module_names = [req.get("spec_name", "core") for req in requirements]
        unique_modules = []
        for module_name in module_names:
            if module_name not in unique_modules:
                unique_modules.append(module_name)

        files: list[str] = []
        if self.backend == "python":
            app_file = src_dir / "app.py"
            app_file.write_text(self._build_fastapi_app(unique_modules), encoding="utf-8")
            files.append(str(app_file))

            requirements_file = backend_dir / "requirements.txt"
            requirements_file.write_text("fastapi>=0.110.0\nuvicorn>=0.27.0\n", encoding="utf-8")
            files.append(str(requirements_file))
        elif self.backend == "node":
            package_json = {
                "name": f"{self.name}-backend",
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "dev": "node src/app.js",
                    "start": "node src/app.js",
                },
                "dependencies": {
                    "express": "^4.19.0",
                },
            }
            package_file = backend_dir / "package.json"
            package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
            files.append(str(package_file))

            app_file = src_dir / "app.js"
            app_file.write_text(self._build_express_app(unique_modules), encoding="utf-8")
            files.append(str(app_file))
        elif self.backend == "go":
            app_file = src_dir / "main.go"
            app_file.write_text(self._build_go_app(unique_modules), encoding="utf-8")
            files.append(str(app_file))
        elif self.backend == "java":
            app_file = backend_dir / "src" / "main" / "java" / "com" / "superdev" / "Application.java"
            app_file.parent.mkdir(parents=True, exist_ok=True)
            app_file.write_text(self._build_java_app(), encoding="utf-8")
            files.append(str(app_file))

            pom_file = backend_dir / "pom.xml"
            pom_file.write_text(self._build_java_pom(), encoding="utf-8")
            files.append(str(pom_file))
        else:
            # 未知后端类型，回落到 node
            package_json = {
                "name": f"{self.name}-backend",
                "version": "0.1.0",
                "private": True,
                "scripts": {"dev": "node src/app.js", "start": "node src/app.js"},
                "dependencies": {"express": "^4.19.0"},
            }
            package_file = backend_dir / "package.json"
            package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
            files.append(str(package_file))

            app_file = src_dir / "app.js"
            app_file.write_text(self._build_express_app(unique_modules), encoding="utf-8")
            files.append(str(app_file))

        api_contract = backend_dir / "API_CONTRACT.md"
        api_contract.write_text(self._build_api_contract(unique_modules), encoding="utf-8")
        files.append(str(api_contract))

        return files

    def _generate_react_frontend(
        self,
        frontend_dir: Path,
        src_dir: Path,
        modules_dir: Path,
        unique_modules: list[str],
    ) -> list[str]:
        files: list[str] = []
        package_json = {
            "name": f"{self.name}-frontend",
            "version": "0.1.0",
            "private": True,
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"react": "^18.3.0", "react-dom": "^18.3.0"},
            "devDependencies": {
                "vite": "^5.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "typescript": "^5.0.0",
            },
        }
        package_file = frontend_dir / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
        files.append(str(package_file))

        app_file = src_dir / "App.tsx"
        app_file.write_text(self._build_react_app(unique_modules), encoding="utf-8")
        files.append(str(app_file))

        main_file = src_dir / "main.tsx"
        main_file.write_text(
            (
                "import React from 'react';\n"
                "import ReactDOM from 'react-dom/client';\n"
                "import App from './App';\n\n"
                "ReactDOM.createRoot(document.getElementById('root')!).render(\n"
                "  <React.StrictMode>\n"
                "    <App />\n"
                "  </React.StrictMode>\n"
                ");\n"
            ),
            encoding="utf-8",
        )
        files.append(str(main_file))

        index_file = frontend_dir / "index.html"
        index_file.write_text(self._build_index_html("root", "/src/main.tsx"), encoding="utf-8")
        files.append(str(index_file))

        for module_name in unique_modules:
            module_file = modules_dir / f"{module_name}.tsx"
            module_file.write_text(self._build_module_component(module_name), encoding="utf-8")
            files.append(str(module_file))

        return files

    def _generate_vue_frontend(
        self,
        frontend_dir: Path,
        src_dir: Path,
        modules_dir: Path,
        unique_modules: list[str],
    ) -> list[str]:
        files: list[str] = []
        package_json = {
            "name": f"{self.name}-frontend",
            "version": "0.1.0",
            "private": True,
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"vue": "^3.4.0"},
            "devDependencies": {"vite": "^5.0.0", "@vitejs/plugin-vue": "^5.0.0"},
        }
        package_file = frontend_dir / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
        files.append(str(package_file))

        vite_file = frontend_dir / "vite.config.js"
        vite_file.write_text(
            (
                "import { defineConfig } from 'vite';\n"
                "import vue from '@vitejs/plugin-vue';\n\n"
                "export default defineConfig({\n"
                "  plugins: [vue()],\n"
                "});\n"
            ),
            encoding="utf-8",
        )
        files.append(str(vite_file))

        app_file = src_dir / "App.vue"
        app_file.write_text(self._build_vue_app(unique_modules), encoding="utf-8")
        files.append(str(app_file))

        main_file = src_dir / "main.js"
        main_file.write_text(
            (
                "import { createApp } from 'vue';\n"
                "import App from './App.vue';\n\n"
                "createApp(App).mount('#app');\n"
            ),
            encoding="utf-8",
        )
        files.append(str(main_file))

        index_file = frontend_dir / "index.html"
        index_file.write_text(self._build_index_html("app", "/src/main.js"), encoding="utf-8")
        files.append(str(index_file))

        for module_name in unique_modules:
            module_file = modules_dir / f"{module_name}.vue"
            module_file.write_text(self._build_vue_module(module_name), encoding="utf-8")
            files.append(str(module_file))

        return files

    def _generate_svelte_frontend(
        self,
        frontend_dir: Path,
        src_dir: Path,
        modules_dir: Path,
        unique_modules: list[str],
    ) -> list[str]:
        files: list[str] = []
        package_json = {
            "name": f"{self.name}-frontend",
            "version": "0.1.0",
            "private": True,
            "scripts": {"dev": "vite", "build": "vite build", "preview": "vite preview"},
            "dependencies": {"svelte": "^4.2.0"},
            "devDependencies": {"vite": "^5.0.0", "@sveltejs/vite-plugin-svelte": "^3.0.0"},
        }
        package_file = frontend_dir / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
        files.append(str(package_file))

        vite_file = frontend_dir / "vite.config.js"
        vite_file.write_text(
            (
                "import { defineConfig } from 'vite';\n"
                "import { svelte } from '@sveltejs/vite-plugin-svelte';\n\n"
                "export default defineConfig({\n"
                "  plugins: [svelte()],\n"
                "});\n"
            ),
            encoding="utf-8",
        )
        files.append(str(vite_file))

        app_file = src_dir / "App.svelte"
        app_file.write_text(self._build_svelte_app(unique_modules), encoding="utf-8")
        files.append(str(app_file))

        main_file = src_dir / "main.js"
        main_file.write_text(
            (
                "import App from './App.svelte';\n\n"
                "const app = new App({\n"
                "  target: document.getElementById('app')\n"
                "});\n\n"
                "export default app;\n"
            ),
            encoding="utf-8",
        )
        files.append(str(main_file))

        index_file = frontend_dir / "index.html"
        index_file.write_text(self._build_index_html("app", "/src/main.js"), encoding="utf-8")
        files.append(str(index_file))

        for module_name in unique_modules:
            module_file = modules_dir / f"{module_name}.svelte"
            module_file.write_text(self._build_svelte_module(module_name), encoding="utf-8")
            files.append(str(module_file))

        return files

    def _generate_angular_frontend(
        self,
        frontend_dir: Path,
        src_dir: Path,
        unique_modules: list[str],
    ) -> list[str]:
        files: list[str] = []
        package_json = {
            "name": f"{self.name}-frontend",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "start": "ng serve",
                "build": "ng build",
                "test": "ng test",
            },
            "dependencies": {
                "@angular/animations": "^17.0.0",
                "@angular/common": "^17.0.0",
                "@angular/compiler": "^17.0.0",
                "@angular/core": "^17.0.0",
                "@angular/forms": "^17.0.0",
                "@angular/platform-browser": "^17.0.0",
                "@angular/platform-browser-dynamic": "^17.0.0",
                "@angular/router": "^17.0.0",
                "rxjs": "^7.8.0",
                "zone.js": "^0.14.0",
            },
            "devDependencies": {
                "@angular/cli": "^17.0.0",
                "@angular/compiler-cli": "^17.0.0",
                "typescript": "^5.0.0",
            },
        }
        package_file = frontend_dir / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2, ensure_ascii=False), encoding="utf-8")
        files.append(str(package_file))

        app_dir = src_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)

        component_file = app_dir / "app.component.ts"
        component_file.write_text(self._build_angular_component(unique_modules), encoding="utf-8")
        files.append(str(component_file))

        module_file = app_dir / "app.module.ts"
        module_file.write_text(
            (
                "import { NgModule } from '@angular/core';\n"
                "import { BrowserModule } from '@angular/platform-browser';\n"
                "import { AppComponent } from './app.component';\n\n"
                "@NgModule({\n"
                "  declarations: [AppComponent],\n"
                "  imports: [BrowserModule],\n"
                "  bootstrap: [AppComponent],\n"
                "})\n"
                "export class AppModule {}\n"
            ),
            encoding="utf-8",
        )
        files.append(str(module_file))

        main_file = src_dir / "main.ts"
        main_file.write_text(
            (
                "import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';\n"
                "import { AppModule } from './app/app.module';\n\n"
                "platformBrowserDynamic()\n"
                "  .bootstrapModule(AppModule)\n"
                "  .catch(err => console.error(err));\n"
            ),
            encoding="utf-8",
        )
        files.append(str(main_file))

        index_file = frontend_dir / "index.html"
        index_file.write_text(self._build_index_html("app-root", "/src/main.ts"), encoding="utf-8")
        files.append(str(index_file))

        return files

    def _build_react_app(self, modules: list[str]) -> str:
        imports = [f"import {self._to_component(module)} from './modules/{module}';" for module in modules]
        cards = [
            (
                f"        <section style={{border: '1px solid #e5e7eb', borderRadius: 12, padding: 16}}>\n"
                f"          <h3>{self._to_component(module)}</h3>\n"
                f"          <{self._to_component(module)} />\n"
                "        </section>"
            )
            for module in modules
        ]

        return (
            "import React from 'react';\n"
            + "\n".join(imports)
            + "\n\n"
            "export default function App() {\n"
            "  return (\n"
            "    <main style={{maxWidth: 960, margin: '40px auto', fontFamily: 'Arial, sans-serif'}}>\n"
            f"      <h1>{self.name} 实现骨架</h1>\n"
            "      <p>该页面由 Super Dev 自动生成，按模块分区承接需求实现。</p>\n"
            "      <div style={{display: 'grid', gap: 12}}>\n"
            + "\n".join(cards)
            + "\n"
            "      </div>\n"
            "    </main>\n"
            "  );\n"
            "}\n"
        )

    def _build_module_component(self, module_name: str) -> str:
        component = self._to_component(module_name)
        return (
            "import React from 'react';\n\n"
            f"export default function {component}() {{\n"
            "  return (\n"
            "    <div>\n"
            f"      <p>{module_name} 模块初始骨架已创建，可在此实现业务逻辑。</p>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
        )

    def _build_express_app(self, modules: list[str]) -> str:
        routes = []
        for module_name in modules:
            routes.append(
                (
                    f"app.get('/api/{module_name}', (req, res) => {{\n"
                    "  res.json({\n"
                    f"    module: '{module_name}',\n"
                    "    status: 'todo',\n"
                    "    message: 'Module scaffold created by Super Dev'\n"
                    "  });\n"
                    "});"
                )
            )

        return (
            "const express = require('express');\n\n"
            "const app = express();\n"
            "app.use(express.json());\n\n"
            "app.get('/health', (_req, res) => {\n"
            "  res.json({ status: 'ok' });\n"
            "});\n\n"
            + "\n\n".join(routes)
            + "\n\n"
            "const port = process.env.PORT || 3001;\n"
            "app.listen(port, () => {\n"
            "  console.log(`Backend scaffold is running on http://localhost:${port}`);\n"
            "});\n"
        )

    def _build_fastapi_app(self, modules: list[str]) -> str:
        route_blocks = []
        for module_name in modules:
            function_name = self._safe_identifier(module_name)
            route_segment = self._safe_route_segment(module_name)
            route_blocks.append(
                (
                    f"@app.get('/api/{route_segment}')\n"
                    f"def get_{function_name}():\n"
                    "    return {\n"
                    f"        'module': '{module_name}',\n"
                    "        'status': 'todo',\n"
                    "        'message': 'Module scaffold created by Super Dev'\n"
                    "    }\n"
                )
            )

        return (
            "from fastapi import FastAPI\n\n"
            "app = FastAPI(title='Super Dev Backend Scaffold')\n\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'status': 'ok'}\n\n"
            + "\n\n".join(route_blocks)
            + "\n"
        )

    def _build_api_contract(self, modules: list[str]) -> str:
        lines = [
            "# API Contract (Scaffold)",
            "",
            "以下接口由 Super Dev 根据需求模块生成，后续请补充字段和鉴权细节。",
            "",
            "| Module | Method | Path | Purpose |",
            "|:---|:---|:---|:---|",
        ]
        for module_name in modules:
            route_segment = self._safe_route_segment(module_name)
            lines.append(f"| {module_name} | GET | /api/{route_segment} | 获取 {module_name} 模块初始数据 |")
        lines.append("")
        return "\n".join(lines)

    def _build_go_app(self, modules: list[str]) -> str:
        handlers = []
        for module_name in modules:
            handler = self._safe_identifier(module_name)
            route = self._safe_route_segment(module_name)
            handlers.append(
                (
                    f"func {handler}Handler(w http.ResponseWriter, _ *http.Request) {{\n"
                    "    w.Header().Set(\"Content-Type\", \"application/json\")\n"
                    f"    w.Write([]byte(`{{\"module\":\"{module_name}\",\"status\":\"todo\"}}`))\n"
                    "}\n"
                )
            )

        routes = [f"    http.HandleFunc(\"/api/{self._safe_route_segment(module_name)}\", {self._safe_identifier(module_name)}Handler)" for module_name in modules]

        return (
            "package main\n\n"
            "import (\n"
            "    \"log\"\n"
            "    \"net/http\"\n"
            ")\n\n"
            + "\n".join(handlers)
            + "\n"
            "func healthHandler(w http.ResponseWriter, _ *http.Request) {\n"
            "    w.Header().Set(\"Content-Type\", \"application/json\")\n"
            "    w.Write([]byte(`{\"status\":\"ok\"}`))\n"
            "}\n\n"
            "func main() {\n"
            "    http.HandleFunc(\"/health\", healthHandler)\n"
            + "\n".join(routes)
            + "\n"
            "    log.Println(\"Backend scaffold running on :3001\")\n"
            "    log.Fatal(http.ListenAndServe(\":3001\", nil))\n"
            "}\n"
        )

    def _build_java_app(self) -> str:
        return (
            "package com.superdev;\n\n"
            "import org.springframework.boot.SpringApplication;\n"
            "import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
            "@SpringBootApplication\n"
            "public class Application {\n"
            "    public static void main(String[] args) {\n"
            "        SpringApplication.run(Application.class, args);\n"
            "    }\n"
            "}\n"
        )

    def _build_java_pom(self) -> str:
        return (
            "<project xmlns=\"http://maven.apache.org/POM/4.0.0\" "
            "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            "xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 "
            "http://maven.apache.org/xsd/maven-4.0.0.xsd\">\n"
            "  <modelVersion>4.0.0</modelVersion>\n"
            "  <groupId>com.superdev</groupId>\n"
            f"  <artifactId>{self.name}-backend</artifactId>\n"
            "  <version>0.1.0</version>\n"
            "  <parent>\n"
            "    <groupId>org.springframework.boot</groupId>\n"
            "    <artifactId>spring-boot-starter-parent</artifactId>\n"
            "    <version>3.2.0</version>\n"
            "    <relativePath/>\n"
            "  </parent>\n"
            "  <properties>\n"
            "    <java.version>17</java.version>\n"
            "  </properties>\n"
            "  <dependencies>\n"
            "    <dependency>\n"
            "      <groupId>org.springframework.boot</groupId>\n"
            "      <artifactId>spring-boot-starter-web</artifactId>\n"
            "    </dependency>\n"
            "  </dependencies>\n"
            "</project>\n"
        )

    def _build_index_html(self, mount_id: str, entry_path: str) -> str:
        return (
            "<!doctype html>\n"
            "<html lang=\"zh-CN\">\n"
            "  <head>\n"
            "    <meta charset=\"UTF-8\" />\n"
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
            f"    <title>{self.name} Frontend</title>\n"
            "  </head>\n"
            "  <body>\n"
            f"    <div id=\"{mount_id}\"></div>\n"
            f"    <script type=\"module\" src=\"{entry_path}\"></script>\n"
            "  </body>\n"
            "</html>\n"
        )

    def _build_vue_app(self, modules: list[str]) -> str:
        imports = [f"import {self._to_component(module)} from './modules/{module}.vue';" for module in modules]
        cards = [
            (
                f"      <section class=\"card\">\n"
                f"        <h3>{self._to_component(module)}</h3>\n"
                f"        <{self._to_component(module)} />\n"
                "      </section>"
            )
            for module in modules
        ]
        components = ", ".join(self._to_component(module) for module in modules)
        return (
            "<template>\n"
            "  <main class=\"shell\">\n"
            f"    <h1>{self.name} 实现骨架</h1>\n"
            "    <div class=\"grid\">\n"
            + "\n".join(cards)
            + "\n"
            "    </div>\n"
            "  </main>\n"
            "</template>\n\n"
            "<script setup>\n"
            + "\n".join(imports)
            + "\n"
            "</script>\n\n"
            "<style>\n"
            ".shell { max-width: 960px; margin: 40px auto; font-family: Arial, sans-serif; }\n"
            ".grid { display: grid; gap: 12px; }\n"
            ".card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }\n"
            "</style>\n"
        )

    def _build_vue_module(self, module_name: str) -> str:
        return (
            "<template>\n"
            f"  <p>{module_name} 模块初始骨架已创建，可在此实现业务逻辑。</p>\n"
            "</template>\n"
        )

    def _build_svelte_app(self, modules: list[str]) -> str:
        imports = [f"import {self._to_component(module)} from './modules/{module}.svelte';" for module in modules]
        cards = [
            (
                "  <section class=\"card\">\n"
                f"    <h3>{self._to_component(module)}</h3>\n"
                f"    <{self._to_component(module)} />\n"
                "  </section>"
            )
            for module in modules
        ]
        return (
            "\n".join(imports)
            + "\n\n"
            f"<main class=\"shell\">\n"
            f"  <h1>{self.name} 实现骨架</h1>\n"
            "  <div class=\"grid\">\n"
            + "\n".join(cards)
            + "\n"
            "  </div>\n"
            "</main>\n\n"
            "<style>\n"
            ".shell { max-width: 960px; margin: 40px auto; font-family: Arial, sans-serif; }\n"
            ".grid { display: grid; gap: 12px; }\n"
            ".card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }\n"
            "</style>\n"
        )

    def _build_svelte_module(self, module_name: str) -> str:
        return f"<p>{module_name} 模块初始骨架已创建，可在此实现业务逻辑。</p>\n"

    def _build_angular_component(self, modules: list[str]) -> str:
        sections = []
        for module_name in modules:
            sections.append(
                (
                    "<section style=\"border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:8px 0;\">\n"
                    f"  <h3>{self._to_component(module_name)}</h3>\n"
                    f"  <p>{module_name} 模块初始骨架已创建，可在此实现业务逻辑。</p>\n"
                    "</section>"
                )
            )
        template = "\\n".join(line.replace("\\", "\\\\").replace("'", "\\'") for line in "\n".join(sections).split("\n"))
        return (
            "import { Component } from '@angular/core';\n\n"
            "@Component({\n"
            "  selector: 'app-root',\n"
            "  template: `\n"
            f"    <main style=\"max-width:960px;margin:40px auto;font-family:Arial,sans-serif;\">\n"
            f"      <h1>{self.name} 实现骨架</h1>\n"
            f"{' '.join(sections)}\n"
            "    </main>\n"
            "  `,\n"
            "})\n"
            "export class AppComponent {}\n"
        )

    def _safe_identifier(self, name: str) -> str:
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in name.lower())
        if not cleaned:
            return "module"
        if cleaned[0].isdigit():
            cleaned = f"m_{cleaned}"
        return cleaned

    def _safe_route_segment(self, name: str) -> str:
        cleaned = "".join(ch if (ch.isalnum() or ch in "-_") else "-" for ch in name.lower())
        cleaned = cleaned.strip("-_")
        return cleaned or "module"

    def _to_component(self, name: str) -> str:
        cleaned = "".join(ch if ch.isalnum() else "-" for ch in name)
        parts = [part for part in cleaned.split("-") if part]
        if not parts:
            return "Module"
        return "".join(part[:1].upper() + part[1:] for part in parts)
