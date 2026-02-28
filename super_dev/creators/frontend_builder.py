# -*- coding: utf-8 -*-
"""
前端骨架生成器 - 先交付可演示前端
"""

from __future__ import annotations

import json
from pathlib import Path


class FrontendScaffoldBuilder:
    """生成可直接打开的前端骨架页面"""

    def __init__(
        self,
        project_dir: Path,
        name: str,
        description: str,
        frontend: str = "react",
    ):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.description = description
        self.frontend = frontend

    def generate(
        self,
        requirements: list[dict],
        phases: list[dict],
        docs: dict,
    ) -> dict:
        """写入前端骨架文件并返回路径"""
        output_dir = self.project_dir / "output" / "frontend"
        output_dir.mkdir(parents=True, exist_ok=True)

        html_path = output_dir / "index.html"
        css_path = output_dir / "styles.css"
        js_path = output_dir / "app.js"

        html_path.write_text(self._build_html(), encoding="utf-8")
        css_path.write_text(self._build_css(), encoding="utf-8")
        js_path.write_text(self._build_js(requirements, phases, docs), encoding="utf-8")

        return {
            "html": str(html_path),
            "css": str(css_path),
            "js": str(js_path),
        }

    def _build_html(self) -> str:
        return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{self.name} · Frontend Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Sora:wght@400;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div class="bg-layer"></div>
    <main class="shell">
      <header class="hero">
        <p class="eyebrow">Super Dev Frontend First Delivery</p>
        <h1>{self.name}</h1>
        <p class="summary">{self.description}</p>
        <div class="meta">
          <span>Framework: {self.frontend}</span>
          <span>Mode: 需求文档驱动</span>
          <span>Status: Ready</span>
        </div>
      </header>

      <section class="card doc-hub">
        <div class="section-head">
          <h2>核心文档</h2>
          <p>先完成文档，再以文档驱动实现。</p>
        </div>
        <div id="doc-links" class="doc-grid"></div>
      </section>

      <section class="card split">
        <div>
          <div class="section-head">
            <h2>需求模块</h2>
            <p>按需求生成页面和能力模块。</p>
          </div>
          <div id="requirements" class="chips"></div>
        </div>
        <div>
          <div class="section-head">
            <h2>执行路线</h2>
            <p>从 0-1 到 1-N+1 的阶段推进。</p>
          </div>
          <ol id="timeline" class="timeline"></ol>
        </div>
      </section>

      <section class="card">
        <div class="section-head">
          <h2>交付清单</h2>
          <p>前端先行，随后进入系统化交付。</p>
        </div>
        <ul class="delivery-list">
          <li>阶段 1: PRD / 架构 / UIUX 文档</li>
          <li>阶段 2: 前端骨架与核心页面</li>
          <li>阶段 3: 后端与数据库能力</li>
          <li>阶段 4: 联调、测试、质量门禁</li>
          <li>阶段 5: 发布、监控与迭代</li>
        </ul>
      </section>
    </main>
    <script src="./app.js"></script>
  </body>
</html>
"""

    def _build_css(self) -> str:
        return """
:root {
  --bg-0: #f5f8ff;
  --bg-1: #fff8f1;
  --surface: rgba(255, 255, 255, 0.86);
  --stroke: rgba(29, 42, 62, 0.12);
  --text: #172133;
  --muted: #51627a;
  --primary: #0f7cfa;
  --accent: #f65f22;
  --radius: 18px;
  --shadow: 0 18px 40px rgba(13, 33, 57, 0.09);
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  color: var(--text);
  font-family: "Manrope", system-ui, sans-serif;
  background: linear-gradient(130deg, var(--bg-0), var(--bg-1));
}

.bg-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: radial-gradient(circle at 8% 10%, rgba(15, 124, 250, 0.2), transparent 35%),
    radial-gradient(circle at 85% 12%, rgba(246, 95, 34, 0.2), transparent 28%),
    radial-gradient(circle at 50% 100%, rgba(19, 173, 120, 0.12), transparent 34%);
}

.shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 40px 20px 64px;
  position: relative;
  z-index: 1;
}

.hero {
  padding: 28px 28px 26px;
  border: 1px solid var(--stroke);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow);
  backdrop-filter: blur(6px);
}

.eyebrow {
  margin: 0;
  color: var(--primary);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
}

.hero h1 {
  margin: 10px 0 8px;
  font-family: "Sora", sans-serif;
  font-size: clamp(28px, 4vw, 48px);
}

.summary {
  margin: 0 0 14px;
  color: var(--muted);
}

.meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.meta span {
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(15, 124, 250, 0.08);
  color: #12438a;
  font-size: 13px;
  font-weight: 700;
}

.card {
  margin-top: 18px;
  border: 1px solid var(--stroke);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow);
  padding: 22px;
}

.section-head h2 {
  margin: 0;
  font-size: 22px;
  font-family: "Sora", sans-serif;
}

.section-head p {
  margin: 6px 0 16px;
  color: var(--muted);
}

.doc-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.doc-item {
  display: block;
  text-decoration: none;
  color: inherit;
  border: 1px solid rgba(23, 33, 51, 0.1);
  border-radius: 14px;
  padding: 14px;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
  background: #ffffff;
}

.doc-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 34, 61, 0.12);
}

.doc-item b {
  display: block;
  margin-bottom: 8px;
}

.split {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 13px;
  background: rgba(246, 95, 34, 0.1);
  color: #8a3719;
  border: 1px solid rgba(246, 95, 34, 0.14);
}

.timeline {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 10px;
}

.timeline li {
  padding-left: 4px;
}

.timeline b {
  display: block;
}

.timeline p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.delivery-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
}

@media (max-width: 860px) {
  .doc-grid {
    grid-template-columns: 1fr;
  }

  .split {
    grid-template-columns: 1fr;
  }
}
"""

    def _build_js(self, requirements: list[dict], phases: list[dict], docs: dict) -> str:
        payload = {
            "requirements": requirements,
            "phases": phases,
            "docs": docs,
        }
        payload_str = json.dumps(payload, ensure_ascii=False, indent=2)
        return f"""const DATA = {payload_str};

const docContainer = document.getElementById("doc-links");
const reqContainer = document.getElementById("requirements");
const timelineContainer = document.getElementById("timeline");

const docList = [
  {{ title: "PRD 文档", desc: "产品目标、需求边界、验收标准", path: DATA.docs.prd }},
  {{ title: "架构文档", desc: "模块划分、接口契约、部署策略", path: DATA.docs.architecture }},
  {{ title: "UI/UX 文档", desc: "视觉系统、交互规则、页面结构", path: DATA.docs.uiux }},
  {{ title: "执行路线图", desc: "0-1 与 1-N+1 的分阶段推进", path: DATA.docs.plan }},
  {{ title: "前端蓝图", desc: "前端模块拆分与先行交付策略", path: DATA.docs.frontend_blueprint }},
];

for (const doc of docList) {{
  if (!doc.path) continue;
  const link = document.createElement("a");
  link.className = "doc-item";
  link.href = relativePath(doc.path);
  link.target = "_blank";
  link.rel = "noreferrer";
  link.innerHTML = `<b>${{doc.title}}</b><span>${{doc.desc}}</span>`;
  docContainer.appendChild(link);
}}

for (const req of DATA.requirements) {{
  const chip = document.createElement("span");
  chip.className = "chip";
  chip.textContent = `${{req.spec_name}} · ${{req.req_name}}`;
  reqContainer.appendChild(chip);
}}

for (const phase of DATA.phases) {{
  const li = document.createElement("li");
  li.innerHTML = `<b>${{phase.title}}</b><p>${{phase.objective}}</p>`;
  timelineContainer.appendChild(li);
}}

function relativePath(path) {{
  if (!path) return "#";
  const normalized = String(path).replace(/\\\\/g, "/");
  const marker = "/output/";
  const index = normalized.lastIndexOf(marker);
  if (index >= 0) {{
    return ".." + normalized.slice(index + marker.length - 1);
  }}
  return "#";
}}
"""
