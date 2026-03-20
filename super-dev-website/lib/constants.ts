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
  status: HostStatus;
  abbr: string;
  trigger: HostTriggerMode;
  protocol: string;
}

export const HOSTS: Host[] = [
  { name: 'Antigravity', abbr: 'A', status: 'compatible', trigger: 'slash', protocol: 'commands + GEMINI.md + workflows' },
  { name: 'Claude Code', abbr: 'C', status: 'certified', trigger: 'slash', protocol: 'commands + subagents' },
  { name: 'CodeBuddy CLI', abbr: 'C', status: 'compatible', trigger: 'slash', protocol: 'commands + skills' },
  { name: 'CodeBuddy', abbr: 'C', status: 'experimental', trigger: 'slash', protocol: 'commands + skills' },
  { name: 'Codex CLI', abbr: 'C', status: 'certified', trigger: 'text', protocol: 'AGENTS.md + skills' },
  { name: 'Cursor CLI', abbr: 'C', status: 'compatible', trigger: 'slash', protocol: 'commands + rules' },
  { name: 'Cursor', abbr: 'C', status: 'experimental', trigger: 'slash', protocol: 'commands + rules' },
  { name: 'Gemini CLI', abbr: 'G', status: 'compatible', trigger: 'slash', protocol: 'commands + GEMINI.md' },
  { name: 'Kiro CLI', abbr: 'K', status: 'compatible', trigger: 'slash', protocol: 'commands + AGENTS.md' },
  { name: 'Kiro', abbr: 'K', status: 'experimental', trigger: 'text', protocol: 'project steering + global steering' },
  { name: 'OpenCode', abbr: 'O', status: 'experimental', trigger: 'slash', protocol: 'commands + skills' },
  { name: 'Qoder CLI', abbr: 'Q', status: 'compatible', trigger: 'slash', protocol: 'commands + skills' },
  { name: 'Qoder', abbr: 'Q', status: 'experimental', trigger: 'slash', protocol: 'commands + rules + skills' },
  { name: 'VS Code Copilot', abbr: 'V', status: 'experimental', trigger: 'text', protocol: 'copilot-instructions + AGENTS.md' },
  { name: 'Windsurf', abbr: 'W', status: 'experimental', trigger: 'slash', protocol: 'workflows + skills' },
  { name: 'Trae', abbr: 'T', status: 'compatible', trigger: 'text', protocol: 'project rules + compatibility skill' },
];

export const SLASH_HOSTS = HOSTS.filter((host) => host.trigger === 'slash');
export const TEXT_TRIGGER_HOSTS = HOSTS.filter((host) => host.trigger === 'text');

export const STATS = {
  zh: [
    { value: '16', label: '主推宿主' },
    { value: '12', label: '流水线阶段' },
    { value: '3', label: '关键门禁' },
    { value: 'MIT', label: '开源许可' },
  ],
  en: [
    { value: '16', label: 'Primary hosts' },
    { value: '12', label: 'Pipeline phases' },
    { value: '3', label: 'Critical gates' },
    { value: 'MIT', label: 'License' },
  ],
} as const;

export const TERMINAL_LINES = {
  zh: [
    { type: 'input', text: 'pip install -U super-dev' },
    { type: 'output', text: 'Collecting super-dev' },
    { type: 'output', text: 'Installing collected packages: super-dev' },
    { type: 'success', text: 'Successfully installed super-dev-2.0.11' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev' },
    { type: 'blank', text: '' },
    { type: 'brand', text: 'Super Dev v2.0.11 — 让 AI 开发更标准地完成商业交付' },
    { type: 'info', text: 'Select hosts and write protocol surfaces...' },
    { type: 'output', text: 'claude-code    /super-dev' },
    { type: 'output', text: 'cursor         /super-dev' },
    { type: 'output', text: 'trae           super-dev:' },
    { type: 'blank', text: '' },
    { type: 'input', text: '/super-dev 开发一个可交付的项目' },
    { type: 'info', text: 'Phase 01 → research, then PRD / Architecture / UI/UX, then wait for confirmation.' },
  ],
  en: [
    { type: 'input', text: 'pip install -U super-dev' },
    { type: 'output', text: 'Collecting super-dev' },
    { type: 'output', text: 'Installing collected packages: super-dev' },
    { type: 'success', text: 'Successfully installed super-dev-2.0.11' },
    { type: 'blank', text: '' },
    { type: 'input', text: 'super-dev' },
    { type: 'blank', text: '' },
    { type: 'brand', text: 'Super Dev v2.0.11 — Governed delivery for AI coding' },
    { type: 'info', text: 'Select hosts and write protocol surfaces...' },
    { type: 'output', text: 'claude-code    /super-dev' },
    { type: 'output', text: 'cursor         /super-dev' },
    { type: 'output', text: 'trae           super-dev:' },
    { type: 'blank', text: '' },
    { type: 'input', text: '/super-dev Build a shippable product' },
    { type: 'info', text: 'Phase 01 → research, then PRD / Architecture / UI/UX, then wait for confirmation.' },
  ],
} as const;
