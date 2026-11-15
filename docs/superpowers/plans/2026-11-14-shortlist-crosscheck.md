# shortlist-crosscheck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一个 `shortlist-crosscheck` 插件 skill：逐项跨平台核实一份候选名单，覆盖餐厅/商家、产品、旅行地点、课程、活动，每项给出 ✅ / ⚠️ / ❌ 初筛和可追溯的证据，结论留给用户。

**Architecture:** 只有一个 `SKILL.md`，里面写通用的核实流程，再放一张"类别 → 去哪查"的表；不带脚本，引文审计用 SKILL.md 里内联的 python 片段。skill 本身就是要测的"代码"，按 writing-skills 的 RED → GREEN 做：先在没有 skill 的情况下跑一次基线，再在有 skill 的情况下跑真实任务，然后用审计 agent 复查。

**Tech Stack:** Claude Code plugin（SKILL.md + plugin.json），browser-use，xiaohongshu MCP，`add-skill.sh` 审核流程，`claude plugin validate`。

**Spec:** `docs/superpowers/specs/2026-11-14-shortlist-crosscheck-design.md`

## Global Constraints
- 分支 `feat/shortlist-crosscheck`，最后开 PR；push 和开 PR 之前先问用户。
- 插件位置 `plugins/shortlist-crosscheck/`，必须通过 `./add-skill.sh` 收进来；marketplace 条目用 `"source": "./plugins/shortlist-crosscheck"`，`"category": "research"`，版本 `0.1.0`，author `weiwei-tsao`。
- 所有网页访问都走 browser-use（小红书走 xhs MCP），不用 curl/WebFetch。
- 只做核实和初筛：不找候选，也不根据用户的个人条件下最终推荐。
- 输出写到调用方仓库的话题目录：`crosscheck-YYYY-MM.json`、`crosscheck-YYYY-MM.md`（中文）、`raw/`。
- 体检必须做：脚本核对每条引文；人工逐条确认"说的是不是这一家"。

## Review Focus
1. **证据归属错误**：帖子里提到 A 店，但评价说的是 B 店（这次 Dragon Legend 的教训）。体检必须读上下文、确认指代，而不只是确认引文存在。→ Task 3 的审计 agent 要专门检查这一项。
2. **把搜索摘要当成读过原帖**：只看了 Google 摘要的，必须标"只看了摘要"并写上日期。→ Task 2 的 SKILL.md 写成规则，Task 3 审计检查。
3. **聚合页上的评分没写来源**：搜索结果里的 `3.2(44)` 要看上一行才知道是 TripAdvisor 还是 Yelp。→ SKILL.md 写明"读评分时要连着来源一起记"。
4. **名字或型号歧义**：店名改过、拼写不同（Bap.Zap → Bap.zip），产品有不同版本、不同年份。→ 身份确认这一步必须给出能唯一确定的标识（地址或型号）。
5. **时间敏感的状态**：暂停营业、停产、活动过期、课程报名截止。→ 每个 ❌ 都必须写出依据和日期。

---

### Task 1: 基线测试（RED）

**Files:**
- Create: `docs/superpowers/specs/2026-11-14-shortlist-crosscheck-baseline.md`

**Interfaces:**
- Produces: 一份失败清单，Task 2 写 SKILL.md 时要逐条对应。

- [ ] **Step 1: 派一个不带任何 skill 提示的 subagent 跑任务**
  Prompt："用 browser-use 核实这份候选名单能不能买、口碑怎么样，结果写到 scratchpad：Ninja Creami NC301、Breville Bambino Plus、Dyson V15 Detect（加拿大市场）。"
- [ ] **Step 2: 对照 Review Focus 和设计文档的"反目标"，记录它漏了什么**
  逐项写有没有做到：确认身份/型号、查加拿大有没有货和价格、看了几个平台、有没有区分摘要和全文、有没有找危险信号、有没有审计引文、有没有替用户下结论。
- [ ] **Step 3: Commit**
  `git add docs/superpowers/specs/2026-11-14-shortlist-crosscheck-design.md docs/superpowers/specs/2026-11-14-shortlist-crosscheck-baseline.md docs/superpowers/plans/2026-11-14-shortlist-crosscheck.md && git commit -m "docs: design, plan and baseline for shortlist-crosscheck"`

### Task 2: 写 SKILL.md 并收进 marketplace

**Files:**
- Create（暂存区）: `<scratchpad>/shortlist-crosscheck/SKILL.md`
- Create（由 add-skill.sh 生成）: `plugins/shortlist-crosscheck/skills/shortlist-crosscheck/SKILL.md`、`plugins/shortlist-crosscheck/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`（追加条目）

**Interfaces:**
- Consumes: Task 1 的失败清单。
- Produces: skill 名 `shortlist-crosscheck`；输出文件名和 JSON 字段，Task 3 会检查这些。

- [ ] **Step 1: 写 SKILL.md**，结构按现有 digest skill 的样子：
  - frontmatter `description`：以 "Use when the user already has a shortlist…" 开头，触发词包括「交叉验证」「核实一下」「这几个靠谱吗」「cross-check」「verify these」；写明它和 xhs-topic-digest / en-community-digest 的区别（那两个找内容，这个只核实名单）。
  - **Workflow**（6 步，按设计文档）：确认名单和类别 → 每个候选做一次 Google 搜索（存 `raw/google_<slug>.txt`）→ 按类别表补查对应平台 → `site:` 搜社区讨论，挑重点帖子读全文和评论（Reddit/RFD 的读法直接引用 en-community-digest，不复制过来）→ 写对照表 → 体检。
  - **类别表**（一类一行）：
    | 类别 | 身份确认 | 现在能不能用 | 评分 / 评价平台 | 危险信号 |
    |---|---|---|---|---|
    | 餐厅/商家 | 地址、Google 上的正式名 | Google Maps 营业状态、当天营业时间 | Google、Yelp、TripAdvisor、外卖平台、Reddit 本地版、RFD | 赞助文、评价数涨得太快、堂食和外卖评分差很大 |
    | 产品 | 完整型号、地区版本 | 加拿大零售商有没有货、价格（Amazon.ca、Costco、Best Buy、RFD 价格帖） | Amazon、RFD、Reddit、专业测评（RTINGS 等） | 联盟推广链接、刷评、新型号旧评价混在一起 |
    | 旅行地点 | 官方名、具体位置 | 有没有关闭、季节性开放、要不要预约 | Google、TripAdvisor、Reddit | 网红景点、照片和实际差很大 |
    | 课程 | 机构、老师、具体课程或开课期 | 能不能报名、开课日期、价格 | Reddit、课程平台评价、RFD | 销售软文、只有机构自己发的好评 |
    | 活动 | 主办方、场地、日期 | 日期过了没、票卖完没 | Eventbrite、Google、Reddit 往届评价 | 主办方太新、没有往届记录 |
    最后一行写明：新类别就加一行；某个类别的规则多到一行写不下，再拆成 `references/<类别>.md`。
  - **初筛标准**：
    - ❌：对用户这次的需求来说现在用不了（关闭、停产、过期、卖完、营业时间对不上），或者身份确认不了。
    - ⚠️：有任何一个危险信号；或者平台之间评分差 ≥0.5；或者只有一个来源；或者来源之间说法冲突。
    - ✅：身份确认了、现在能用，并且至少 2 个独立平台都正面、没有危险信号。
    - 每个判断都要附上依据和日期。
  - **证据规则**：评分要连着平台名和评价数一起记；只看了摘要的要标"只看了摘要"和日期；同一帖里几个人推荐，要写"同一帖 n 人"。
  - **输出**：JSON 包含 `shortlist`、`category`、`items[]`，每项有 `name`、`identity`、`availability`、`ratings[]`、`red_flags[]`、`verdict`、`evidence_notes[]`（`platform`、`raw`、`date`、`quote`、`snippet_only`），另外还有 `uncertainties[]`。md 包含对照表、规律、待确认；结尾不写"推荐选哪个"。
  - **体检**：内联 python 片段，检查每条 `quote` 都能在对应的 `raw` 文件里找到；再逐条检查每个说法指的是不是这一项、评分的平台有没有写错、有没有把单一来源写成共识。
  - **Common mistakes**：把 Task 1 的失败清单和 Review Focus 的 1–5 条逐条写进去。
- [ ] **Step 2: 收进 marketplace**
  Run: `./add-skill.sh <scratchpad>/shortlist-crosscheck shortlist-crosscheck`
  Expected：静态审计退出码 0 或 1（0 = clean，1 = 有 HIGH，会停下来让你确认是否继续），最后打印出 marketplace 条目。
- [ ] **Step 3: 把条目粘进 `.claude-plugin/marketplace.json`**，description 写成："Cross-check a shortlist (venues, products, places, courses, events) across platforms via browser-use — identity, availability, ratings, red flags, ✅/⚠️/❌ with traceable evidence; companion to the digest skills."，keywords 写 `["cross-check","verification","shortlist","research","browser-use"]`。
- [ ] **Step 4: 校验**
  Run: `claude plugin validate .` → Expected: 没有 error。
  Run: `python3 vetting/audit_skill.py plugins/shortlist-crosscheck --quiet` → Expected: 退出码 0。
- [ ] **Step 5: Commit**
  `git add plugins/shortlist-crosscheck .claude-plugin/marketplace.json && git commit -m "feat: add shortlist-crosscheck skill (vetted)"`

### Task 3: 带 skill 跑一次（GREEN）并审计

**Files:**
- Modify: `plugins/shortlist-crosscheck/skills/shortlist-crosscheck/SKILL.md`（只修审计发现的漏洞）
- Modify: `plugins/shortlist-crosscheck/.claude-plugin/plugin.json` 和 `.claude-plugin/marketplace.json`（只有在 SKILL.md 改了的时候才升版本到 `0.1.1`）

**Interfaces:**
- Consumes: Task 2 的 SKILL.md 和输出格式；Task 1 的基线。

- [ ] **Step 1: 派一个 subagent，带上 SKILL.md 全文，跑和 Task 1 一样的产品名单**，输出到会话的 scratchpad 目录（是测试数据，不进任何仓库）。
- [ ] **Step 2: 派第二个审计 subagent**：只给 `raw/` 和输出文件，要求它逐条检查 Review Focus 的 1–5 条，并跑一次 quote 子串检查。Expected：没有归属错误；所有只看了摘要的都标了；每个 ❌ 都有依据和日期；md 里没有"推荐选哪个"。
- [ ] **Step 3: 对比基线**：Task 1 失败清单里的每一项现在都要做到。没做到的，回到 SKILL.md 补规则（REFACTOR），只补失败的那条，然后重跑 Step 1–2。
- [ ] **Step 4: 再校验并 Commit**
  Run: `claude plugin validate .` → 没有 error。
  `git add -A plugins/shortlist-crosscheck .claude-plugin/marketplace.json docs/superpowers && git commit -m "fix: tighten shortlist-crosscheck after green run"`（没有改动就跳过）

### Task 4: PR

- [ ] **Step 1: 问用户能不能 push。** 同意后：`git push -u origin feat/shortlist-crosscheck`。
- [ ] **Step 2: 开 PR**：`gh pr create --title "feat: add shortlist-crosscheck skill" --body <概述 + 基线和 GREEN 跑的对比 + 审计结果>`，正文结尾加上：

  🤖 Generated with [Claude Code](https://claude.com/claude-code)
- [ ] **Step 3: 合并之后**（用户来做）：`claude plugin marketplace update my-skills && claude plugin install shortlist-crosscheck@my-skills`，然后 `/reload-plugins`；更新 memory 里的 research-skills-setup，把它加进技能列表。
