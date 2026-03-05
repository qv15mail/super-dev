"""
统一维护 Super Dev 的枚举目录（平台、前后端模板、领域、语言偏好等）。

该模块用于消除 CLI / Config / Web API 之间的重复定义，保证单一真源。
"""

from __future__ import annotations

PLATFORM_CATALOG: list[dict[str, str]] = [
    {"id": "web", "name": "Web 应用"},
    {"id": "mobile", "name": "移动应用"},
    {"id": "wechat", "name": "微信小程序"},
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
    {"id": "claude-code", "name": "Claude Code"},
    {"id": "codebuddy-cli", "name": "CodeBuddy CLI"},
    {"id": "codebuddy", "name": "CodeBuddy"},
    {"id": "codex-cli", "name": "Codex CLI"},
    {"id": "cursor-cli", "name": "Cursor CLI"},
    {"id": "windsurf", "name": "Windsurf"},
    {"id": "gemini-cli", "name": "Gemini CLI"},
    {"id": "iflow", "name": "iFlow CLI"},
    {"id": "kimi-cli", "name": "Kimi CLI"},
    {"id": "kiro-cli", "name": "Kiro CLI"},
    {"id": "opencode", "name": "OpenCode CLI"},
    {"id": "qoder-cli", "name": "Qoder CLI"},
    {"id": "cursor", "name": "Cursor"},
    {"id": "kiro", "name": "Kiro"},
    {"id": "qoder", "name": "Qoder"},
    {"id": "trae", "name": "Trae"},
]

HOST_TOOL_IDS: tuple[str, ...] = tuple(item["id"] for item in HOST_TOOL_CATALOG)

CLI_HOST_TOOL_IDS: tuple[str, ...] = (
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
    "claude-code": ["claude", "claude-code"],
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
    "cursor": ["cursor"],
    "qoder": ["qoder"],
    "trae": ["trae"],
}

HOST_PATH_PATTERNS: dict[str, list[str]] = {
    "codebuddy": ["~/Applications/CodeBuddy.app", "/Applications/CodeBuddy.app"],
    "cursor-cli": ["~/Applications/Cursor.app", "/Applications/Cursor.app"],
    "cursor": ["~/Applications/Cursor.app", "/Applications/Cursor.app"],
    "kiro": ["~/Applications/Kiro.app", "/Applications/Kiro.app"],
    "windsurf": ["~/Applications/Windsurf.app", "/Applications/Windsurf.app"],
    "qoder-cli": ["~/Applications/Qoder.app", "/Applications/Qoder.app"],
    "qoder": ["~/Applications/Qoder.app", "/Applications/Qoder.app"],
    "trae": ["~/Applications/Trae.app", "/Applications/Trae.app"],
}
