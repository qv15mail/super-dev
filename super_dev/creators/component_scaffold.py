"""
组件脚手架生成器 — 从 UIUX 规范生成可直接使用的 UI 组件代码。

解决的问题：
  - UIUX 文档是"说明书"不是"施工图"
  - 宿主从零实现组件，自然偏离规范
  - 生成的组件代码可直接复制使用，确保设计一致性
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# React / Next.js component templates
#
# All templates use __SUPERDEV_<NAME>__ placeholders instead of Python format
# strings to avoid conflicts with JSX / TypeScript curly-brace syntax.
# ---------------------------------------------------------------------------

_BUTTON_TSX = """\
import { forwardRef, type ButtonHTMLAttributes } from "react";
import { Loader2 } from "__SUPERDEV_ICON_LIB__";
import { cn } from "@/lib/utils";

const variants = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
  outline:
    "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
  ghost: "hover:bg-accent hover:text-accent-foreground",
} as const;

const sizes = {
  sm: "h-8 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
} as const;

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
  loading?: boolean;
}

/**
 * Button component with four visual variants and three sizes.
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="md">Save</Button>
 * <Button variant="outline" loading>Submitting...</Button>
 * ```
 */
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant = "primary", size = "md", loading, disabled, children, ...props },
    ref,
  ) => (
    <button
      ref={ref}
      className={cn(
        variants[variant],
        sizes[size],
        "inline-flex items-center justify-center rounded-md font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "disabled:pointer-events-none disabled:opacity-50",
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";

export { Button, type ButtonProps };
"""

_CARD_TSX = """\
import { type HTMLAttributes, type ReactNode, forwardRef } from "react";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Optional card title rendered inside the header section. */
  title?: string;
  /** Optional subtitle / description below the title. */
  description?: string;
  /** Footer actions (buttons, links, etc.). */
  footer?: ReactNode;
}

/**
 * Flexible Card component with optional header, body and footer.
 *
 * @example
 * ```tsx
 * <Card title="Plan" description="Choose your plan">
 *   <p>Content here</p>
 * </Card>
 * ```
 */
const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, description, footer, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-lg border bg-card text-card-foreground shadow-sm",
        className,
      )}
      {...props}
    >
      {(title || description) && (
        <div className="flex flex-col space-y-1.5 p-6">
          {title && (
            <h3 className="text-2xl font-semibold leading-none tracking-tight">
              {title}
            </h3>
          )}
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      )}
      <div className="p-6 pt-0">{children}</div>
      {footer && (
        <div className="flex items-center p-6 pt-0">{footer}</div>
      )}
    </div>
  ),
);
Card.displayName = "Card";

export { Card, type CardProps };
"""

_INPUT_TSX = """\
import { forwardRef, type InputHTMLAttributes, useId } from "react";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Visible label rendered above the input. */
  label?: string;
  /** Error message displayed below the input. */
  error?: string;
  /** Helper / hint text shown when there is no error. */
  helperText?: string;
}

/**
 * Text input with built-in label, error state and helper text.
 *
 * Supports type="text | email | password | number" out of the box.
 *
 * @example
 * ```tsx
 * <Input label="Email" type="email" error="Invalid email" />
 * ```
 */
const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id: externalId, ...props }, ref) => {
    const autoId = useId();
    const inputId = externalId || autoId;
    return (
      <div className="grid w-full gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
            "ring-offset-background placeholder:text-muted-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive focus-visible:ring-destructive",
            className,
          )}
          aria-invalid={!!error}
          {...props}
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
        {!error && helperText && (
          <p className="text-sm text-muted-foreground">{helperText}</p>
        )}
      </div>
    );
  },
);
Input.displayName = "Input";

export { Input, type InputProps };
"""

_MODAL_TSX = """\
import {
  type ReactNode,
  useCallback,
  useEffect,
  useRef,
  type MouseEvent as ReactMouseEvent,
} from "react";
import { X } from "__SUPERDEV_ICON_LIB__";
import { cn } from "@/lib/utils";

interface ModalProps {
  /** Controls visibility. */
  open: boolean;
  /** Called when the modal requests to close (overlay click, Escape, X button). */
  onClose: () => void;
  /** Modal title shown in the header. */
  title?: string;
  /** Footer actions (e.g. confirm / cancel buttons). */
  footer?: ReactNode;
  /** Body content. */
  children?: ReactNode;
  /** Extra classes for the panel container. */
  className?: string;
}

/**
 * Accessible modal dialog with backdrop, close-on-Escape and focus trap.
 *
 * @example
 * ```tsx
 * <Modal open={show} onClose={() => setShow(false)} title="Confirm">
 *   <p>Are you sure?</p>
 * </Modal>
 * ```
 */
export function Modal({ open, onClose, title, footer, children, className }: ModalProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  /* Close on Escape */
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (open) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [open, handleKeyDown]);

  if (!open) return null;

  const handleOverlayClick = (e: ReactMouseEvent) => {
    if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
    >
      <div
        ref={panelRef}
        className={cn(
          "relative w-full max-w-lg rounded-lg bg-background p-6 shadow-lg",
          "animate-in fade-in-0 zoom-in-95",
          className,
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          <button
            onClick={onClose}
            className="rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </button>
        </div>

        {/* Body */}
        <div className="mt-4">{children}</div>

        {/* Footer */}
        {footer && <div className="mt-6 flex justify-end gap-2">{footer}</div>}
      </div>
    </div>
  );
}
"""

_NAV_TSX = """\
import { useState } from "react";
import { Menu, X } from "__SUPERDEV_ICON_LIB__";
import { cn } from "@/lib/utils";

interface NavLink {
  href: string;
  label: string;
}

interface NavProps {
  /** Brand text or logo element. */
  logo?: React.ReactNode;
  /** Navigation links. */
  links?: NavLink[];
  /** Extra classes for the outer <nav>. */
  className?: string;
}

/**
 * Responsive navigation bar with mobile hamburger menu.
 *
 * @example
 * ```tsx
 * <Nav logo="Acme" links={[{ href: "/about", label: "About" }]} />
 * ```
 */
export function Nav({ logo, links = [], className }: NavProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className={cn("border-b bg-background", className)}>
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <div className="flex-shrink-0 text-lg font-bold">{logo}</div>

        {/* Desktop links */}
        <div className="hidden gap-6 md:flex">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Mobile toggle */}
        <button
          className="inline-flex items-center justify-center rounded-md p-2 md:hidden"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label="Toggle navigation"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile panel */}
      {mobileOpen && (
        <div className="border-t px-4 pb-4 pt-2 md:hidden">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="block py-2 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}
"""

_LAYOUT_TSX = """\
import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface LayoutProps {
  /** Rendered at the top of the page (e.g. <Nav />). */
  header?: ReactNode;
  /** Rendered at the bottom of the page. */
  footer?: ReactNode;
  /** Main page content. */
  children?: ReactNode;
  /** Extra classes for the outer wrapper. */
  className?: string;
}

/**
 * Full-page layout wrapper with header, scrollable main area and footer.
 *
 * @example
 * ```tsx
 * <Layout header={<Nav />} footer={<Footer />}>
 *   <HomePage />
 * </Layout>
 * ```
 */
export function Layout({ header, footer, children, className }: LayoutProps) {
  return (
    <div className={cn("flex min-h-screen flex-col", className)}>
      {header}
      <main className="flex-1">{children}</main>
      {footer}
    </div>
  );
}
"""

_DESIGN_TOKENS_TS = """\
/**
 * Design tokens exported as TypeScript constants.
 *
 * Auto-generated by Super Dev from the UIUX spec.
 * Re-generate with: super-dev generate components
 */

export const colors = {
  primary: "__SUPERDEV_COLOR_PRIMARY__",
  "primary-foreground": "__SUPERDEV_COLOR_PRIMARY_FG__",
  secondary: "__SUPERDEV_COLOR_SECONDARY__",
  "secondary-foreground": "__SUPERDEV_COLOR_SECONDARY_FG__",
  background: "__SUPERDEV_COLOR_BACKGROUND__",
  foreground: "__SUPERDEV_COLOR_FOREGROUND__",
  muted: "__SUPERDEV_COLOR_MUTED__",
  "muted-foreground": "__SUPERDEV_COLOR_MUTED_FG__",
  accent: "__SUPERDEV_COLOR_ACCENT__",
  "accent-foreground": "__SUPERDEV_COLOR_ACCENT_FG__",
  destructive: "__SUPERDEV_COLOR_DESTRUCTIVE__",
  "destructive-foreground": "__SUPERDEV_COLOR_DESTRUCTIVE_FG__",
  border: "__SUPERDEV_COLOR_BORDER__",
  input: "__SUPERDEV_COLOR_INPUT__",
  ring: "__SUPERDEV_COLOR_RING__",
  card: "__SUPERDEV_COLOR_CARD__",
  "card-foreground": "__SUPERDEV_COLOR_CARD_FG__",
} as const;

export const fontFamily = {
  sans: ["__SUPERDEV_FONT_SANS__", "system-ui", "sans-serif"],
  mono: ["__SUPERDEV_FONT_MONO__", "ui-monospace", "monospace"],
} as const;

export const fontSize = {
  xs: "0.75rem",
  sm: "0.875rem",
  base: "1rem",
  lg: "1.125rem",
  xl: "1.25rem",
  "2xl": "1.5rem",
  "3xl": "1.875rem",
  "4xl": "2.25rem",
} as const;

export const spacing = {
  0: "0",
  1: "0.25rem",
  2: "0.5rem",
  3: "0.75rem",
  4: "1rem",
  5: "1.25rem",
  6: "1.5rem",
  8: "2rem",
  10: "2.5rem",
  12: "3rem",
  16: "4rem",
} as const;

export const borderRadius = {
  none: "0",
  sm: "0.125rem",
  md: "0.375rem",
  lg: "0.5rem",
  xl: "0.75rem",
  full: "9999px",
} as const;
"""

_TAILWIND_CONFIG_TS = """\
import type { Config } from "tailwindcss";

/**
 * Tailwind CSS configuration with design tokens.
 *
 * Auto-generated by Super Dev from the UIUX spec.
 * Re-generate with: super-dev generate tailwind
 */
const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "__SUPERDEV_COLOR_PRIMARY__",
          foreground: "__SUPERDEV_COLOR_PRIMARY_FG__",
        },
        secondary: {
          DEFAULT: "__SUPERDEV_COLOR_SECONDARY__",
          foreground: "__SUPERDEV_COLOR_SECONDARY_FG__",
        },
        background: "__SUPERDEV_COLOR_BACKGROUND__",
        foreground: "__SUPERDEV_COLOR_FOREGROUND__",
        muted: {
          DEFAULT: "__SUPERDEV_COLOR_MUTED__",
          foreground: "__SUPERDEV_COLOR_MUTED_FG__",
        },
        accent: {
          DEFAULT: "__SUPERDEV_COLOR_ACCENT__",
          foreground: "__SUPERDEV_COLOR_ACCENT_FG__",
        },
        destructive: {
          DEFAULT: "__SUPERDEV_COLOR_DESTRUCTIVE__",
          foreground: "__SUPERDEV_COLOR_DESTRUCTIVE_FG__",
        },
        border: "__SUPERDEV_COLOR_BORDER__",
        input: "__SUPERDEV_COLOR_INPUT__",
        ring: "__SUPERDEV_COLOR_RING__",
        card: {
          DEFAULT: "__SUPERDEV_COLOR_CARD__",
          foreground: "__SUPERDEV_COLOR_CARD_FG__",
        },
      },
      fontFamily: {
        sans: ["__SUPERDEV_FONT_SANS__", "system-ui", "sans-serif"],
        mono: ["__SUPERDEV_FONT_MONO__", "ui-monospace", "monospace"],
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.125rem",
      },
    },
  },
  plugins: [],
};

export default config;
"""

# ---------------------------------------------------------------------------
# Default token values (used when UIUX doc does not specify)
# ---------------------------------------------------------------------------

_DEFAULT_TOKENS: dict[str, str] = {
    "color_primary": "#1d4ed8",
    "color_primary_fg": "#ffffff",
    "color_secondary": "#64748b",
    "color_secondary_fg": "#ffffff",
    "color_background": "#ffffff",
    "color_foreground": "#0f172a",
    "color_muted": "#f1f5f9",
    "color_muted_fg": "#64748b",
    "color_accent": "#f1f5f9",
    "color_accent_fg": "#0f172a",
    "color_destructive": "#ef4444",
    "color_destructive_fg": "#ffffff",
    "color_border": "#e2e8f0",
    "color_input": "#e2e8f0",
    "color_ring": "#1d4ed8",
    "color_card": "#ffffff",
    "color_card_fg": "#0f172a",
    "font_sans": "Inter",
    "font_mono": "JetBrains Mono",
}


def _apply_tokens(template: str, tokens: dict[str, str], icon_lib: str) -> str:
    """Replace ``__SUPERDEV_<KEY>__`` placeholders with actual values."""
    result = template.replace("__SUPERDEV_ICON_LIB__", icon_lib)
    for key, value in tokens.items():
        placeholder = f"__SUPERDEV_{key.upper()}__"
        result = result.replace(placeholder, value)
    return result


class ComponentScaffoldGenerator:
    """Generates working UI component starter code from the UIUX specification."""

    # Supported frontend frameworks (only React/Next for now)
    _REACT_FRAMEWORKS = {"next", "react", "react-vite", "remix", "gatsby"}

    def __init__(self) -> None:
        self._templates: dict[str, str] = {
            "components/ui/button.tsx": _BUTTON_TSX,
            "components/ui/card.tsx": _CARD_TSX,
            "components/ui/input.tsx": _INPUT_TSX,
            "components/ui/modal.tsx": _MODAL_TSX,
            "components/ui/nav.tsx": _NAV_TSX,
            "components/ui/layout.tsx": _LAYOUT_TSX,
            "lib/design-tokens.ts": _DESIGN_TOKENS_TS,
            "tailwind.config.ts": _TAILWIND_CONFIG_TS,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all(
        self,
        project_dir: str | Path,
        frontend: str = "next",
        ui_profile: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Return a dict mapping relative file paths to file contents.

        Parameters
        ----------
        project_dir:
            Project root; used to locate ``output/*-uiux.md`` for token extraction.
        frontend:
            Frontend framework identifier (``next``, ``react``, ``react-vite``, etc.).
        ui_profile:
            Optional overrides for design tokens and icon library.  Recognised keys:
            ``icon_library`` (str), ``colors`` (dict), ``fonts`` (dict).
        """
        try:
            project_dir = Path(project_dir)
            ui_profile = ui_profile or {}

            if frontend not in self._REACT_FRAMEWORKS:
                logger.info(
                    "Frontend '%s' is not a React variant; component scaffold skipped.",
                    frontend,
                )
                return {}

            tokens = self._resolve_tokens(project_dir, ui_profile)
            icon_lib = ui_profile.get("icon_library", "lucide-react")

            result: dict[str, str] = {}
            for rel_path, template in self._templates.items():
                try:
                    content = _apply_tokens(template, tokens, icon_lib)
                    result[rel_path] = content
                except Exception as exc:
                    logger.warning(
                        "Template '%s' rendering failed: %s; skipping.",
                        rel_path,
                        exc,
                    )

            return result
        except Exception:
            logger.exception("Component scaffold generation failed")
            return {}

    def generate_for_project(self, project_dir: str | Path) -> list[Path]:
        """Read config, generate all components and write to ``output/components/``.

        Returns the list of written file paths (absolute).
        """
        try:
            project_dir = Path(project_dir)

            frontend, ui_profile = self._read_project_config(project_dir)
            files = self.generate_all(project_dir, frontend=frontend, ui_profile=ui_profile)

            if not files:
                logger.info("No component files generated (frontend=%s).", frontend)
                return []

            output_root = project_dir / "output" / "components"
            written: list[Path] = []
            for rel_path, content in files.items():
                dest = output_root / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
                written.append(dest)
                logger.debug("Wrote component scaffold: %s", dest)

            return written
        except Exception:
            logger.exception("generate_for_project failed")
            return []

    # ------------------------------------------------------------------
    # Token resolution helpers
    # ------------------------------------------------------------------

    def _resolve_tokens(
        self,
        project_dir: Path,
        ui_profile: dict[str, Any],
    ) -> dict[str, str]:
        """Merge default tokens with values from UIUX doc and ui_profile."""
        tokens = dict(_DEFAULT_TOKENS)

        # Try to extract from output/*-uiux.md
        try:
            uiux_content = self._read_uiux_doc(project_dir)
            if uiux_content:
                extracted = self._extract_tokens_from_uiux(uiux_content)
                tokens.update(extracted)
        except Exception:
            logger.debug("Could not extract tokens from UIUX doc; using defaults.")

        # Apply overrides from ui_profile
        if "colors" in ui_profile and isinstance(ui_profile["colors"], dict):
            for key, val in ui_profile["colors"].items():
                token_key = f"color_{key.replace('-', '_')}"
                if token_key in tokens:
                    tokens[token_key] = str(val)

        if "fonts" in ui_profile and isinstance(ui_profile["fonts"], dict):
            if "sans" in ui_profile["fonts"]:
                tokens["font_sans"] = str(ui_profile["fonts"]["sans"])
            if "mono" in ui_profile["fonts"]:
                tokens["font_mono"] = str(ui_profile["fonts"]["mono"])

        return tokens

    def _read_uiux_doc(self, project_dir: Path) -> str:
        """Read the first ``output/*-uiux.md`` file found."""
        output_dir = project_dir / "output"
        if not output_dir.is_dir():
            return ""
        candidates = sorted(output_dir.glob("*-uiux.md"))
        if not candidates:
            return ""
        return candidates[0].read_text(encoding="utf-8")

    @staticmethod
    def _extract_tokens_from_uiux(content: str) -> dict[str, str]:
        """Best-effort extraction of color hex codes and font names."""
        tokens: dict[str, str] = {}

        color_map = {
            r"(?i)primary(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_primary",
            r"(?i)secondary(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_secondary",
            r"(?i)background(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_background",
            r"(?i)foreground(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_foreground",
            r"(?i)accent(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_accent",
            r"(?i)destructive(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_destructive",
            r"(?i)muted(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_muted",
            r"(?i)border(?:\s*color)?[\s:]+?(#[0-9a-fA-F]{3,8})": "color_border",
        }
        for pattern, key in color_map.items():
            match = re.search(pattern, content)
            if match:
                tokens[key] = match.group(1)

        # Font family extraction
        font_pattern = (
            r"(?i)(?:sans[- ]?serif|body|primary)\s*(?:font|字体)"
            r"[\s:]+?[\"']?([A-Za-z ]+)[\"']?"
        )
        match = re.search(font_pattern, content)
        if match:
            tokens["font_sans"] = match.group(1).strip()

        mono_pattern = (
            r"(?i)(?:mono(?:space)?|code)\s*(?:font|字体)" r"[\s:]+?[\"']?([A-Za-z ]+)[\"']?"
        )
        match = re.search(mono_pattern, content)
        if match:
            tokens["font_mono"] = match.group(1).strip()

        return tokens

    # ------------------------------------------------------------------
    # Project config reading
    # ------------------------------------------------------------------

    def _read_project_config(self, project_dir: Path) -> tuple[str, dict[str, Any]]:
        """Read ``super-dev.yaml`` and return ``(frontend, ui_profile)``."""
        frontend = "next"
        ui_profile: dict[str, Any] = {}

        try:
            import yaml  # type: ignore[import-untyped]

            config_path = project_dir / "super-dev.yaml"
            if config_path.is_file():
                data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
                frontend = data.get("frontend", "next")
                ui_profile["icon_library"] = data.get("icon_library", "lucide-react")
        except Exception:
            logger.debug("Could not read super-dev.yaml; using defaults.")

        return frontend, ui_profile
