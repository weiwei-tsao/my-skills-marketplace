---
name: weiwei-notes
description: Use when Weiwei asks to turn a discussion, debugging session, ticket analysis, or rough idea into a public-safe Markdown note or blog-style article, including sanitizing private/internal details before publication and producing both Simplified Chinese and English versions — triggers like 写笔记, 写成 blog, 整理成文章, 总结一下发出去, 脱敏后发布, 中英文版本, "write this up as a note/post".
---

# Weiwei Notes — 笔记 / Blog 写作

## Overview

把对话、排查过程、ticket 分析或零散想法,写成 Weiwei 风格的笔记或 blog 文章。
核心原则:**结论先行,根因导向,中英混合,不写 AI 腔。**

## Step 0 — 读风格源文件

写之前先读 `/Users/bule-station/Documents/personal-prompts/weiwei-prompts.md`(如果存在)。
那是 canonical 的风格定义,会持续更新;本 skill 只是它在「文章写作」场景的适配。若文件不存在,直接用下面的规则。

## Step 1 — Public-safe 脱敏

默认假设输出会公开发布到网络。写正文前,先把素材中的内部事实抽象成公开可讨论的 product / technical / system design 表述。

必须移除或泛化:

- 公司、客户、供应商、团队、brand、项目名、产品代号、repo 名。
- Ticket / issue / PR / incident / Slack thread / doc / dashboard 等可定位 ID 或链接。
- 人员姓名、handle、邮箱、账号、头像、组织关系、具体职级。
- 文件路径、URL、域名、bucket、数据库名、表名、schema、queue、topic、service name、environment name。
- 代码常量、feature flag、内部 enum、API route、配置 key、secret/token 形态的字符串。
- 时间点、地域、规模、金额、数量等组合后会让外部定位事件的细节。

保留并重写为:

- Product goal:用户要达成什么、业务约束是什么。
- Technical trade-off:latency vs correctness、scope vs maintainability、fallback vs source of truth 等。
- System design thinking:数据流、边界、ownership、failure mode、observability、migration path。
- 可公开的抽象例子,例如「某个 CMS」「一个 SSR 页面」「上游 API」「internal workflow」。

如果内部名词对论点很重要,改成稳定占位符,不要保留原词:

| 内部信息 | 公开写法 |
|----------|----------|
| 具体公司 / brand | 某个 B2B product / 一个 customer-facing surface |
| ticket ID / incident ID | 这次需求 / 这次排查 |
| repo / service / table 名 | 某个服务 / 某张关系表 / upstream system |
| 人名 / team 名 | reviewer / owning team / downstream consumer |
| 文件路径 / 常量 | 某个 config / 一个 feature flag / render path |

如果无法在不泄漏上下文的情况下解释,就删掉那段,只留下抽象判断。

## Step 2 — 产出契约

最终产出必须是 Markdown 格式的文档,不是聊天式摘要、纯提纲或只有 bullet points 的回答。

默认同时给两个版本:

```markdown
# <标题>

## 简体中文

<中文正文>

## English

<English version>
```

- 简体中文版本放在前面,英文版本放在后面。
- 两个版本表达同一个公开安全的观点,但不需要逐句直译;英文要自然,中文要保持 Weiwei 风格。
- 两个版本都必须经过同一套脱敏规则。
- 如果用户明确只要其中一种语言,仍然优先确认是否可以省略另一种;没有确认时保持双语输出。

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

## 最终检查

交付前做一遍 redaction review:

1. 标出所有可能让外部定位到公司、项目、ticket、代码、路径、表结构、人员的词。
2. 能抽象就替换成公开概念;不能抽象就删除。
3. 确认文章仍然只依赖公开可讨论的 product / technical trade-off / system design thinking frame。
4. 不要在最终答案里附带「已删除的敏感信息清单」或原始内部名词。

## Common Mistakes

| 错误 | 修正 |
|------|------|
| 「本文将带你了解…」式开头 | 第一段直接给结论 |
| 把 scope、fallback 翻译成中文 | 技术词保留英文 |
| 「各有优劣,取决于场景」收尾 | 给出明确判断,并说明依据什么 |
| 把排查过程按时间流水账写 | 按 现象→机制→根因→做法 重组 |
| 塞进所有相关背景知识 | 只留支撑结论的部分 |
| 保留公司、ticket、路径、表名来证明上下文 | 改成抽象系统角色和 trade-off |
