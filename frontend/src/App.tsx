import React from 'react';
import Core from './modules/core';
import Content from './modules/content';

export default function App() {
  return (
    <main style={{maxWidth: 960, margin: '40px auto', fontFamily: "'Plus Jakarta Sans','Noto Sans SC','PingFang SC','Segoe UI',sans-serif"}}>
      <h1>super-dev 实现骨架</h1>
      <p>该页面由 Super Dev 自动生成，按模块分区承接需求实现。</p>
      <div style={{display: 'grid', gap: 12}}>
        <section style={{border: '1px solid #e5e7eb', borderRadius: 12, padding: 16}}>
          <h3>Core</h3>
          <Core />
        </section>
        <section style={{border: '1px solid #e5e7eb', borderRadius: 12, padding: 16}}>
          <h3>Content</h3>
          <Content />
        </section>
      </div>
    </main>
  );
}
