'use client';
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SiteLocale } from '@/lib/site-locale';

const FAQ_ITEMS = {
  zh: [
    {
      question: 'Super Dev 和 Cursor、Claude Code 是竞争关系吗？',
      answer: '不是。Super Dev 是它们的流程治理层，与任何 AI 编码工具互补而非竞争。你用宿主写代码，Super Dev 确保这些代码满足商业交付标准。',
    },
    {
      question: '需要有特定的 AI 工具才能使用吗？',
      answer: '支持多类主流 AI 宿主工具，包括 Claude Code、Cursor、Windsurf、Gemini CLI 等。你用什么工具，就在那个工具里触发 Super Dev。',
    },
    {
      question: '什么是用户确认门？',
      answer: '三文档（PRD + 架构 + UI/UX）完成后必须暂停等待人工确认，未确认不得进入编码。这能避免宿主在错误方向上继续生成。',
    },
    {
      question: '如何安装和更新？',
      answer: '安装使用 pip install -U super-dev 或 uv tool install super-dev。更新直接使用 super-dev update。',
    },
  ],
  en: [
    {
      question: 'Is Super Dev competing with Cursor or Claude Code?',
      answer: 'No. Super Dev is the governance layer inside those hosts. The host writes and runs code; Super Dev makes sure the work follows a commercial delivery pipeline.',
    },
    {
      question: 'Do I need a specific AI coding tool to use it?',
      answer: 'Super Dev supports multiple mainstream AI hosts such as Claude Code, Cursor, Windsurf, Gemini CLI, Codex CLI, and more. You trigger it inside the host you already use.',
    },
    {
      question: 'What is the document confirmation gate?',
      answer: 'After PRD, Architecture, and UI/UX docs are generated, the pipeline must pause for explicit user confirmation. Without confirmation, coding cannot continue.',
    },
    {
      question: 'How do installation and updates work?',
      answer: 'Install with pip install -U super-dev or uv tool install super-dev. Update with super-dev update.',
    },
  ],
} as const;

const COPY = {
  zh: { title: '常见问题', body: '还有疑问？在', issues: 'GitHub Issues', tail: '提问。' },
  en: { title: 'FAQ', body: 'Still have questions? Ask in', issues: 'GitHub Issues', tail: '.' },
} as const;

function FaqItem({ question, answer, isOpen, onToggle, id }: { question: string; answer: string; isOpen: boolean; onToggle: () => void; id: string; }) {
  return (
    <div className="border-b border-border-muted last:border-0">
      <h3>
        <button
          id={`faq-btn-${id}`}
          aria-expanded={isOpen}
          aria-controls={`faq-content-${id}`}
          onClick={onToggle}
          className={cn('w-full flex items-center justify-between py-5 text-left', 'text-base font-medium transition-colors duration-150', isOpen ? 'text-text-primary' : 'text-text-secondary hover:text-text-primary')}
        >
          {question}
          <ChevronDown size={18} aria-hidden="true" className={cn('shrink-0 ml-4 text-text-muted transition-transform duration-200', isOpen && 'rotate-180')} />
        </button>
      </h3>
      <div id={`faq-content-${id}`} role="region" aria-labelledby={`faq-btn-${id}`} className={cn('overflow-hidden transition-all duration-200', isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0')}>
        <p className="pb-5 text-sm text-text-secondary leading-relaxed">{answer}</p>
      </div>
    </div>
  );
}

export function FaqSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const copy = COPY[locale];
  function handleToggle(index: number) { setOpenIndex((prev) => (prev === index ? null : index)); }
  return (
    <section className="py-20 lg:py-28 bg-bg-secondary" aria-labelledby="faq-title">
      <div className="max-w-2xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <h2 id="faq-title" className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight">{copy.title}</h2>
          <p className="text-text-secondary">
            {copy.body}{' '}
            <a href="https://github.com/shangyankeji/super-dev/issues" target="_blank" rel="noopener noreferrer" className="text-accent-blue hover:text-accent-blue-hover transition-colors">{copy.issues}</a>
            {copy.tail}
          </p>
        </div>
        <div role="list">
          {FAQ_ITEMS[locale].map((item, index) => (
            <div key={item.question} role="listitem">
              <FaqItem id={String(index)} question={item.question} answer={item.answer} isOpen={openIndex === index} onToggle={() => handleToggle(index)} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
