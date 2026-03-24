/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：应用根组件
 * 作用：整合各业务模块并提供顶层路由布局
 * 创建时间：2026-03-24
 * 最后修改：2026-03-24
 */

import React, { useState } from 'react';
import Auth from './modules/auth';
import Content from './modules/content';
import Profile from './modules/profile';
import Analytics from './modules/analytics';
import Workflow from './modules/workflow';
import Core from './modules/core';
import Experience from './modules/experience';
import Operation from './modules/operation';

const modules: Record<string, React.FC> = {
  core: Core,
  auth: Auth,
  content: Content,
  profile: Profile,
  analytics: Analytics,
  workflow: Workflow,
  experience: Experience,
  operation: Operation,
};

export default function App() {
  const [active, setActive] = useState('core');
  const ActiveModule = modules[active] || Core;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <nav style={{ width: 200, padding: 16, borderRight: '1px solid #e5e7eb' }}>
        <h2 style={{ margin: '0 0 16px' }}>Super Dev</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {Object.keys(modules).map((key) => (
            <li key={key} style={{ marginBottom: 8 }}>
              <button
                onClick={() => setActive(key)}
                aria-current={active === key ? 'page' : undefined}
                style={{
                  background: active === key ? '#e0e7ff' : 'transparent',
                  border: 'none',
                  padding: '8px 12px',
                  cursor: 'pointer',
                  width: '100%',
                  textAlign: 'left',
                  borderRadius: 4,
                }}
              >
                {key}
              </button>
            </li>
          ))}
        </ul>
      </nav>
      <main style={{ flex: 1, padding: 24 }}>
        <ActiveModule />
      </main>
    </div>
  );
}
