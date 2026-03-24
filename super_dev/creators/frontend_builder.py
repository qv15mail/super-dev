"""
前端骨架生成器 - 先交付可演示前端
"""

from __future__ import annotations

import html
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
    <title>{html.escape(self.name)} · Frontend Blueprint</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Sora:wght@400;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div class="bg-layer"></div>
    <main class="shell">
      <nav class="topbar">
        <div class="brand">
          <span class="brand-mark">SD</span>
          <span>{html.escape(self.name)}</span>
        </div>
        <div class="top-actions">
          <a href="#trust">客户证明</a>
          <a href="#workspace">交付路径</a>
          <a class="primary-link" href="#doc-links">查看文档</a>
        </div>
      </nav>

      <header class="hero">
        <div class="hero-copy">
          <p class="eyebrow">Super Dev Frontend First Delivery</p>
          <h1>{self.name}</h1>
          <p class="summary">{self.description}</p>
          <div class="meta">
            <span>Framework: {self.frontend}</span>
            <span>Mode: 需求文档驱动</span>
            <span>Status: Ready</span>
          </div>
          <div class="hero-actions">
            <a class="button button-primary" href="#doc-links">打开核心文档</a>
            <a class="button button-secondary" href="#workspace">查看交付流程</a>
          </div>
          <ul class="trust-strip">
            <li>商业级流程治理</li>
            <li>研究报告与 UI/UX 规范先行</li>
            <li>质量门禁与交付审计可追踪</li>
          </ul>
        </div>
        <div class="hero-panel" aria-label="产品演示摘要">
          <div class="panel-card">
            <p class="panel-label">Preview Snapshot</p>
            <h2>从需求到交付的工作台</h2>
            <p>把 Research、PRD、Architecture、UI/UX、Spec、Quality Gate 放进同一条可审计的交付链。</p>
            <div class="metric-grid">
              <div><strong>12</strong><span>阶段治理</span></div>
              <div><strong>3</strong><span>核心文档</span></div>
              <div><strong>80+</strong><span>质量门禁</span></div>
            </div>
          </div>
        </div>
      </header>

      <section id="trust" class="card trust-band">
        <div class="section-head">
          <h2>可信交付信号</h2>
          <p>不是只生成页面，而是确保需求、规范、状态、质量和上线准备全部可追踪。</p>
        </div>
        <div class="trust-grid">
          <article class="trust-item">
            <h3>Research First</h3>
            <p>先研究同类产品、页面结构与商业表达，再写文档和代码。</p>
          </article>
          <article class="trust-item">
            <h3>UI/UX Baseline</h3>
            <p>先冻结组件生态、设计 token、页面骨架和状态矩阵，再实现页面。</p>
          </article>
          <article class="trust-item">
            <h3>Quality Gate</h3>
            <p>红队审查、UI 审查、质量门禁和发布演练共同保证可交付性。</p>
          </article>
        </div>
      </section>

      <section class="card doc-hub">
        <div class="section-head">
          <h2>核心文档</h2>
          <p>先完成文档，再以文档驱动实现。</p>
        </div>
        <div id="doc-links" class="doc-grid"></div>
      </section>

      <section id="workspace" class="card split">
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

      <section class="card split preview-proof">
        <div>
          <div class="section-head">
            <h2>页面骨架</h2>
            <p>对外页面要有价值表达、信任证明、能力模块和明确 CTA。</p>
          </div>
          <ul class="delivery-list">
            <li>Hero + 价值主张 + CTA</li>
            <li>真实截图/演示摘要</li>
            <li>案例 / 安全 / FAQ / 证明</li>
            <li>功能分区与下一步转化入口</li>
          </ul>
        </div>
        <div>
          <div class="section-head">
            <h2>交付证明</h2>
            <p>适用于官网、产品页、工作台和商业级 MVP 验证。</p>
          </div>
          <div class="proof-card">
            <strong>Case Study Ready</strong>
            <p>支持把页面、文档、任务状态和质量报告一起用于内部评审或商业验证。</p>
            <a class="inline-link" href="#faq">查看 FAQ</a>
          </div>
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

      <section id="faq" class="card">
        <div class="section-head">
          <h2>FAQ</h2>
          <p>快速回答“为什么不是直接写代码”的问题。</p>
        </div>
        <div class="faq-list">
          <article>
            <h3>为什么先做文档？</h3>
            <p>因为商业级交付不只是把页面写出来，而是让需求、架构、UI/UX 和质量口径可审计。</p>
          </article>
          <article>
            <h3>为什么要看质量门禁？</h3>
            <p>为了尽早识别风险、状态缺失、UI 模板化和交付短板，而不是等上线前才返工。</p>
          </article>
        </div>
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

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #172133;
  color: #ffffff;
  font-size: 13px;
}

.top-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.top-actions a {
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
}

.top-actions .primary-link {
  color: var(--primary);
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.9fr);
  gap: 18px;
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

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 18px 0 18px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  font-weight: 800;
  text-decoration: none;
}

.button-primary {
  background: var(--text);
  color: #ffffff;
}

.button-secondary {
  background: rgba(15, 124, 250, 0.08);
  color: #12438a;
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

.trust-strip {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.trust-strip li {
  color: var(--muted);
}

.hero-panel {
  display: flex;
}

.panel-card,
.proof-card {
  width: 100%;
  border-radius: 18px;
  border: 1px solid rgba(23, 33, 51, 0.08);
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(243,247,255,0.92));
  padding: 20px;
}

.panel-label {
  margin: 0 0 8px;
  color: var(--primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel-card h2,
.proof-card strong {
  display: block;
  margin: 0 0 8px;
  font-family: "Sora", sans-serif;
}

.metric-grid,
.trust-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric-grid div,
.trust-item {
  border-radius: 14px;
  padding: 14px;
  background: rgba(15, 124, 250, 0.06);
}

.metric-grid strong {
  display: block;
  font-size: 24px;
  font-family: "Sora", sans-serif;
}

.metric-grid span {
  color: var(--muted);
  font-size: 13px;
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

.inline-link {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.faq-list {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.faq-list article {
  border-radius: 14px;
  border: 1px solid rgba(23, 33, 51, 0.08);
  padding: 16px;
  background: #ffffff;
}

.faq-list h3 {
  margin: 0 0 8px;
  font-size: 17px;
}

.faq-list p,
.trust-item p,
.proof-card p {
  margin: 0;
  color: var(--muted);
}

@media (max-width: 860px) {
  .topbar,
  .hero {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }

  .doc-grid {
    grid-template-columns: 1fr;
  }

  .split {
    grid-template-columns: 1fr;
  }

  .metric-grid,
  .trust-grid,
  .faq-list {
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
        payload_str = payload_str.replace("</", "<\\/")
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
