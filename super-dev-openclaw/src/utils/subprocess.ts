/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：CLI 桥接工具
 * 作用：封装 child_process.execFile 调用 super-dev Python CLI
 * 创建时间：2026-03-24
 * 最后修改：2026-03-24
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export interface SuperDevResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface InvokeOptions {
  cwd: string;
  bin?: string;
  timeout?: number;
  env?: Record<string, string>;
}

/**
 * 调用 super-dev CLI 并返回结果
 *
 * @param args - CLI 参数数组，如 ["pipeline", "需求描述", "--frontend", "next"]
 * @param options - 工作目录、二进制路径、超时时间
 */
export async function invokeSuperDev(
  args: string[],
  options: InvokeOptions
): Promise<SuperDevResult> {
  const bin = options.bin ?? "super-dev";
  const timeout = options.timeout ?? 300000;

  try {
    const { stdout, stderr } = await execFileAsync(bin, args, {
      cwd: options.cwd,
      timeout,
      maxBuffer: 10 * 1024 * 1024,
      env: {
        ...process.env,
        ...options.env,
        SUPER_DEV_OUTPUT_MODE: "auto",
      },
    });
    return { stdout, stderr, exitCode: 0 };
  } catch (error: unknown) {
    if (error instanceof Error) {
      const execError = error as Error & {
        stdout?: string;
        stderr?: string;
        status?: number | null;
        code?: string;
      };
      return {
        stdout: execError.stdout ?? "",
        stderr: execError.stderr ?? error.message,
        exitCode: typeof execError.status === "number" ? execError.status : 1,
      };
    }
    return {
      stdout: "",
      stderr: String(error),
      exitCode: 1,
    };
  }
}

/**
 * 将 SuperDevResult 格式化为 OpenClaw Tool 返回格式
 */
export function formatToolResult(result: SuperDevResult): {
  content: Array<{ type: "text"; text: string }>;
  details: { exitCode: number };
} {
  const text =
    result.exitCode === 0
      ? result.stdout || result.stderr || "(no output)"
      : `[exit code ${result.exitCode}]\n${result.stderr}\n${result.stdout}`.trim();

  return {
    content: [{ type: "text", text }],
    details: { exitCode: result.exitCode },
  };
}
