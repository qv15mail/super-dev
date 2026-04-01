"""
Compact Summary Template — 上下文压缩指令模板

开发：Excellent（11964948@qq.com）
功能：为 pipeline 执行上下文提供结构化压缩摘要模板
9 段结构化压缩摘要模板。
创建时间：2026-03-31
"""

from __future__ import annotations

COMPACT_SUMMARY_TEMPLATE = """\
Your task is to create a detailed summary of the pipeline execution so far.

This summary will be used to replace the existing conversation context when the
context window is running low, so it must be comprehensive enough to continue
the pipeline without losing critical information.

Your summary should include:

1. **Primary Request and Intent**
   - What the user originally asked for
   - The overall goal of the current pipeline run

2. **Key Technical Concepts**
   - Architecture decisions made so far
   - Technology stack choices and constraints
   - Design patterns and conventions adopted

3. **Files and Code Sections**
   - Files created or modified (with absolute paths)
   - Key code sections that are relevant to ongoing work
   - Configuration changes

4. **Errors and Fixes**
   - Errors encountered during the pipeline
   - How they were resolved
   - Workarounds applied

5. **Problem Solving**
   - Complex decisions and their rationale
   - Trade-offs evaluated
   - Alternative approaches considered and rejected

6. **User Messages Summary**
   - Key feedback from the user
   - Confirmed design choices
   - Rejected proposals and reasons

7. **Pending Tasks**
   - Remaining items from tasks.md
   - Known issues not yet addressed
   - Deferred work items

8. **Current Work**
   - What phase the pipeline is in
   - What was being worked on when the summary was requested
   - State of any in-progress changes

9. **Next Step**
   - The immediate next action to take
   - Any blockers or dependencies
   - Expected outcome of the next step

Format the summary as structured Markdown. Be specific: include file paths,
function names, variable names, and exact error messages where relevant.
Do NOT be vague or use placeholders — the summary must be actionable.
"""
