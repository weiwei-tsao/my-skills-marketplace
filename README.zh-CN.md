# my-skills

私人维护、人工审核的 Claude Code 技能市场。

本仓库是一个 Claude Code 插件和技能的可信白名单。你可以把自己认可的
skills 放在这个公开 GitHub 仓库里，然后在任意机器上通过 Claude Code 的
plugin marketplace 流程安装。

英文版 [README.md](README.md) 是主文档；本文档是中文配套说明。

## 这个仓库解决什么问题

- **跨机器安装**：每台机器只需添加一次 marketplace，之后即可安装列表里的
  任意技能。
- **受控准入**：新的 skill 必须通过 `add-skill.sh` 才能进入 `plugins/`。
- **静态与动态检查**：准入流程包含 Python 静态审计、可选的无网络 Docker
  沙箱运行，以及人工阅读 `SKILL.md`。
- **CI 防护**：GitHub Actions 会在 push 和 pull request 时重新运行静态审计，
  CRITICAL 级别问题会阻止合入。
- **结构清晰**：`.claude-plugin/marketplace.json` 是市场目录，
  `plugins/<name>/` 保存插件 manifest 和 skill 内容。

## 当前插件

当前 marketplace 包含：

| 插件 | 分类 | 用途 |
| --- | --- | --- |
| `a11y-audit` | quality | 辅助进行 WCAG 2.1/2.2 可访问性审计。 |
| `git-commit` | workflow | 运行质量检查，起草 Conventional Commits 信息，并提交 staged changes。 |
| `setup` | workflow | 初始化和刷新项目中的 `.claude/` 基础设施。 |
| `ai-engineering-workspace` | workflow | Ticket 全家桶：工作区脚手架、阶段门控 ticket 流程、结构化 bug 修复、跨会话 handoff —— 四个 skill，均可单独使用。 |
| `system-design-coach` | learning | 通过路线图、case drill 和答案 review 辅助学习系统设计。 |

权威列表以
[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) 为准。

## 在 Claude Code 中安装

每台机器添加一次 marketplace：

```text
/plugin marketplace add weiwei-tsao/my-skills-marketplace
```

安装某个 skill：

```text
/plugin install a11y-audit@my-skills
```

当仓库更新后，同步 marketplace：

```text
/plugin marketplace update
```

这个流程假设仓库是公开的，因为 Claude Code 会从 GitHub 拉取 marketplace。
不要把密钥、token、凭据或公司私有 skill 内容放进这个公开仓库。

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
