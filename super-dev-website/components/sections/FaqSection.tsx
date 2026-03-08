'use client';
/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：FAQ 折叠问答组件
 * 作用：展示常见问题，支持键盘访问的折叠交互
 * 创建时间：2026-03-08
 * 最后修改：2026-03-08
 */
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { FAQ_ITEMS } from '@/lib/constants';

interface FaqItemProps {
  question: string;
  answer: string;
  isOpen: boolean;
  onToggle: () => void;
  id: string;
}

function FaqItem({ question, answer, isOpen, onToggle, id }: FaqItemProps) {
  return (
    <div className="border-b border-border-muted last:border-0">
      <h3>
        <button
          id={`faq-btn-${id}`}
          aria-expanded={isOpen}
          aria-controls={`faq-content-${id}`}
          onClick={onToggle}
          className={cn(
            'w-full flex items-center justify-between py-5 text-left',
            'text-base font-medium transition-colors duration-150',
            isOpen ? 'text-text-primary' : 'text-text-secondary hover:text-text-primary'
          )}
        >
          {question}
          <ChevronDown
            size={18}
            aria-hidden="true"
            className={cn(
              'shrink-0 ml-4 text-text-muted transition-transform duration-200',
              isOpen && 'rotate-180'
            )}
          />
        </button>
      </h3>

      <div
        id={`faq-content-${id}`}
        role="region"
        aria-labelledby={`faq-btn-${id}`}
        className={cn(
          'overflow-hidden transition-all duration-200',
          isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <p className="pb-5 text-sm text-text-secondary leading-relaxed">{answer}</p>
      </div>
    </div>
  );
}

export function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  function handleToggle(index: number) {
    setOpenIndex((prev) => (prev === index ? null : index));
  }

  return (
    <section
      className="py-20 lg:py-28 bg-bg-secondary"
      aria-labelledby="faq-title"
    >
      <div className="max-w-2xl mx-auto px-4 sm:px-6">
        {/* 标题区 */}
        <div className="text-center mb-12">
          <h2
            id="faq-title"
            className="text-3xl sm:text-4xl font-bold text-text-primary mb-4 tracking-tight"
          >
            常见问题
          </h2>
          <p className="text-text-secondary">
            还有疑问？在{' '}
            <a
              href="https://github.com/shangyankeji/super-dev/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-blue hover:text-accent-blue-hover transition-colors"
            >
              GitHub Issues
            </a>{' '}
            提问。
          </p>
        </div>

        {/* FAQ 列表 */}
        <div role="list">
          {FAQ_ITEMS.map((item, index) => (
            <div key={item.question} role="listitem">
              <FaqItem
                id={String(index)}
                question={item.question}
                answer={item.answer}
                isOpen={openIndex === index}
                onToggle={() => handleToggle(index)}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
