/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：OpenClaw 插件入口
 * 作用：通过 definePluginEntry 注册所有 Super Dev 工具到 OpenClaw Agent
 * 创建时间：2026-03-24
 * 最后修改：2026-03-24
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";
import { invokeSuperDev, formatToolResult } from "./utils/subprocess";
import { resolvePluginConfig } from "./types";

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
    api.registerTool({
      name: "super_dev_pipeline",
      label: "Super Dev Pipeline",
      description:
        "Start the Super Dev pipeline: research -> PRD -> architecture -> UIUX -> spec -> frontend -> backend -> quality -> delivery.",
      parameters: Type.Object({
        requirement: Type.String({ description: "Project or feature requirement description" }),
        name: Type.Optional(Type.String({ description: "Project name" })),
        frontend: Type.Optional(Type.String({ description: "Frontend: next, react-vite, vue-vite, nuxt, remix, angular, sveltekit" })),
        backend: Type.Optional(Type.String({ description: "Backend: node, python, go, java, rust, php" })),
        platform: Type.Optional(Type.String({ description: "Platform: web, mobile, wechat, desktop" })),
        domain: Type.Optional(Type.String({ description: "Domain: fintech, ecommerce, medical, social, iot, education" })),
        mode: Type.Optional(Type.String({ description: "Mode: feature or bugfix" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["pipeline", params.requirement as string];
        if (params.name) args.push("--name", params.name as string);
        if (params.frontend) args.push("--frontend", params.frontend as string);
        if (params.backend) args.push("--backend", params.backend as string);
        if (params.platform) args.push("--platform", params.platform as string);
        if (params.domain) args.push("--domain", params.domain as string);
        if (params.mode) args.push("--mode", params.mode as string);
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 2. super_dev_init - 项目初始化
    api.registerTool({
      name: "super_dev_init",
      label: "Super Dev Init",
      description: "Initialize Super Dev in an existing project. Creates super-dev.yaml.",
      parameters: Type.Object({
        frontend: Type.Optional(Type.String({ description: "Frontend framework" })),
        backend: Type.Optional(Type.String({ description: "Backend framework" })),
        platform: Type.Optional(Type.String({ description: "Platform type" })),
        domain: Type.Optional(Type.String({ description: "Business domain" })),
        name: Type.Optional(Type.String({ description: "Project name" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["init"];
        if (params.frontend) args.push("--frontend", params.frontend as string);
        if (params.backend) args.push("--backend", params.backend as string);
        if (params.platform) args.push("--platform", params.platform as string);
        if (params.domain) args.push("--domain", params.domain as string);
        if (params.name) args.push("--name", params.name as string);
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 3. super_dev_status - 状态查看
    api.registerTool({
      name: "super_dev_status",
      label: "Super Dev Status",
      description: "Check pipeline status: completed phases and existing outputs.",
      parameters: Type.Object({}),
      async execute() {
        return formatToolResult(await invokeSuperDev(["status"], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 4. super_dev_quality - 质量门禁
    api.registerTool({
      name: "super_dev_quality",
      label: "Super Dev Quality",
      description: "Run the quality gate check on documentation, code, security, and architecture.",
      parameters: Type.Object({
        threshold: Type.Optional(Type.Number({ description: "Quality score threshold (0-100)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["quality"];
        if (params.threshold !== undefined) args.push("--threshold", String(params.threshold));
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 5. super_dev_spec - Spec 管理
    api.registerTool({
      name: "super_dev_spec",
      label: "Super Dev Spec",
      description: "Manage specs: list, show, propose, scaffold, validate.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: list, show, propose, scaffold, validate" }),
        specId: Type.Optional(Type.String({ description: "Spec or change ID" })),
        requirement: Type.Optional(Type.String({ description: "Requirement description (for propose)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["spec", params.action as string];
        if (params.specId) args.push(params.specId as string);
        if (params.requirement) args.push(params.requirement as string);
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 6. super_dev_config - 配置管理
    api.registerTool({
      name: "super_dev_config",
      label: "Super Dev Config",
      description: "View or modify project configuration (super-dev.yaml). Actions: list, get, set.",
      parameters: Type.Object({
        action: Type.Optional(Type.String({ description: "Subcommand: list (default), get, set" })),
        key: Type.Optional(Type.String({ description: "Config key" })),
        value: Type.Optional(Type.String({ description: "Config value (for set)" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["config", (params.action as string) ?? "list"];
        if (params.key) args.push(params.key as string);
        if ((params.action as string) === "set" && params.value) args.push(params.value as string);
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 7. super_dev_review - 审查
    api.registerTool({
      name: "super_dev_review",
      label: "Super Dev Review",
      description: "Run a targeted review or confirm a gate. Types: docs, ui, architecture, quality. Pass status='confirmed' to approve a gate.",
      parameters: Type.Object({
        type: Type.String({ description: "Review type: docs, ui, architecture, quality" }),
        status: Type.Optional(Type.String({ description: "Set status: confirmed, revision_requested" })),
        comment: Type.Optional(Type.String({ description: "Comment for the review action" })),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        const args = ["review", params.type as string];
        if (params.status) args.push("--status", params.status as string);
        if (params.comment) args.push("--comment", params.comment as string);
        return formatToolResult(await invokeSuperDev(args, { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 8. super_dev_release - 发布管理
    api.registerTool({
      name: "super_dev_release",
      label: "Super Dev Release",
      description: "Release management: check readiness or generate proof-pack.",
      parameters: Type.Object({
        action: Type.String({ description: "Subcommand: readiness or proof-pack" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(await invokeSuperDev(["release", params.action as string], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 9. super_dev_expert - 专家咨询
    api.registerTool({
      name: "super_dev_expert",
      label: "Super Dev Expert",
      description: "Consult an expert: PM, ARCHITECT, UI, UX, SECURITY, CODE, DBA, QA, DEVOPS, RCA.",
      parameters: Type.Object({
        role: Type.String({ description: "Expert role" }),
        question: Type.String({ description: "Question for the expert" }),
      }),
      async execute(_id: string, params: Record<string, unknown>) {
        return formatToolResult(await invokeSuperDev(["expert", params.role as string, params.question as string], { cwd: cwd(), bin: bin(), timeout: timeout() }));
      },
    });

    // 10. super_dev_run - 通用透传（可选 tool）
    api.registerTool(
      {
        name: "super_dev_run",
        label: "Super Dev Run",
        description: "Run any super-dev CLI command directly (e.g. 'run frontend', 'deploy --platform github').",
        parameters: Type.Object({
          command: Type.String({ description: "CLI command string (e.g. 'run frontend')" }),
        }),
        async execute(_id: string, params: Record<string, unknown>) {
          const parts = (params.command as string).split(/\s+/).filter(Boolean);
          return formatToolResult(await invokeSuperDev(parts, { cwd: cwd(), bin: bin(), timeout: timeout() }));
        },
      },
      { optional: true },
    );
  },
});
