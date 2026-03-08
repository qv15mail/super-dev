'use client';
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { SiteLocale } from '@/lib/site-locale';

const FAQ_ITEMS = {
  zh: [
    {
      question: '宿主和 Super Dev 的关系到底是什么？',
      answer: '宿主负责模型、联网、调用工具、改代码和运行项目。Super Dev 负责研究顺序、三文档、确认门、前端运行验证、质量门禁和交付标准。两者不是竞争关系，而是执行层和治理层的关系。',
    },
    {
      question: '为什么它不是一个提示词模板？',
      answer: '提示词模板只能影响当前对话，不能稳定安装到宿主协议面，也不能持续维护确认门、运行验证、质量门禁、交付状态和 release readiness。Super Dev 是一个 Python CLI + 宿主接入面 + 产物治理系统。',
    },
    {
      question: '为什么它不是一个 spec 工具？',
      answer: 'Spec 工具主要规范项目规格。Super Dev 规范的是宿主里的 AI 开发过程，从 research、三文档、Spec、前后端、测试到交付都在同一条流水线上，而不是只停在规格阶段。',
    },
    {
      question: '宿主不支持 slash 时怎么工作？',
      answer: '这类宿主使用 super-dev: 作为文本触发词，再通过 AGENTS、rules、steering 或 skills 等官方接入面理解并执行 Super Dev 流程。用户记住触发方式即可，不需要自己处理底层协议。',
    },
  ],
  en: [
    {
      question: 'What is the relationship between the host and Super Dev?',
      answer: 'The host handles the model, browsing, tool calls, file edits, and runtime execution. Super Dev handles research order, the three core docs, approval gates, frontend runtime validation, quality gates, and delivery standards. They are execution and governance layers, not competitors.',
    },
    {
      question: 'Why is this not just a prompt template?',
      answer: 'A prompt template only affects one conversation. It does not install into host protocol surfaces, and it cannot persist approval gates, runtime validation, quality gates, delivery state, or release readiness. Super Dev is a Python CLI plus host integration surfaces plus artifact governance.',
    },
    {
      question: 'Why is this not just a spec tool?',
      answer: 'Spec tools mainly govern project specs. Super Dev governs the AI development process inside the host, covering research, the three core docs, spec, frontend, backend, testing, and delivery in one governed path.',
    },
    {
      question: 'How does it work when the host does not support slash commands?',
      answer: 'Those hosts use super-dev: as the text trigger, then rely on AGENTS, rules, steering, or skills to interpret and execute the Super Dev flow. The user only needs to remember the trigger, not the underlying protocol details.',
    },
  ],
} as const;

const COPY = {
  zh: { title: '常见问题', body: '这些问题回答的是定位和工作方式，不是语法细节。' },
  en: { title: 'FAQ', body: 'These answers explain positioning and operating model, not just syntax.' },
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
          className={cn('flex w-full items-center justify-between py-5 text-left', 'text-base font-medium transition-colors duration-150', isOpen ? 'text-text-primary' : 'text-text-secondary hover:text-text-primary')}
        >
          {question}
          <ChevronDown size={18} aria-hidden="true" className={cn('ml-4 shrink-0 text-text-muted transition-transform duration-200', isOpen && 'rotate-180')} />
        </button>
      </h3>
      <div id={`faq-content-${id}`} role="region" aria-labelledby={`faq-btn-${id}`} className={cn('overflow-hidden transition-all duration-200', isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0')}>
        <p className="pb-5 text-sm leading-7 text-text-secondary">{answer}</p>
      </div>
    </div>
  );
}

export function FaqSection({ locale = 'zh' }: { locale?: SiteLocale }) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const copy = COPY[locale];
  function handleToggle(index: number) {
    setOpenIndex((prev) => (prev === index ? null : index));
  }

  return (
    <section className="border-b border-border-muted bg-bg-secondary py-20 lg:py-24" aria-labelledby="faq-title">
      <div className="mx-auto max-w-3xl px-4 sm:px-6">
        <div className="mb-12 max-w-2xl">
          <h2 id="faq-title" className="text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{copy.title}</h2>
          <p className="mt-4 text-lg leading-8 text-text-secondary">{copy.body}</p>
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
