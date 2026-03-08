# Super Dev Website Docs Design

## Goal

Add a standalone `/docs` page to the website without changing the existing visual language. The page should feel like product documentation rather than marketing copy, while still matching the current dark industrial style, spacing rhythm, and component vocabulary.

## Information Architecture

Recommended single-page docs hub:

1. Overview
2. Quick Start
3. Installation
4. Host Matrix
5. Trigger Model
6. Pipeline
7. Local Knowledge Base
8. Review / Quality / Delivery Gates
9. Core Commands
10. Release / Update
11. Troubleshooting

This structure matches how users actually adopt the tool:

- understand what it is
- install it
- know which host to use
- know how to trigger it
- understand the pipeline
- learn the commands that unblock them

## UI Structure

Use a three-column layout on desktop:

1. Left sticky section navigation
2. Main content column with structured cards and code blocks
3. Right sticky “quick actions” / shortcuts panel

On mobile, collapse into a single content column with the quick actions moved near the top.

## Interaction Rules

- The top nav “文档” entry should point to `/docs`
- Footer “文档” should also point to `/docs`
- The page should use section anchors for fast navigation
- Code examples should use the existing `CodeBlock` component
- Host matrix should clearly separate `/super-dev` and `super-dev:` hosts

## Content Rules

- Avoid generic AI tone
- Prefer short operational statements
- Keep commands copyable
- Present the pipeline as an actual governance system, not vague methodology
- Explain what is automatic vs what still depends on the host

## Validation

- `npm run build`
- verify `/docs` static export exists
- ensure the page works on GitHub Pages with `/super-dev` base path
