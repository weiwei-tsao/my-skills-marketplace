# project-context refresh — 端到端测试记录

日期：2026-11-18 至 11-19。插件版本 0.8.0（仓库工作树，与已安装版本内容一致）。目的：第一次完整验证 `refresh` 的扫描 → 报告 → 确认 → 写入流程，并为后续修复收集具体失败案例。本轮只测试和记录，没有修改插件。

## 环境

- 每个仓库 clone 一份副本并删掉 remote；原仓库不动。
- `claude -p` 加 `--plugin-dir plugins/project-context`，用 `--settings '{"enabledPlugins":{"project-context@my-skills":false}}'` 只在测试会话里停用已安装版本。确认步骤用 `--resume <session>` 续上会话回复。
- 嵌套会话需要 `bypassPermissions`（`.claude/` 在 headless 下受保护）。auto mode 会拦截这种启动方式，需要在 accept edits 模式下由用户逐次批准。
- `CLAUDE.md` 和 `.claude/` 被 gitignore，`git diff` 看不到，用运行前后的快照 `diff -r` 判断改动。

| 仓库 | 用途 |
| --- | --- |
| mac_monitor（只用标准库的 Python 单文件） | R0、R1、R9 |
| virtualbox-non-cmra-verifier（Go 和 TS 的 monorepo） | R1、R2、R3、R4、R7、R8、稳定性。副本里先删掉原有的被跟踪上下文，让 setup 生成已知基线 |
| trip-book（Vite、React、Worker） | R5 旧版产物、R6a |
| roam-weave（`.claude/skills/` 被跟踪，没有 `CLAUDE.md`） | R0b、R6b/c |

## 结果

| # | 场景 | 结果 |
| --- | --- | --- |
| 0 | headless 加 `--resume` 的多轮确认 | 通过 |
| R0 | 没有 setup | 通过：提示先运行 setup，不写任何文件 |
| R0b | 只有被跟踪的 `.claude/skills/`，没有 `CLAUDE.md` | 通过，但靠模型判断：把「infrastructure」理解为 setup 生成的文件。规范只写了「两者都不存在时停下」 |
| R1 | setup 后直接 refresh（mac_monitor） | 通过：无建议，无改动 |
| R1 | 同上（monorepo） | 无改动，但有 10 条建议：6 条 Key Pitfalls（setup 有意留空，属于设计），另外 4 条见下文 |
| R2 | 埋入 7 处变化 | 5 处完整发现，2 处部分发现；无改动。新增模块、路径迁移（含失效的 `paths:`）、依赖替换、make 目标改名、新的 fix 模式都发现了；新语言只提到脚本、没建议 `<language>.md` |
| R3 | 只确认 4 条 | 通过：只改 3 个文件，逐行修改；用户自己写的段落和规则文件不动 |
| R4a | 拒绝后原样再跑 | 同样的建议再次出现（预期）；条目数量和措辞两次不同 |
| R4b | 拒绝后改无关代码再跑 | 3/3 再次出现（预期） |
| R5 | 旧版产物迁移 | 通过：`@import`、内联 `$CLAUDE_TOOL_INPUT` guard、`npm run lint \|\| true`（脚本不存在）、遗留 skill 全部发现；迁移后用户的 hook 和 `permissions` 保留，JSON 有效，guard 与模板一致，自检 2/0。小问题：整个 `settings.json` 被重新缩进；没有建议给旧规则补 `paths:` |
| R6a | 缺 ignore 条目，没有被跟踪的路径 | 通过：出报告前补上并写进报告 |
| R6b/c | `CLAUDE.md` 被跟踪，`.claude/` 部分被跟踪 | 通过：只 ignore `.claude/rules/`、`hooks/`、`settings.json`，说明了原因。另外发现共享的 `CLAUDE.md` 引用了只在本地的规则 |
| R7 | 全部拒绝 | 通过：无改动 |
| R8 | 手动修改被 ignore 的 `git.md` | 通过 3/3：用户加的行没有被标出；用户自己的文件只在有证据时标出，改动需用户选择 |
| R9 | 新增 `pyproject.toml`（依赖和 ruff） | 通过（2b 清单里没有 pyproject 也发现了）；指出 ruff 未安装时切换 lint hook 会让每次编辑失败 |

## R1 中非 Key Pitfalls 的 4 条建议

判断标准：照着文档做，会不会出错或漏掉必要的步骤。

| 建议 | 证据 | 分类 |
| --- | --- | --- |
| migrate skill「每批 ≤400 个操作」 | 现有迁移程序每批 100；一个 fix 提交因请求体超限降到 50。照做会重现已修的 bug | 不准确（setup 用平台通用上限写的） |
| `db.md`「`BatchUpsert` 每批最多 400」 | 本身没错，但所有调用方因请求体大小把每批控制在 20/50/100 | 遗漏（与一条 Key Pitfall 重复） |
| Dev Commands 加 `pnpm dev`、`make api-test` | 与已列出的 `make start`、`go test ./...` 等价 | 改进（同义命令） |
| 改 `make help` 注释、补 `docker-down` | 原文没错，列表本来就是挑选的 | 改进 |

## 检出稳定性

同一状态下独立运行 3 次。埋入 3 处会影响实际操作的错误，加上原有的「≤400」。

| 埋点 | 类型 | 发现次数 |
| --- | --- | --- |
| 不存在的 make 目标 | 命令是否存在 | 3/3 |
| 不存在的文件路径 | 路径是否存在 | 3/3 |
| 遗留旧路径、改名前的目标 | 路径、命令是否存在 | 3/3 |
| 测试改到 compose 里的 `api-test` 服务 | 检查在哪里跑 | 3/3 |
| 文中写 50，代码里是 20 | 文中的数值 | 1/3 |
| migrate skill「每批 ≤400」 | 指导性规则与仓库做法不一致 | 0/3（三次都标为无需修改；所有运行合计 1/6） |

规范对路径（2c）和命令（2d）有具体核对步骤，对文档中的数值、常量和指导性规则没有，检出结果与此一致。

Key Pitfalls 三次分别 4、5、4 条，其中两次包含与 `db.md` 重复的条目。

## 后续

按优先级：setup 准确性 ≈ refresh 检出可靠性 > 建议去重 > 拒绝记录持久化。暂不引入基线文件和 SessionStart hook。

- #56 setup：指导性规则必须有仓库证据或用户决定支持，不能把通用最佳实践写成既有规范。
- #57 refresh：增加核对文档说法（数值、常量、限制、指导性规则）的步骤，用本轮埋点复测。
- #58 refresh：报告区分漂移、不准确、遗漏；默认不提改进类建议，Key Pitfalls 去重。
- #59 refresh 规范小缺口：R0b 的判断标准；迁移时只改目标条目、不重新格式化 `settings.json`；旧规则缺 `paths:` 时给出建议。
- #60（暂缓）拒绝记录：按证据（commit SHA、文件加规则、模式）匹配，不按文字；暂缓。

本轮全部运行费用约 $10.4。
