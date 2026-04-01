"""Tests for ComponentScaffoldGenerator."""

from pathlib import Path

import yaml

from super_dev.creators.component_scaffold import ComponentScaffoldGenerator


class TestComponentScaffoldGenerator:
    def test_generate_all_returns_eight_files_for_next(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")

        assert len(result) == 8
        assert "components/ui/button.tsx" in result
        assert "components/ui/card.tsx" in result
        assert "components/ui/input.tsx" in result
        assert "components/ui/modal.tsx" in result
        assert "components/ui/nav.tsx" in result
        assert "components/ui/layout.tsx" in result
        assert "lib/design-tokens.ts" in result
        assert "tailwind.config.ts" in result

    def test_generate_all_returns_empty_for_unsupported_frontend(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="angular")
        assert result == {}

    def test_generate_all_supports_react_variants(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        for fw in ("next", "react", "react-vite", "remix", "gatsby"):
            result = gen.generate_all(tmp_path, frontend=fw)
            assert len(result) == 8, f"Expected 8 files for {fw}"

    def test_button_tsx_contains_variants_and_forwardref(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        button = result["components/ui/button.tsx"]

        assert "forwardRef" in button
        assert "primary" in button
        assert "secondary" in button
        assert "outline" in button
        assert "ghost" in button
        assert 'Button.displayName = "Button"' in button

    def test_button_tsx_uses_custom_icon_library(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(
            tmp_path, frontend="next", ui_profile={"icon_library": "heroicons"}
        )
        button = result["components/ui/button.tsx"]
        assert 'from "heroicons"' in button

    def test_design_tokens_contain_default_colors(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        tokens = result["lib/design-tokens.ts"]

        assert "primary:" in tokens
        assert "secondary:" in tokens
        assert "#1d4ed8" in tokens  # default primary color

    def test_tokens_extracted_from_uiux_doc(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        uiux = output_dir / "demo-uiux.md"
        uiux.write_text(
            "# UIUX\n\nprimary color: #ff5500\nsecondary color: #00aaff\n",
            encoding="utf-8",
        )

        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        tokens = result["lib/design-tokens.ts"]

        assert "#ff5500" in tokens
        assert "#00aaff" in tokens

    def test_ui_profile_color_overrides(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(
            tmp_path,
            frontend="next",
            ui_profile={"colors": {"primary": "#111111"}},
        )
        tokens = result["lib/design-tokens.ts"]
        assert "#111111" in tokens

    def test_ui_profile_font_overrides(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(
            tmp_path,
            frontend="next",
            ui_profile={"fonts": {"sans": "Poppins", "mono": "Fira Code"}},
        )
        tokens = result["lib/design-tokens.ts"]
        assert "Poppins" in tokens
        assert "Fira Code" in tokens

    def test_tailwind_config_contains_design_tokens(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        tw = result["tailwind.config.ts"]

        assert "darkMode" in tw
        assert "primary" in tw
        assert "secondary" in tw
        assert "fontFamily" in tw

    def test_generate_for_project_writes_files(self, tmp_path: Path):
        # Set up super-dev.yaml
        config = {"frontend": "next", "name": "demo"}
        (tmp_path / "super-dev.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

        gen = ComponentScaffoldGenerator()
        written = gen.generate_for_project(tmp_path)

        assert len(written) == 8
        for path in written:
            assert path.exists()
            assert path.is_file()

        # Check output directory structure
        assert (tmp_path / "output" / "components" / "components" / "ui" / "button.tsx").exists()
        assert (tmp_path / "output" / "components" / "lib" / "design-tokens.ts").exists()
        assert (tmp_path / "output" / "components" / "tailwind.config.ts").exists()

    def test_generate_for_project_no_config_uses_defaults(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        written = gen.generate_for_project(tmp_path)

        # Default frontend is "next" so it should generate files
        assert len(written) == 8

    def test_generate_for_project_angular_returns_empty(self, tmp_path: Path):
        config = {"frontend": "angular"}
        (tmp_path / "super-dev.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

        gen = ComponentScaffoldGenerator()
        written = gen.generate_for_project(tmp_path)
        assert written == []

    def test_modal_tsx_has_escape_and_overlay_close(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        modal = result["components/ui/modal.tsx"]

        assert "Escape" in modal
        assert "aria-modal" in modal
        assert "onClose" in modal

    def test_nav_tsx_has_mobile_menu(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        nav = result["components/ui/nav.tsx"]

        assert "mobileOpen" in nav
        assert "md:hidden" in nav

    def test_layout_tsx_has_header_main_footer(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        layout = result["components/ui/layout.tsx"]

        assert "header" in layout
        assert "footer" in layout
        assert "<main" in layout

    def test_input_tsx_has_error_state(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        inp = result["components/ui/input.tsx"]

        assert "error" in inp
        assert "helperText" in inp
        assert "aria-invalid" in inp

    def test_card_tsx_has_title_and_footer(self, tmp_path: Path):
        gen = ComponentScaffoldGenerator()
        result = gen.generate_all(tmp_path, frontend="next")
        card = result["components/ui/card.tsx"]

        assert "title" in card
        assert "footer" in card
        assert "description" in card
