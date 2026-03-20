"""
统一维护 Super Dev 的枚举目录（平台、前后端模板、领域、语言偏好等）。

该模块用于消除 CLI / Config / Web API 之间的重复定义，保证单一真源。
"""

from __future__ import annotations

import os
from pathlib import Path

PLATFORM_CATALOG: list[dict[str, str]] = [
    {"id": "web", "name": "Web 应用"},
    {"id": "mobile", "name": "H5 / APP"},
    {"id": "wechat", "name": "微信小程序（MiniApp）"},
    {"id": "desktop", "name": "桌面应用"},
]

PIPELINE_FRONTEND_TEMPLATE_CATALOG: list[dict[str, str]] = [
    {"id": "react", "name": "React"},
    {"id": "vue", "name": "Vue"},
    {"id": "angular", "name": "Angular"},
    {"id": "svelte", "name": "Svelte"},
    {"id": "none", "name": "无"},
]

FULL_FRONTEND_TEMPLATE_CATALOG: list[dict[str, str]] = [
    {"id": "next", "name": "Next.js"},
    {"id": "remix", "name": "Remix"},
    {"id": "react-vite", "name": "React + Vite"},
    {"id": "gatsby", "name": "Gatsby"},
    {"id": "nuxt", "name": "Nuxt"},
    {"id": "vue-vite", "name": "Vue + Vite"},
    {"id": "angular", "name": "Angular"},
    {"id": "sveltekit", "name": "SvelteKit"},
    {"id": "astro", "name": "Astro"},
    {"id": "solid", "name": "Solid"},
    {"id": "qwik", "name": "Qwik"},
    {"id": "react", "name": "React"},
    {"id": "vue", "name": "Vue"},
    {"id": "svelte", "name": "Svelte"},
    {"id": "none", "name": "无"},
]

BACKEND_TEMPLATE_CATALOG: list[dict[str, str]] = [
    {"id": "node", "name": "Node.js"},
    {"id": "python", "name": "Python"},
    {"id": "go", "name": "Go"},
    {"id": "java", "name": "Java"},
    {"id": "rust", "name": "Rust"},
    {"id": "php", "name": "PHP"},
    {"id": "ruby", "name": "Ruby"},
    {"id": "csharp", "name": "C# (.NET)"},
    {"id": "kotlin", "name": "Kotlin"},
    {"id": "swift", "name": "Swift"},
    {"id": "elixir", "name": "Elixir"},
    {"id": "scala", "name": "Scala"},
    {"id": "dart", "name": "Dart"},
    {"id": "none", "name": "无"},
]

DOMAIN_CATALOG: list[dict[str, str]] = [
    {"id": "", "name": "通用"},
    {"id": "fintech", "name": "金融科技"},
    {"id": "ecommerce", "name": "电子商务"},
    {"id": "medical", "name": "医疗健康"},
    {"id": "social", "name": "社交媒体"},
    {"id": "iot", "name": "物联网"},
    {"id": "education", "name": "在线教育"},
    {"id": "auth", "name": "认证安全"},
    {"id": "content", "name": "内容平台"},
    {"id": "saas", "name": "SaaS"},
]

CICD_PLATFORM_CATALOG: list[dict[str, str]] = [
    {"id": "all", "name": "全部平台"},
    {"id": "github", "name": "GitHub Actions"},
    {"id": "gitlab", "name": "GitLab CI"},
    {"id": "jenkins", "name": "Jenkins"},
    {"id": "azure", "name": "Azure DevOps"},
    {"id": "bitbucket", "name": "Bitbucket Pipelines"},
]

LANGUAGE_PREFERENCE_CATALOG: list[dict[str, str]] = [
    {"id": "python", "name": "Python"},
    {"id": "typescript", "name": "TypeScript"},
    {"id": "javascript", "name": "JavaScript"},
    {"id": "go", "name": "Go"},
    {"id": "java", "name": "Java"},
    {"id": "csharp", "name": "C#"},
    {"id": "cpp", "name": "C++"},
    {"id": "c", "name": "C"},
    {"id": "rust", "name": "Rust"},
    {"id": "kotlin", "name": "Kotlin"},
    {"id": "swift", "name": "Swift"},
    {"id": "objective-c", "name": "Objective-C"},
    {"id": "php", "name": "PHP"},
    {"id": "ruby", "name": "Ruby"},
    {"id": "scala", "name": "Scala"},
    {"id": "dart", "name": "Dart"},
    {"id": "elixir", "name": "Elixir"},
    {"id": "erlang", "name": "Erlang"},
    {"id": "clojure", "name": "Clojure"},
    {"id": "haskell", "name": "Haskell"},
    {"id": "ocaml", "name": "OCaml"},
    {"id": "fsharp", "name": "F#"},
    {"id": "lua", "name": "Lua"},
    {"id": "perl", "name": "Perl"},
    {"id": "groovy", "name": "Groovy"},
    {"id": "r", "name": "R"},
    {"id": "julia", "name": "Julia"},
    {"id": "matlab", "name": "MATLAB"},
    {"id": "sql", "name": "SQL"},
    {"id": "bash", "name": "Bash"},
    {"id": "powershell", "name": "PowerShell"},
    {"id": "solidity", "name": "Solidity"},
    {"id": "zig", "name": "Zig"},
    {"id": "nim", "name": "Nim"},
    {"id": "fortran", "name": "Fortran"},
    {"id": "assembly", "name": "Assembly"},
]

PLATFORM_IDS: tuple[str, ...] = tuple(item["id"] for item in PLATFORM_CATALOG)
PIPELINE_FRONTEND_TEMPLATE_IDS: tuple[str, ...] = tuple(item["id"] for item in PIPELINE_FRONTEND_TEMPLATE_CATALOG)
FULL_FRONTEND_TEMPLATE_IDS: tuple[str, ...] = tuple(item["id"] for item in FULL_FRONTEND_TEMPLATE_CATALOG)
PIPELINE_BACKEND_IDS: tuple[str, ...] = tuple(item["id"] for item in BACKEND_TEMPLATE_CATALOG)
DOMAIN_IDS: tuple[str, ...] = tuple(item["id"] for item in DOMAIN_CATALOG)
CICD_PLATFORM_IDS: tuple[str, ...] = tuple(item["id"] for item in CICD_PLATFORM_CATALOG)
CICD_PLATFORM_TARGET_IDS: tuple[str, ...] = tuple(item for item in CICD_PLATFORM_IDS if item != "all")

HOST_TOOL_CATALOG: list[dict[str, str]] = [
    {"id": "antigravity", "name": "Antigravity"},
    {"id": "aider", "name": "Aider CLI"},
    {"id": "claude-code", "name": "Claude Code"},
    {"id": "cline", "name": "Cline"},
    {"id": "codebuddy-cli", "name": "CodeBuddy CLI"},
    {"id": "codebuddy", "name": "CodeBuddy"},
    {"id": "codex-cli", "name": "Codex CLI"},
    {"id": "cursor-cli", "name": "Cursor CLI"},
    {"id": "windsurf", "name": "Windsurf"},
    {"id": "gemini-cli", "name": "Gemini CLI"},
    {"id": "iflow", "name": "iFlow CLI"},
    {"id": "jetbrains-ai", "name": "JetBrains Junie"},
    {"id": "kimi-cli", "name": "Kimi CLI"},
    {"id": "kiro-cli", "name": "Kiro CLI"},
    {"id": "opencode", "name": "OpenCode CLI"},
    {"id": "qoder-cli", "name": "Qoder CLI"},
    {"id": "roo-code", "name": "Roo Code"},
    {"id": "vscode-copilot", "name": "VS Code Copilot"},
    {"id": "cursor", "name": "Cursor"},
    {"id": "kiro", "name": "Kiro"},
    {"id": "qoder", "name": "Qoder"},
    {"id": "trae", "name": "Trae"},
]

HOST_TOOL_IDS: tuple[str, ...] = tuple(item["id"] for item in HOST_TOOL_CATALOG)

PRIMARY_CLI_HOST_TOOL_IDS: tuple[str, ...] = (
    "claude-code",
    "codex-cli",
    "gemini-cli",
    "opencode",
    "kiro-cli",
    "cursor-cli",
    "qoder-cli",
    "codebuddy-cli",
)

PRIMARY_IDE_HOST_TOOL_IDS: tuple[str, ...] = (
    "antigravity",
    "cursor",
    "windsurf",
    "kiro",
    "qoder",
    "codebuddy",
    "trae",
    "vscode-copilot",
)

PRIMARY_HOST_TOOL_IDS: tuple[str, ...] = PRIMARY_CLI_HOST_TOOL_IDS + PRIMARY_IDE_HOST_TOOL_IDS

CLI_HOST_TOOL_IDS: tuple[str, ...] = (
    "aider",
    "claude-code",
    "codebuddy-cli",
    "codex-cli",
    "cursor-cli",
    "gemini-cli",
    "iflow",
    "kimi-cli",
    "kiro-cli",
    "opencode",
    "qoder-cli",
)

HOST_TOOL_CATEGORY_MAP: dict[str, str] = {
    host_id: ("cli" if host_id in CLI_HOST_TOOL_IDS else "ide")
    for host_id in HOST_TOOL_IDS
}

HOST_COMMAND_CANDIDATES: dict[str, list[str]] = {
    "antigravity": ["antigravity"],
    "aider": ["aider"],
    "claude-code": ["claude", "claude-code"],
    "cline": ["cline"],
    "codebuddy-cli": ["codebuddy", "codebuddy-cli"],
    "codebuddy": ["codebuddy"],
    "codex-cli": ["codex"],
    "cursor-cli": ["cursor-agent", "cursor", "cursor-cli"],
    "windsurf": ["windsurf"],
    "gemini-cli": ["gemini", "gemini-cli"],
    "iflow": ["iflow"],
    "kimi-cli": ["kimi", "kimi-cli"],
    "kiro-cli": ["kiro"],
    "opencode": ["opencode"],
    "qoder-cli": ["qoder", "qoder-cli"],
    "roo-code": ["roo", "roo-code"],
    "cursor": ["cursor"],
    "qoder": ["qoder"],
    "trae": ["trae"],
}

HOST_PATH_PATTERNS: dict[str, list[str]] = {
    "antigravity": [
        "~/Applications/Antigravity.app",
        "/Applications/Antigravity.app",
        "%LOCALAPPDATA%/Programs/Google/Antigravity/Antigravity.exe",
        "%PROGRAMFILES%/Google/Antigravity/Antigravity.exe",
        "%PROGRAMFILES(X86)%/Google/Antigravity/Antigravity.exe",
        "%LOCALAPPDATA%/Programs/Antigravity/Antigravity.exe",
        "%PROGRAMFILES%/Antigravity/Antigravity.exe",
        "%PROGRAMFILES(X86)%/Antigravity/Antigravity.exe",
    ],
    "codebuddy": [
        "~/Applications/CodeBuddy.app",
        "/Applications/CodeBuddy.app",
        "%LOCALAPPDATA%/Programs/CodeBuddy/CodeBuddy.exe",
        "%PROGRAMFILES%/CodeBuddy/CodeBuddy.exe",
        "%PROGRAMFILES(X86)%/CodeBuddy/CodeBuddy.exe",
    ],
    "cursor-cli": [
        "~/Applications/Cursor.app",
        "/Applications/Cursor.app",
        "%LOCALAPPDATA%/Programs/Cursor/Cursor.exe",
        "%PROGRAMFILES%/Cursor/Cursor.exe",
        "%PROGRAMFILES(X86)%/Cursor/Cursor.exe",
    ],
    "cursor": [
        "~/Applications/Cursor.app",
        "/Applications/Cursor.app",
        "%LOCALAPPDATA%/Programs/Cursor/Cursor.exe",
        "%PROGRAMFILES%/Cursor/Cursor.exe",
        "%PROGRAMFILES(X86)%/Cursor/Cursor.exe",
    ],
    "kiro": [
        "~/Applications/Kiro.app",
        "/Applications/Kiro.app",
        "%LOCALAPPDATA%/Programs/Kiro/Kiro.exe",
        "%PROGRAMFILES%/Kiro/Kiro.exe",
        "%PROGRAMFILES(X86)%/Kiro/Kiro.exe",
    ],
    "windsurf": [
        "~/Applications/Windsurf.app",
        "/Applications/Windsurf.app",
        "%LOCALAPPDATA%/Programs/Windsurf/Windsurf.exe",
        "%PROGRAMFILES%/Windsurf/Windsurf.exe",
        "%PROGRAMFILES(X86)%/Windsurf/Windsurf.exe",
    ],
    "qoder-cli": [
        "~/Applications/Qoder.app",
        "/Applications/Qoder.app",
        "%LOCALAPPDATA%/Programs/Qoder/Qoder.exe",
        "%PROGRAMFILES%/Qoder/Qoder.exe",
        "%PROGRAMFILES(X86)%/Qoder/Qoder.exe",
    ],
    "qoder": [
        "~/Applications/Qoder.app",
        "/Applications/Qoder.app",
        "%LOCALAPPDATA%/Programs/Qoder/Qoder.exe",
        "%PROGRAMFILES%/Qoder/Qoder.exe",
        "%PROGRAMFILES(X86)%/Qoder/Qoder.exe",
    ],
    "trae": [
        "~/Applications/Trae.app",
        "/Applications/Trae.app",
        "%LOCALAPPDATA%/Programs/Trae/Trae.exe",
        "%PROGRAMFILES%/Trae/Trae.exe",
        "%PROGRAMFILES(X86)%/Trae/Trae.exe",
    ],
    "vscode-copilot": [
        "~/Applications/Visual Studio Code.app",
        "/Applications/Visual Studio Code.app",
        "%LOCALAPPDATA%/Programs/Microsoft VS Code/Code.exe",
        "%PROGRAMFILES%/Microsoft VS Code/Code.exe",
        "%PROGRAMFILES(X86)%/Microsoft VS Code/Code.exe",
    ],
    "jetbrains-ai": [
        "~/Applications/IntelliJ IDEA.app",
        "/Applications/IntelliJ IDEA.app",
        "~/Applications/PyCharm.app",
        "/Applications/PyCharm.app",
    ],
}


def _expand_host_pattern(pattern: str) -> str:
    expanded = pattern
    windows_aliases = {
        "%LOCALAPPDATA%": os.environ.get("LOCALAPPDATA", ""),
        "%APPDATA%": os.environ.get("APPDATA", ""),
        "%PROGRAMFILES%": os.environ.get("PROGRAMFILES", ""),
        "%PROGRAMFILES(X86)%": os.environ.get("PROGRAMFILES(X86)", ""),
        "%USERPROFILE%": os.environ.get("USERPROFILE", str(Path.home())),
    }
    for key, value in windows_aliases.items():
        if key in expanded:
            expanded = expanded.replace(key, value)
    return os.path.expanduser(os.path.expandvars(expanded))


def host_path_candidates(host_id: str) -> list[str]:
    seen: set[str] = set()
    candidates: list[str] = []
    for pattern in HOST_PATH_PATTERNS.get(host_id, []):
        expanded = _expand_host_pattern(pattern)
        if not expanded or expanded in seen:
            continue
        seen.add(expanded)
        candidates.append(expanded)
    return candidates
