/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：全局静态数据常量
 * 作用：宿主列表、站点统计与演示数据
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */

export type HostStatus = 'certified' | 'compatible' | 'experimental';
export type HostTriggerMode = 'slash' | 'text';

export interface Host {
  name: string;
  integration: HostStatus;
  runtime: HostStatus;
  abbr: string;
  trigger: HostTriggerMode;
  protocol: string;
}

export const HOSTS: Host[] = [
  { name: 'Antigravity', abbr: 'A', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'commands + GEMINI.md + workflows' },
  { name: 'Claude Code', abbr: 'C', integration: 'certified', runtime: 'compatible', trigger: 'slash', protocol: 'CLAUDE.md + skills + optional plugin' },
  { name: 'CodeBuddy CLI', abbr: 'C', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'CODEBUDDY.md + commands + skills' },
  { name: 'CodeBuddy', abbr: 'C', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'CODEBUDDY.md + rules + commands + agents + skills' },
  { name: 'Codex', abbr: 'C', integration: 'certified', runtime: 'compatible', trigger: 'slash', protocol: 'AGENTS.md + skills + repo plugin' },
  { name: 'Cursor CLI', abbr: 'C', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'commands + rules' },
  { name: 'Cursor', abbr: 'C', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'commands + rules' },
  { name: 'Gemini CLI', abbr: 'G', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'commands + GEMINI.md' },
  { name: 'Kiro CLI', abbr: 'K', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'steering slash entry + skills' },
  { name: 'Kiro', abbr: 'K', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'project steering + global steering + skills' },
  { name: 'OpenCode', abbr: 'O', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'commands + skills' },
  { name: 'Qoder CLI', abbr: 'Q', integration: 'compatible', runtime: 'experimental', trigger: 'slash', protocol: 'AGENTS.md + rules + commands + skills' },
  { name: 'Qoder', abbr: 'Q', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'AGENTS.md + rules + commands + skills' },
  { name: 'GitHub Copilot', abbr: 'G', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: 'copilot-instructions + AGENTS.md' },
  { name: 'Windsurf', abbr: 'W', integration: 'experimental', runtime: 'experimental', trigger: 'slash', protocol: 'workflows + skills' },
  { name: 'Trae', abbr: 'T', integration: 'compatible', runtime: 'experimental', trigger: 'text', protocol: 'project rules + compatibility skill' },
  { name: 'Copilot CLI', abbr: 'C', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: 'copilot-instructions + AGENTS' },
  { name: 'Roo Code', abbr: 'R', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: 'commands + rules + custom modes' },
  { name: 'Kilo Code', abbr: 'K', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: 'rules + compatibility skill' },
  { name: 'Cline', abbr: 'C', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: '.clinerules + skills + AGENTS' },
  { name: 'WorkBuddy', abbr: 'W', integration: 'experimental', runtime: 'experimental', trigger: 'text', protocol: 'Skills + MCP' },
];

export const SLASH_HOSTS = HOSTS.filter((host) => host.trigger === 'slash');
export const TEXT_TRIGGER_HOSTS = HOSTS.filter((host) => host.trigger === 'text');

export const STATS = {
  zh: [
    { value: '21+1', label: '宿主接入' },
    { value: '10', label: '专家 Agent' },
    { value: '9', label: '流水线阶段' },
    { value: '119', label: '配色方案' },
  ],
  en: [
    { value: '21+1', label: 'Host integrations' },
    { value: '10', label: 'Expert agents' },
    { value: '9', label: 'Pipeline stages' },
    { value: '119', label: 'Color palettes' },
  ],
} as const;

export const TERMINAL_LINES = {
  zh: [
    { type: 'input', text: 'pip install -U super-dev' },
    { type: 'output', text: 'Collecting super-dev' },
    { type: 'output', text: 'Installing collected packages: super-dev' },
    { type: 'success', text: 'Successfully installed super-dev-2.3.8' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev' },
    { type: 'brand', text: 'Super Dev 安装器 — 终端只负责接入与升级' },
    { type: 'info', text: 'Detected hosts: Claude Code, Codex, Cursor CLI' },
    { type: 'info', text: 'Recommended host: Codex' },
    { type: 'info', text: 'Writing project protocol + global protocol surfaces' },
    { type: 'blank', text: '' },
    { type: 'output', text: 'Next in host: /super-dev 或 super-dev:' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev update' },
    { type: 'info', text: 'Upgrading Super Dev and migrating onboarded hosts' },
    { type: 'success', text: 'Upgrade complete. Reopen your host and continue there.' },
  ],
  en: [
    { type: 'input', text: 'pip install -U super-dev' },
    { type: 'output', text: 'Collecting super-dev' },
    { type: 'output', text: 'Installing collected packages: super-dev' },
    { type: 'success', text: 'Successfully installed super-dev-2.3.8' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev' },
    { type: 'brand', text: 'Super Dev installer — terminal only handles onboarding and upgrade' },
    { type: 'info', text: 'Detected hosts: Claude Code, Codex, Cursor CLI' },
    { type: 'info', text: 'Recommended host: Codex' },
    { type: 'info', text: 'Writing project and global protocol surfaces' },
    { type: 'blank', text: '' },
    { type: 'output', text: 'Next in host: /super-dev or super-dev:' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev update' },
    { type: 'info', text: 'Upgrading Super Dev and migrating onboarded hosts' },
    { type: 'success', text: 'Upgrade complete. Reopen your host and continue there.' },
  ],
} as const;
