/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：OpenClaw 插件入口
 * 作用：通过 definePluginEntry 注册 Super Dev Tool 到 OpenClaw Agent
 * 创建时间：2026-03-24
 * 最后修改：2026-03-28
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";
import { invokeSuperDev, formatToolResult } from "./utils/subprocess";
import { resolvePluginConfig } from "./types";

/** 子命令白名单（用于 super_dev_run 安全校验） */
const ALLOWED_SUBCOMMANDS = new Set([
  "init", "bootstrap", "analyze", "repo-map", "feature-checklist", "impact",
  "regression-guard", "dependency-graph", "workflow", "studio", "expert",
  "quality", "metrics", "preview", "deploy", "config", "skill", "integrate",
  "onboard", "doctor", "setup", "install", "start", "detect", "update",
  "review", "release", "create", "wizard", "design", "spec", "task",
  "pipeline", "fix", "run", "status", "jump", "confirm", "policy",
  "governance", "product-audit",
]);

export default definePluginEntry({
  id: "super-dev",
  name: "Super Dev Pipeline",
  description:
    "AI development orchestration - research-first, commercial-grade delivery pipeline with 10 expert roles",
  register(api: any) {
    const config = () => resolvePluginConfig(api.pluginConfig);
    const cwd = () => config().projectDir || process.cwd();
    const bin = () => config().superDevBin;
    const timeout = () => config().timeout;

    // 1. super_dev_pipeline - 核心流水线
    // CLI: super-dev pipeline "描述" [--name X] [--frontend X] [--backend X] [--platform X] [--domain X] [--mode X]
    api.registerTool({
      name: "super_dev_pipeline",
      label: "Super Dev Pipeline",
      description:
        "Start the full Super Dev pipeline: research -> PRD -> architecture -> UIUX -> spec -> frontend -> backend -> quality -> delivery.",
      parameters: Type.Object({
        description: Type.String({ description: "Project or feature requirement description" }),
        name: Type.Optional(Type.String({ description: "Project name (auto-generated if omitted)" })),
        frontend: Type.Optional(Type.String({ description: "Frontend: react, vue, angular, svelte, none" })),
        backend: Type.Optional(Type.String({ description: "Backend: node, python, go, java, rust, php, ruby, csharp, kotlin, swift, elixir, scala, dart, none" })),
        platform: Type.Optional(Type.String({ description: "Platform: web, mobile, wechat, desktop" })),
        domain: Type.Optional(Type.String({ description: "Domain: fintech, ecommerce, medical, social, iot, education, auth, content, saas" })),
        mode: Type.Optional(Type.String({ description: "Mode: feature (default) or bugfix" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const desc = params.description;
        if (typeof desc !== "string" || !desc.trim()) {
          return formatToolResult({ stdout: "", stderr: "Missing required parameter: description", exitCode: 1 });
        }
        const args = ["pipeline", desc];
        if (params.name) args.push("--name", String(params.name));
        if (params.frontend) args.push("--frontend", String(params.frontend));
        if (params.backend) args.push("--backend", String(params.backend));
        if (params.platform) args.push("--platform", String(params.platform));
        if (params.domain) args.push("--domain", String(params.domain));
        if (params.mode) args.push("--mode", String(params.mode));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 2. super_dev_init - 项目初始化
    // CLI: super-dev init <name> [-f FRONTEND] [-b BACKEND] [-p PLATFORM] [--domain DOMAIN]
    api.registerTool({
      name: "super_dev_init",
      label: "Super Dev Init",
      description: "Initialize Super Dev in an existing project. Creates super-dev.yaml config file.",
      parameters: Type.Object({
        name: Type.String({ description: "Project name (required, used as positional argument)" }),
        frontend: Type.Optional(Type.String({ description: "Frontend framework: next, react-vite, vue-vite, etc." })),
        backend: Type.Optional(Type.String({ description: "Backend framework: node, python, go, etc." })),
        platform: Type.Optional(Type.String({ description: "Platform: web, mobile, wechat, desktop" })),
        domain: Type.Optional(Type.String({ description: "Domain: fintech, ecommerce, medical, social, iot, education, auth, content, saas" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const name = params.name;
        if (typeof name !== "string" || !name.trim()) {
          return formatToolResult({ stdout: "", stderr: "Missing required parameter: name", exitCode: 1 });
        }
        const args = ["init", name];
        if (params.frontend) args.push("-f", String(params.frontend));
        if (params.backend) args.push("-b", String(params.backend));
        if (params.platform) args.push("-p", String(params.platform));
        if (params.domain) args.push("--domain", String(params.domain));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 3. super_dev_status - 状态查看
    // CLI: super-dev status
    api.registerTool({
      name: "super_dev_status",
      label: "Super Dev Status",
      description: "Check pipeline status: completed phases, current stage, blocking gates, and existing outputs.",
      parameters: Type.Object({}),
      async execute(_id: string, _params: Record<string, unknown>) {
        return formatToolResult(await invokeSuperDev(["status"], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 4. super_dev_quality - 质量门禁
    // CLI: super-dev quality [-t TYPE]
    api.registerTool({
      name: "super_dev_quality",
      label: "Super Dev Quality",
      description: "Run quality gate check. Types: prd, architecture, ui, ux, ui-review, code, all (default).",
      parameters: Type.Object({
        type: Type.Optional(Type.String({ description: "Check type: prd, architecture, ui, ux, ui-review, code, all" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["quality"];
        if (params.type) args.push("-t", String(params.type));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 5. super_dev_spec - Spec 管理
    // CLI: super-dev spec <action> [args...]
    //   list: no extra args
    //   show <change_id>: positional
    //   propose <change_id> --title "..." --description "...": positional + flags
    //   scaffold <change_id> [--force]: positional + optional flag
    //   validate <change_id>: positional
    api.registerTool({
      name: "super_dev_spec",
      label: "Super Dev Spec",
      description: "Manage specs and changes. Actions: init, list, show, propose, add-req, scaffold, quality, validate, view, archive.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: init, list, show, propose, add-req, scaffold, quality, validate, view, archive" }),
        changeId: Type.Optional(Type.String({ description: "Change ID (required for show/propose/scaffold/validate/add-req)" })),
        title: Type.Optional(Type.String({ description: "Change title (required for propose)" })),
        description: Type.Optional(Type.String({ description: "Change description (required for propose)" })),
        motivation: Type.Optional(Type.String({ description: "Change motivation (for propose)" })),
        impact: Type.Optional(Type.String({ description: "Impact description (for propose)" })),
        force: Type.Optional(Type.Boolean({ description: "Force overwrite (for scaffold)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const action = String(params.action || "list");
        const args = ["spec", action];
        if (params.changeId) args.push(String(params.changeId));
        if (action === "propose") {
          if (params.title) args.push("--title", String(params.title));
          if (params.description) args.push("--description", String(params.description));
          if (params.motivation) args.push("--motivation", String(params.motivation));
          if (params.impact) args.push("--impact", String(params.impact));
        }
        if (action === "scaffold" && params.force) args.push("--force");
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 6. super_dev_config - 配置管理
    // CLI: super-dev config <action> [key] [value]
    //   action: get | set | list (positional, required)
    api.registerTool({
      name: "super_dev_config",
      label: "Super Dev Config",
      description: "View or modify project configuration (super-dev.yaml). Actions: list, get, set.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: list, get, or set" }),
        key: Type.Optional(Type.String({ description: "Config key (for get/set)" })),
        value: Type.Optional(Type.String({ description: "Config value (for set)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["config", String(params.action || "list")];
        if (params.key) args.push(String(params.key));
        if (String(params.action) === "set" && params.value !== undefined) args.push(String(params.value));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 7. super_dev_review - 审查与门禁确认
    // CLI: super-dev review <type> [--status STATUS] [--comment COMMENT]
    //   type: docs, ui, architecture, quality
    //   status: pending_review, revision_requested, confirmed
    api.registerTool({
      name: "super_dev_review",
      label: "Super Dev Review",
      description:
        "Run a review or confirm a gate. Types: docs, ui, architecture, quality. " +
        "Pass status='confirmed' to approve a gate, 'revision_requested' to request changes.",
      parameters: Type.Object({
        type: Type.String({ description: "Review type: docs, ui, architecture, quality" }),
        status: Type.Optional(Type.String({ description: "Status: pending_review, revision_requested, confirmed" })),
        comment: Type.Optional(Type.String({ description: "Comment or feedback" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["review", String(params.type)];
        if (params.status) args.push("--status", String(params.status));
        if (params.comment) args.push("--comment", String(params.comment));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 8. super_dev_release - 发布管理
    // CLI: super-dev release <subcommand>
    //   readiness: 发布就绪度检查
    //   proof-pack: 生成交付证明包
    api.registerTool({
      name: "super_dev_release",
      label: "Super Dev Release",
      description: "Release management: 'readiness' to check release readiness, 'proof-pack' to generate delivery evidence.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: readiness or proof-pack" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(await invokeSuperDev(["release", String(params.action)], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 9. super_dev_expert - 专家咨询
    // CLI: super-dev expert <role> <prompt...>
    //   role: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA (positional)
    //   prompt: one or more words (positional, nargs=*)
    api.registerTool({
      name: "super_dev_expert",
      label: "Super Dev Expert",
      description: "Consult an expert. Roles: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA.",
      parameters: Type.Object({
        role: Type.String({ description: "Expert role: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA" }),
        question: Type.String({ description: "Question or topic for the expert" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const role = String(params.role);
        const question = String(params.question);
        // expert 的 prompt 是 nargs=*，加 -- 防止 question 中的 --flag 被 argparse 误解析
        const args = ["expert", role, "--", ...question.split(/\s+/).filter(Boolean)];
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 10. super_dev_deploy - 部署配置生成
    // CLI: super-dev deploy [--cicd PLATFORM] [--docker] [--rehearsal]
    api.registerTool({
      name: "super_dev_deploy",
      label: "Super Dev Deploy",
      description: "Generate deployment config: CI/CD pipelines, Dockerfile, and release rehearsal.",
      parameters: Type.Object({
        cicd: Type.Optional(Type.String({ description: "CI/CD platform: github, gitlab, jenkins, azure, bitbucket, all" })),
        docker: Type.Optional(Type.Boolean({ description: "Generate Dockerfile" })),
        rehearsal: Type.Optional(Type.Boolean({ description: "Generate release rehearsal checklist" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["deploy"];
        if (params.cicd) args.push("--cicd", String(params.cicd));
        if (params.docker) args.push("--docker");
        if (params.rehearsal) args.push("--rehearsal");
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 11. super_dev_analyze - 项目分析
    // CLI: super-dev analyze
    api.registerTool({
      name: "super_dev_analyze",
      label: "Super Dev Analyze",
      description: "Analyze the current project: detect tech stack, frameworks, dependencies, and project structure.",
      parameters: Type.Object({}),
      async execute(_id: string, _params: Record<string, unknown>) {
        return formatToolResult(await invokeSuperDev(["analyze"], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 12. super_dev_doctor - 环境诊断
    // CLI: super-dev doctor [--host HOST]
    api.registerTool({
      name: "super_dev_doctor",
      label: "Super Dev Doctor",
      description: "Run health check and diagnostics for host integration status.",
      parameters: Type.Object({
        host: Type.Optional(Type.String({ description: "Specific host to check (e.g. openclaw, claude-code)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["doctor"];
        if (params.host) args.push("--host", String(params.host));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 13. super_dev_governance - 治理管理
    // CLI: super-dev governance <action>
    api.registerTool({
      name: "super_dev_governance",
      label: "Super Dev Governance",
      description:
        "Governance management: view status, list rules, validate rules, generate knowledge report, manage ADR, view metrics, manage templates.",
      parameters: Type.Object({
        action: Type.String({
          description:
            "Subcommand: status, rules-list, rules-validate, knowledge-report, adr-generate, adr-list, metrics-show, templates-list",
        }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const action = String(params.action || "status");
        const actionMap: Record<string, string[]> = {
          "status": ["governance", "status"],
          "rules-list": ["governance", "rules", "list"],
          "rules-validate": ["governance", "rules", "validate"],
          "knowledge-report": ["governance", "knowledge-report"],
          "adr-generate": ["governance", "adr", "generate"],
          "adr-list": ["governance", "adr", "list"],
          "metrics-show": ["governance", "metrics", "show"],
          "templates-list": ["governance", "templates", "list"],
        };
        const args = actionMap[action] || ["governance", action];
        return formatToolResult(
          await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }),
        );
      },
    });

    // 14. super_dev_task - 任务管理
    // CLI: super-dev task <action> [change-id]
    api.registerTool({
      name: "super_dev_task",
      label: "Super Dev Task",
      description: "Manage spec tasks: list tasks, run task execution, check completion status.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: list, run, status" }),
        changeId: Type.Optional(Type.String({ description: "Change ID" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["task", String(params.action || "list")];
        if (params.changeId) args.push(String(params.changeId));
        return formatToolResult(
          await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }),
        );
      },
    });

    // 15. super_dev_fix - 缺陷修复
    // CLI: super-dev fix "<description>"
    api.registerTool({
      name: "super_dev_fix",
      label: "Super Dev Fix",
      description:
        "Start a lightweight bugfix pipeline. Skips research/docs, goes straight to spec -> implement -> quality.",
      parameters: Type.Object({
        description: Type.String({ description: "Bug description" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(
          await invokeSuperDev(["fix", String(params.description)], {
            cwd: cwd(),
            bin: bin(),
            timeout: timeout(),
          }),
        );
      },
    });

    // 16. super_dev_confirm - 快捷门禁确认
    // CLI: super-dev confirm <gate>
    api.registerTool({
      name: "super_dev_confirm",
      label: "Super Dev Confirm",
      description: "Quick confirm a gate: docs, ui, architecture, quality, preview.",
      parameters: Type.Object({
        gate: Type.String({ description: "Gate to confirm: docs, ui, architecture, quality, preview" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(
          await invokeSuperDev(["confirm", String(params.gate)], {
            cwd: cwd(),
            bin: bin(),
            timeout: timeout(),
          }),
        );
      },
    });

    // 17. super_dev_jump - 阶段跳转
    // CLI: super-dev jump <stage>
    api.registerTool({
      name: "super_dev_jump",
      label: "Super Dev Jump",
      description:
        "Jump to a specific pipeline stage: research, docs, spec, frontend, backend, quality, delivery.",
      parameters: Type.Object({
        stage: Type.String({ description: "Target stage name or number (1-9)" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(
          await invokeSuperDev(["jump", String(params.stage)], {
            cwd: cwd(),
            bin: bin(),
            timeout: timeout(),
          }),
        );
      },
    });

    // 18. super_dev_product_audit - 产品审查
    // CLI: super-dev product-audit
    api.registerTool({
      name: "super_dev_product_audit",
      label: "Super Dev Product Audit",
      description:
        "Run a comprehensive product audit: feature gaps, user journey completeness, delivery credibility.",
      parameters: Type.Object({}),
      async execute(_id: string, _params: Record<string, unknown>) {
        return formatToolResult(
          await invokeSuperDev(["product-audit"], { cwd: cwd(), bin: bin(), timeout: timeout() }),
        );
      },
    });

    // 19. super_dev_metrics - 度量查看
    // CLI: super-dev metrics [--format FORMAT]
    api.registerTool({
      name: "super_dev_metrics",
      label: "Super Dev Metrics",
      description: "View pipeline metrics, quality trends, and DORA indicators.",
      parameters: Type.Object({
        format: Type.Optional(Type.String({ description: "Output format: text, json" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["metrics"];
        if (params.format) args.push("--format", String(params.format));
        return formatToolResult(
          await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }),
        );
      },
    });

    // 20. super_dev_seeai - 赛事极速模式（SEEAI Competition Mode）
    // 一键进入30分钟极速交付流水线：compact research -> compact docs -> confirm -> compact spec -> full-stack sprint -> polish
    api.registerTool({
      name: "super_dev_seeai",
      label: "Super Dev SEEAI (Competition)",
      description:
        "Activate the SEEAI competition fast mode for time-boxed (30 min) high-quality showcase delivery. " +
        "Compresses the full pipeline into: fast research -> compact docs -> quick confirm -> sprint build -> polish. " +
        "Optimized for demo impact, not engineering completeness.",
      parameters: Type.Object({
        description: Type.String({ description: "Competition requirement or project idea" }),
        type: Type.Optional(Type.String({ description: "Project archetype: landing, game, tool, dashboard, saas, app" })),
        frontend: Type.Optional(Type.String({ description: "Frontend: react, vue, next, svelte" })),
        backend: Type.Optional(Type.String({ description: "Backend: node, python, go, none" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const desc = params.description;
        if (typeof desc !== "string" || !desc.trim()) {
          return formatToolResult({ stdout: "", stderr: "Missing required parameter: description", exitCode: 1 });
        }
        const args = ["create", desc, "--mode", "feature"];
        if (params.frontend) args.push("--frontend", String(params.frontend));
        if (params.backend) args.push("--backend", String(params.backend));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 21. super_dev_seeai_polish - 赛事演示打磨
    // 快速检查并提升作品的演示完成度：视觉效果、交互完整性、文案质量、演示路径验证
    api.registerTool({
      name: "super_dev_seeai_polish",
      label: "Super Dev SEEAI Polish",
      description:
        "Quick polish check for competition showcase: verify demo path works, check visual completeness, " +
        "fix placeholder content, ensure wow points land. Run this in the last 5 minutes before presentation.",
      parameters: Type.Object({
        focus: Type.Optional(Type.String({
          description: "Polish focus: visual (UI polish), content (copy/text), demo (demo path check), all (default)"
        })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const focus = String(params.focus || "all");
        const args = ["quality", "--type", "ui-review"];
        const result = await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() });
        // Append polish guidance
        const polishHints = [
          "\n--- SEEAI Polish Checklist ---",
          focus === "all" || focus === "visual" ? "\n[Visual] Check: no emoji icons, no purple/pink gradient, no hardcoded colors, dark mode OK" : "",
          focus === "all" || focus === "content" ? "\n[Content] Check: no placeholder text (Lorem ipsum), CTA text is specific, titles are catchy" : "",
          focus === "all" || focus === "demo" ? "\n[Demo] Check: main user path works end-to-end, no broken links, loading states show, empty states show" : "",
          "\n[WOW] Verify your single biggest wow point actually works and is immediately visible",
        ];
        const stdout = (result.stdout || "") + polishHints.join("");
        return formatToolResult({ ...result, stdout });
      },
    });

    // 22. super_dev_seeai_score - 赛事自评
    // 按比赛评审标准快速自评，给出分数和改进建议
    api.registerTool({
      name: "super_dev_seeai_score",
      label: "Super Dev SEEAI Score",
      description:
        "Self-evaluate your competition project against typical judging criteria: completeness, visual quality, " +
        "innovation, demo flow, and technical depth. Returns a score (0-100) with actionable improvement suggestions.",
      parameters: Type.Object({
        criteria: Type.Optional(Type.String({
          description: "Judging criteria to score against: general (default), innovation, design, tech, completeness"
        })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        // Run quality gate as the scoring base
        const qualityArgs = ["quality"];
        const qualityResult = await invokeSuperDev(qualityArgs, { cwd: cwd(), bin: bin(), timeout: timeout() });

        const scoringGuide = [
          "\n--- SEEAI Competition Self-Score ---",
          "\n[Judging Dimensions]",
          "  1. Completeness (25%): Does the main path work end-to-end? No dead buttons, no empty pages?",
          "  2. Visual Quality (25%): First impression strong? No template feel? Design tokens used? Dark mode?",
          "  3. Innovation / Wow (20%): Is there a clear 'wow' moment? Something memorable?",
          "  4. Demo Flow (15%): Can you present it in 2 minutes? Smooth transitions? Clear narrative?",
          "  5. Technical Depth (15%): Real data (not all mock)? Responsive? A11y basics?",
          "\n[Quick Wins if score < 70]",
          "  - Replace all placeholder text with real, topic-specific copy",
          "  - Add one clear hero animation or transition (even simple CSS)",
          "  - Make sure the main CTA/button does something real",
          "  - Add a result/completion screen at the end of the main flow",
          "  - Check: no console.errors, no 404s, no broken images",
          "\n[Anti-patterns that lose points]",
          "  - Purple/pink gradient hero (instant AI-template feel)",
          "  - Emoji used as icons",
          "  - Generic lorem ipsum or AI-boilerplate copy",
          "  - All features half-done instead of one feature fully done",
        ];

        const stdout = (qualityResult.stdout || "") + scoringGuide.join("");
        return formatToolResult({ ...qualityResult, stdout });
      },
    });

    // 23. super_dev_run - 通用透传（可选 tool，带子命令白名单）
    api.registerTool(
      {
        name: "super_dev_run",
        label: "Super Dev Run",
        description:
          "Run any super-dev CLI command directly. Use as fallback when no specialized tool fits. " +
          "Examples: 'run frontend', 'run --resume', 'fix \"bug description\"', 'repo-map', 'dependency-graph'.",
        parameters: Type.Object({
          command: Type.String({ description: "CLI command and args as string (e.g. 'run frontend', 'fix \"bug desc\"')" }),
        }),
        async execute(_id: string, params: Record<string, unknown>) {
          const raw = String(params.command || "");
          const parts = raw.split(/\s+/).filter(Boolean);
          if (parts.length === 0) {
            return formatToolResult({ stdout: "", stderr: "Empty command", exitCode: 1 });
          }
          if (!ALLOWED_SUBCOMMANDS.has(parts[0])) {
            return formatToolResult({ stdout: "", stderr: `Unknown subcommand: ${parts[0]}. Use 'super-dev --help' for available commands.`, exitCode: 1 });
          }
          return formatToolResult(await invokeSuperDev(parts, { cwd: cwd(), bin: bin(), timeout: timeout() }));
        },
      },
      { optional: true },
    );
  },
});
