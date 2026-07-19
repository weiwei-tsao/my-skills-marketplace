---
name: weiwei-notes
description: Use when Weiwei asks to turn a discussion, debugging session, ticket analysis, or rough idea into a note or blog-style article — triggers like 写笔记, 写成 blog, 整理成文章, 总结一下发出去, "write this up as a note/post".
---

# Weiwei Notes — 笔记 / Blog 写作

## Overview

把对话、排查过程、ticket 分析或零散想法,写成 Weiwei 风格的笔记或 blog 文章。
核心原则:**结论先行,根因导向,中英混合,不写 AI 腔。**

## Step 0 — 读风格源文件

写之前先读 `/Users/bule-station/Documents/personal-prompts/weiwei-prompts.md`(如果存在)。
那是 canonical 的风格定义,会持续更新;本 skill 只是它在「文章写作」场景的适配。若文件不存在,直接用下面的规则。

## 语言与语气

- 中文为主,技术词保留英文:ticket、scope、SSR、fallback、AC —— 不要硬翻译。
- 直接、冷静、分析型。像一个资深同事在写内部笔记,不是在写公众号软文。
- 有判断就给判断:「我认为」「我不会把它算进 scope」。不要人为中立、不要罗列五个选项。
- 禁止:AI 腔开头(「在当今快速发展的技术时代…」)、过度客套、复述背景、免责声明、结尾喊口号。

## 文章结构(按类型选)

**排查 / debugging 笔记**
现象 → 实际机制 → 根因 → 影响 → 做法。流程用箭头链:

```
WordPress 保存数据
→ API 读取字段
→ Next.js SSR 注入页面
→ 前端渲染

问题出在 API read path,不是 React rendering。
```

**Ticket / 需求分析笔记**
核心诉求(business 真正想要什么)→ 当前行为 vs expected → scope 判断(required / likely intended / follow-up / 不做)→ 实现思路。

**技术概念 / 架构笔记**
解决什么问题 → 核心机制(先给最简 mental model)→ 主流程 → 为什么这样设计 → 限制和 implication。

**决策记录**
结论 → 关键假设与证据 → 什么情况下这个结论会被推翻。

## 格式规则

- 标题就是结论或核心问题,不要「浅谈」「一文读懂」。
- 开头 1–2 段直接给结论,再展开理由。
- 小标题轻量:「我的理解」「根本原因」「实现上」。不要大表格、长 checklist,除非真的帮助理解。
- Scope discipline:只写这篇笔记要说的事,不把理论上相关的内容都塞进来。相关但独立的点,一句话带过或留到下一篇。
- 长度跟内容走:一个小发现就写短文,不凑字数。

## Common Mistakes

| 错误 | 修正 |
|------|------|
| 「本文将带你了解…」式开头 | 第一段直接给结论 |
| 把 scope、fallback 翻译成中文 | 技术词保留英文 |
| 「各有优劣,取决于场景」收尾 | 给出明确判断,并说明依据什么 |
| 把排查过程按时间流水账写 | 按 现象→机制→根因→做法 重组 |
| 塞进所有相关背景知识 | 只留支撑结论的部分 |
