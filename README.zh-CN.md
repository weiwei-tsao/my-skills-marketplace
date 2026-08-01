# my-skills

私人维护、人工审核的 Claude Code 与 Codex skills 集合。

本仓库是一个可复用 agent skills 的可信白名单，并同时支持两种安装路径：

- **Claude Code** 通过仓库里的 `.claude-plugin/` marketplace catalog 安装已审核的
  plugin bundles。
- **Codex** 复用同一份 skill payload，把 `plugins/*/skills/*` 软链接到 Codex 的
  skill 目录，作为本地 filesystem skills 使用。

目标是把你亲自认可的 skills 放在同一个公开 GitHub 仓库里，并为 Claude Code 和
Codex 都提供清晰的审核、安装和更新流程。

英文版 [README.md](README.md) 是主文档；本文档是中文配套说明。

## 这个仓库解决什么问题

- **Claude Code 跨机器安装**：每台机器只需添加一次 marketplace，之后即可安装
  列表里的任意 bundle。
- **Codex 本地安装与更新**：把同一份 skill payload 软链接到 Codex 的本地
  filesystem skill 目录中，供个人使用。
- **受控准入**：新的 skill 必须通过 `add-skill.sh` 才能进入 `plugins/`。
- **静态与动态检查**：准入流程包含 Python 静态审计、可选的无网络 Docker
  沙箱运行，以及人工阅读 `SKILL.md`。
- **CI 防护**：GitHub Actions 会在 push 和 pull request 时重新运行静态审计，
  CRITICAL 级别问题会阻止合入。
- **结构清晰**：`.claude-plugin/marketplace.json` 是 Claude Code catalog，
  `plugins/<name>/` 保存 plugin manifest 和一个或多个 Codex 可直接链接的
  skill payload。

## 当前插件与 Skills

当前 catalog 包含这些 plugin bundles。对 Claude Code 来说，每一行都是 marketplace
里可安装的 plugin；对 Codex 来说，`install-codex-skills.sh` 会发现并链接这些
bundle 内部的各个 `skills/*` 目录。

| 插件 | 分类 | 用途 |
| --- | --- | --- |
| `a11y-audit` | quality | 辅助进行 WCAG 2.1/2.2 可访问性审计。 |
| `git-commit` | workflow | 运行质量检查，起草 Conventional Commits 信息，并提交 staged changes。 |
| `setup` | workflow | 初始化和刷新项目中的 `.claude/` 基础设施。 |
| `ai-engineering-workspace` | workflow | Ticket 全家桶：工作区脚手架、阶段门控 ticket 流程、结构化 bug 修复、跨会话 handoff、ticket completion 知识沉淀 —— 五个 skill，可按场景单独使用。 |
| `system-design-coach` | learning | 通过路线图、case drill 和答案 review 辅助学习系统设计。 |
| `weiwei-notes` | writing | 把讨论、排查过程或 ticket 分析整理成 Weiwei 风格的笔记 / blog 文章（结论先行、根因导向、中英混合）。 |

权威列表以
[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) 为准。

## 通过 Claude Code Marketplace 安装

每台机器添加一次 marketplace：

```text
/plugin marketplace add weiwei-tsao/my-skills-marketplace
```

安装某个 plugin bundle：

```text
/plugin install a11y-audit@my-skills
```

当仓库更新后，同步 marketplace：

```text
/plugin marketplace update
```

这个流程假设仓库是公开的，因为 Claude Code 会从 GitHub 拉取 marketplace。
不要把密钥、token、凭据或公司私有 skill 内容放进这个公开仓库。

## 在 Codex 中安装或更新

Codex 可以从 `$HOME/.agents/skills` 和仓库级 `.agents/skills` 等目录读取本地
filesystem skills。本仓库的 skill payload 已经位于 `plugins/*/skills/*`，所以
最低风险的 Codex 本地安装方式，是把这些 payload 目录软链接到 Codex 的用户级
skill 目录。首次安装和仓库更新后的同步都使用同一个 installer。

预览安装计划：

```bash
./install-codex-skills.sh
```

创建软链接：

```bash
./install-codex-skills.sh --apply
```

拉取仓库更新后，同步已有的 Codex 安装：

```bash
git pull
./install-codex-skills.sh
./install-codex-skills.sh --apply
```

安装到其他 Codex skill scope：

```bash
./install-codex-skills.sh --apply --target /path/to/.agents/skills
```

也可以设置 `CODEX_SKILLS_DIR`，而不是传 `--target`。

这个脚本刻意保持保守：

- 默认只 dry run，不写入。
- 使用软链接，不复制 skill 内容。
- 对已经指向当前仓库的链接是幂等的，可以重复运行。
- 不覆盖已有文件、目录，或指向其他位置的 symlink。
- 会检查每个发现的 `SKILL.md` 是否包含简单的 `name`。
- 不会自动清理已删除或重命名 skill 留下的旧 symlink；如有需要，请先人工检查再删除。

安装后，如果 Codex 没有立刻显示新 skills，请重启 Codex 或开启新 session。在
Codex CLI 或 IDE extension 中，可以运行 `/skills`，也可以输入 `$` 显式 mention
某个 skill，例如 `$weiwei-notes` 或 `$ticket-workflow`。

如果你移动了这个 checkout，或重新 clone 到了新路径，已有 symlink 可能仍指向旧
位置。installer 会把这类情况标记为 "already links elsewhere" 并跳过，方便你先
检查再决定是否替换。

这不是把本仓库作为 Codex plugin marketplace 直接安装。当前仓库使用
`.claude-plugin/` 下的 Claude Code marketplace 结构；Codex plugin 分发使用自己
的 plugin manifest 和 marketplace 结构。个人本地使用优先采用 symlink installer；
只有需要 marketplace 分发时，再迁移/新增 Codex plugin packaging。

## 添加新的 Skill

请把 `add-skill.sh` 作为唯一准入路径：

```bash
cd my-skills-marketplace
./add-skill.sh /path/to/skill-dir <plugin-name>
```

示例：

```bash
./add-skill.sh ~/Documents/Repositories/plain-dock/.claude/skills/git-commit git-commit
```

脚本会执行四道关卡：

1. **静态审计**：`vetting/audit_skill.py` 检查高风险模式和 Python taint flow。
   CRITICAL 发现会直接停止流程。
2. **沙箱首跑**：`vetting/sandbox_skill.sh` 在禁用网络的 Docker 容器中运行，
   并记录可疑访问。如果没有 Docker，脚本会明确警告并询问是否继续。
3. **人工阅读**：脚本会打印发现的 `SKILL.md`，由维护者手动确认。
4. **准入复制**：skill 会被复制到 `plugins/<plugin-name>/`，脚本生成最小
   plugin manifest，并打印需要粘贴到 marketplace 的 catalog entry。

准入后，把脚本打印的条目粘贴到 `.claude-plugin/marketplace.json` 的
`plugins` 数组中，补全 `description`、`category` 和 `keywords`，然后验证并提交：

```bash
claude plugin validate .
git add -A
git commit -m "add <plugin-name> (vetted)"
git push
```

Codex 不需要单独更新 catalog。只要 skill 已经位于
`plugins/<plugin-name>/skills/<skill-name>/`，重新运行
`./install-codex-skills.sh --apply` 即可把它链接到选定的 Codex skill 目录。

## Marketplace Source 格式

对于 vendored local plugin，catalog entry 的 `source` 必须是以 `./` 开头的
相对路径：

```json
{
  "name": "git-commit",
  "source": "./plugins/git-commit",
  "version": "0.1.0",
  "description": "Run quality checks and draft a Conventional Commits message, then commit staged changes.",
  "author": { "name": "weiwei-tsao" },
  "category": "workflow",
  "keywords": ["git", "commit", "conventional-commits"]
}
```

常见规则：

- 使用 `"source": "./plugins/<name>"`，不要写成 `"plugins/<name>"` 或
  `"<name>"`。
- 不要添加顶层 `pluginRoot` 字段。
- 不要添加顶层 `strict` 字段。
- push 前运行 `claude plugin validate .`。

如果 Claude Code 报错：

```text
This plugin uses a source type your version does not support.
```

请先更新 Claude Code，然后检查上面的 source path 格式。

## 改为引用上游 Skill

如果不想 vendoring，也可以引用上游 GitHub 仓库，但应固定到 commit SHA：

```json
{
  "name": "cool-skill",
  "source": {
    "source": "github",
    "repo": "someone/cool-skill",
    "sha": "<40-character-commit-sha>"
  }
}
```

请使用 SHA，不要使用 branch 或会移动的 tag。更新 SHA 前需要重新 vet 上游内容。

## 仓库结构

```text
.claude-plugin/marketplace.json   # Claude Code 读取的 marketplace catalog
.github/workflows/vet-skills.yml  # CI 静态审计关卡
CLAUDE.md                         # 给 Claude Code 的维护说明
README.md                         # 英文主文档
README.zh-CN.md                   # 中文配套文档
add-skill.sh                      # vetting 与准入流程
install-codex-skills.sh           # Codex 本地 skills 软链接安装脚本
plugins/<name>/
  .claude-plugin/plugin.json      # plugin manifest
  skills/<name>/SKILL.md          # skill 指令
vetting/
  audit_skill.py                  # 静态审计器
  taint_python.py                 # Python AST taint 分析器
  sandbox_skill.sh                # Docker 沙箱首跑脚本
```

## 审计工具退出码

`vetting/audit_skill.py` 的返回值：

| 退出码 | 含义 | 影响 |
| --- | --- | --- |
| `0` | clean | 继续。 |
| `1` | HIGH findings | 本地警告；CI 报 warning。 |
| `2` | CRITICAL findings | 本地停止；CI 失败。 |

手动审计：

```bash
python3 vetting/audit_skill.py plugins/<name> --no-color
```

如果需要机器可读报告，可以加上 `--json report.json`。

## 维护规则

- 公开仓库中不要放 secrets、tokens、credentials 或公司私有资料。
- 尽量一个 skill 对应一个 commit，并在 commit message 中说明已 vet。
- 更新 skill 时重新运行 vetting 流程。
- 保持 catalog source path 与 `plugins/<name>/` 一致。
- clean audit 只表示“未发现红旗”，不等于证明 skill 安全。
- 提交前清理意外出现的 macOS metadata；`.gitignore` 已排除 `.DS_Store`，
  但已有文件仍可能出现在工作区。

## 常见问题

**Plugin source type is not supported**

先更新 Claude Code，再确认 catalog source 是否严格写成
`"./plugins/<name>"`。删除不兼容的 `pluginRoot` 或 `strict` 字段，运行
`claude plugin validate .`，提交、push，然后执行 `/plugin marketplace update`。

**`git push` 报 permission denied 或 403**

机器可能缓存了错误 GitHub 账号的凭据。清理凭据后，用 `gh auth login` 或具有
相应仓库权限的 Personal Access Token 重新认证。

**`git push` 报 repository not found**

先在 GitHub 创建公开空仓库，再把本地仓库 push 上去。

**插件能安装，但 skill 不触发**

检查 skill 的 `SKILL.md` frontmatter。`description` 应该明确说明什么时候使用
这个 skill，而不仅是描述它是什么。

## 安全边界

本仓库通过私人白名单、静态扫描、沙箱观察、人工阅读和 CI 降低风险，但不能证明
skill 绝对安全。对不熟悉的 skill 仍需仔细阅读，尤其是会执行脚本、访问凭据、
安装依赖或需要网络访问的 skill。
