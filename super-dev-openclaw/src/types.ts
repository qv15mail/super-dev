/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：插件类型定义
 * 作用：定义与 OpenClaw Plugin SDK 兼容的类型接口
 * 创建时间：2026-03-24
 * 最后修改：2026-03-24
 */

/** 插件配置（对应 openclaw.plugin.json configSchema） */
export interface SuperDevPluginConfig {
  projectDir?: string;
  superDevBin?: string;
  qualityThreshold?: number;
  timeout?: number;
  language?: "zh" | "en";
}

/**
 * 从 OpenClaw SDK 的 pluginConfig（Record<string, unknown> | undefined）
 * 安全提取为 SuperDevPluginConfig
 */
export function resolvePluginConfig(
  raw: Record<string, unknown> | undefined
): SuperDevPluginConfig {
  if (!raw) return {};
  return {
    projectDir: typeof raw.projectDir === "string" ? raw.projectDir : undefined,
    superDevBin: typeof raw.superDevBin === "string" ? raw.superDevBin : undefined,
    qualityThreshold: typeof raw.qualityThreshold === "number" ? raw.qualityThreshold : undefined,
    timeout: typeof raw.timeout === "number" ? raw.timeout : undefined,
    language: raw.language === "zh" || raw.language === "en" ? raw.language : undefined,
  };
}
