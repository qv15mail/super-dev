"""
Next.js App Router 脚手架生成器测试
"""

import json
from pathlib import Path

from super_dev.creators.nextjs_scaffold import NextjsScaffoldGenerator


class TestNextjsScaffoldGenerator:
    """Tests for NextjsScaffoldGenerator."""

    def test_generate_creates_all_files(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        files = gen.generate(temp_project_dir, "my-app")

        assert len(files) == 16

        base = temp_project_dir / "output" / "nextjs-scaffold"
        expected = [
            base / "app" / "layout.tsx",
            base / "app" / "page.tsx",
            base / "app" / "globals.css",
            base / "app" / "api" / "health" / "route.ts",
            base / "app" / "dashboard" / "layout.tsx",
            base / "app" / "dashboard" / "page.tsx",
            base / "app" / "error.tsx",
            base / "app" / "loading.tsx",
            base / "app" / "not-found.tsx",
            base / "middleware.ts",
            base / "next.config.ts",
            base / "tailwind.config.ts",
            base / "tsconfig.json",
            base / "package.json",
            base / ".eslintrc.json",
            base / "lib" / "utils.ts",
        ]
        for p in expected:
            assert p.exists(), f"Missing file: {p}"

    def test_root_layout_uses_next_font(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        layout = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "layout.tsx").read_text(
            encoding="utf-8"
        )

        assert 'from "next/font/google"' in layout
        assert "Metadata" in layout
        assert 'lang="zh-CN"' in layout
        assert "my-app" in layout

    def test_home_page_is_server_component(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        page = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "page.tsx").read_text(
            encoding="utf-8"
        )

        # Server component: no "use client" directive
        assert '"use client"' not in page
        # Async data fetch
        assert "async" in page

    def test_error_boundary_is_client_component(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        error = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "error.tsx").read_text(
            encoding="utf-8"
        )

        assert '"use client"' in error
        assert "reset" in error

    def test_middleware_protects_dashboard(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        mw = (temp_project_dir / "output" / "nextjs-scaffold" / "middleware.ts").read_text(
            encoding="utf-8"
        )

        assert "NextRequest" in mw
        assert "/dashboard" in mw
        assert "matcher" in mw

    def test_next_config_has_security_headers(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        cfg = (temp_project_dir / "output" / "nextjs-scaffold" / "next.config.ts").read_text(
            encoding="utf-8"
        )

        assert "X-Frame-Options" in cfg
        assert "X-Content-Type-Options" in cfg
        assert "standalone" in cfg
        assert "poweredByHeader: false" in cfg

    def test_tsconfig_has_strict_and_path_aliases(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        raw = (temp_project_dir / "output" / "nextjs-scaffold" / "tsconfig.json").read_text(
            encoding="utf-8"
        )
        tsconfig = json.loads(raw)

        assert tsconfig["compilerOptions"]["strict"] is True
        assert "@/*" in tsconfig["compilerOptions"]["paths"]

    def test_package_json_has_required_deps(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        raw = (temp_project_dir / "output" / "nextjs-scaffold" / "package.json").read_text(
            encoding="utf-8"
        )
        pkg = json.loads(raw)

        assert "next" in pkg["dependencies"]
        assert "react" in pkg["dependencies"]
        assert "react-dom" in pkg["dependencies"]
        assert "lucide-react" in pkg["dependencies"]
        assert "tailwindcss" in pkg["devDependencies"]
        assert pkg["scripts"]["dev"] == "next dev"

    def test_lib_utils_cn_function(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        utils = (temp_project_dir / "output" / "nextjs-scaffold" / "lib" / "utils.ts").read_text(
            encoding="utf-8"
        )

        assert "clsx" in utils
        assert "twMerge" in utils
        assert "cn" in utils

    def test_tailwind_config_has_design_tokens(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        tw = (temp_project_dir / "output" / "nextjs-scaffold" / "tailwind.config.ts").read_text(
            encoding="utf-8"
        )

        assert "primary" in tw
        assert "secondary" in tw
        assert "accent" in tw
        assert "destructive" in tw
        assert "muted" in tw
        assert "fontFamily" in tw
        assert "borderRadius" in tw
        assert "app/**" in tw

    def test_generate_tailwind_config_standalone(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        result = gen.generate_tailwind_config(temp_project_dir)

        assert isinstance(result, str)
        assert "import type { Config }" in result
        assert "primary" in result

    def test_custom_ui_profile_colors(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        profile = {
            "colors": {"primary": "#1a1a2e", "accent": "#e94560"},
            "fonts": {"sans": "Roboto"},
        }
        gen.generate(temp_project_dir, "my-app", ui_profile=profile)

        tw = (temp_project_dir / "output" / "nextjs-scaffold" / "tailwind.config.ts").read_text(
            encoding="utf-8"
        )

        assert "#1a1a2e" in tw
        assert "#e94560" in tw
        assert "Roboto" in tw

        layout = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "layout.tsx").read_text(
            encoding="utf-8"
        )
        assert "Roboto" in layout

    def test_health_route_handler(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        route = (
            temp_project_dir / "output" / "nextjs-scaffold" / "app" / "api" / "health" / "route.ts"
        ).read_text(encoding="utf-8")

        assert "NextResponse" in route
        assert "GET" in route
        assert "healthy" in route

    def test_dashboard_uses_suspense(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        page = (
            temp_project_dir / "output" / "nextjs-scaffold" / "app" / "dashboard" / "page.tsx"
        ).read_text(encoding="utf-8")

        assert "Suspense" in page
        # Server component by default
        assert '"use client"' not in page

    def test_not_found_page(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        nf = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "not-found.tsx").read_text(
            encoding="utf-8"
        )

        assert "404" in nf
        assert "next/link" in nf

    def test_eslintrc(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        raw = (temp_project_dir / "output" / "nextjs-scaffold" / ".eslintrc.json").read_text(
            encoding="utf-8"
        )
        cfg = json.loads(raw)

        assert "next/core-web-vitals" in cfg["extends"]

    def test_globals_css_has_tailwind_imports(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        css = (temp_project_dir / "output" / "nextjs-scaffold" / "app" / "globals.css").read_text(
            encoding="utf-8"
        )

        assert "@tailwind base" in css
        assert "@tailwind components" in css
        assert "@tailwind utilities" in css
        assert "--background" in css

    def test_loading_ui(self, temp_project_dir: Path):
        gen = NextjsScaffoldGenerator()
        gen.generate(temp_project_dir, "my-app")

        loading = (
            temp_project_dir / "output" / "nextjs-scaffold" / "app" / "loading.tsx"
        ).read_text(encoding="utf-8")

        assert "Loading" in loading
        assert "animate-spin" in loading
