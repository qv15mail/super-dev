/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：OpenClaw 插件入口
 * 作用：通过 definePluginEntry 注册 Super Dev Tool 到 OpenClaw Agent
 * 创建时间：2026-03-24
 * 最后修改：2026-03-25
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
        // expert 的 prompt 是 nargs=*，需要按空格拆分传入
        const args = ["expert", role, ...question.split(/\s+/).filter(Boolean)];
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

    // 13. super_dev_run - 通用透传（可选 tool，带子命令白名单）
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
