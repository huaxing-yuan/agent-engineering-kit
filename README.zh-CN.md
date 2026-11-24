# Agent Engineering Kit

**为 coding agent 提供仓库原生的项目记忆与验证机制。**

Agent Engineering Kit 补上代码本身无法告诉新会话的信息：当前计划、长期决策、模块成熟度、验证路径、人工测试责任，以及由机器校验的完成定义。

它不绑定 Agent 宿主。任何能读取仓库文件、执行命令的 coding agent 都可以使用。

- English: [README.md](README.md)
- Français: [README.fr.md](README.fr.md)
- 中文：本文件

## 它是什么

- 一组精简的 Markdown 契约与模板。
- 一个 Python CLI，用于发现项目结构、安全初始化、生成索引、校验回写和汇报进度。
- 一套区分单元、集成、headless、真实进程、外部 live 和人工验证的测试模型。
- 一条保留现有 `AGENTS.md`、`CLAUDE.md`、instructions 和工程文档的采用路径。

## 它不是

- 不是 Agent runtime、模型、编排器或任务队列。
- 不替代 GitHub Issues、Jira 或 Linear。
- 不要求特定语言、框架或云平台。
- 不会让 Agent 自动获得自主性，也不会把绿色构建变成功能可用的证明。

## 核心思想

> 代码说明系统做什么；仓库记忆说明团队想做什么、已经拒绝什么，以及还缺哪些证据。

| Artifact | 职责 |
|---|---|
| `AGENTS.md` | Agent 常驻契约 |
| `engineering/modules/` | 功能成熟度、文档、测试和路线图 |
| `engineering/plans/` | 当前执行契约与原子切片 |
| `engineering/decisions/` | 已接受、拒绝、延期或取代的长期裁决 |
| `engineering/manual-tests/` | 今天的自动化仍无法验证的检查 |
| `engineering/verification/` | 测试矩阵与带到期日的已知失败 |
| `aeng check` | 检查遗漏回写和过期事实的完成门 |

## 环境要求

- Python 3.10 或更高版本。
- PyYAML 6.x。
- 测试选择需要 Git。
- 只有显式使用 `aeng verify add --create-issue` 或 `--close-issue` 时才需要 GitHub CLI。

不需要模型 API key。

## 快速开始

### 1. 运行框架本身

```bash
git clone https://github.com/<你的账号>/agent-engineering-kit.git
cd agent-engineering-kit

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -e .
aeng --version
aeng check
aeng report
```

把 `<你的账号>` 替换为你 fork 的账号。本仓库的公开地址是：

```bash
git clone https://github.com/huaxing-yuan/agent-engineering-kit.git
```

### 2. 在现有项目中使用

从本地 fork 安装 CLI，然后进入目标项目执行发现：

```bash
python -m pip install -e /path/to/agent-engineering-kit
cd /path/to/your-project

aeng discover --output .agent-engineering.yaml
```

初始化前必须人工或由 Agent 审阅生成文件。发现结果只是草稿，不是架构裁决。重点核对：

- 项目名称、描述和语言；
- source roots 与模块边界；
- test/build/lint 命令；
- 已有 instructions；
- 文档目录和语言；
- 是否需要 UI/headless 验证；
- 人工测试是否必须绑定 Issue。

预览并应用：

```bash
aeng init --dry-run
aeng init
aeng check
aeng report
```

`aeng init` 从不覆盖已有的 `AGENTS.md`、`CLAUDE.md`、instruction、模块卡或工程文档。如果 `engineering/` 已存在，用 `--adopt-existing` 只补缺失文件。

## 让 coding agent 初始化项目

安装 CLI 后，把下面提示词交给 Agent：

```text
在当前仓库初始化 agent-engineering-kit。

1. 执行 `aeng discover --stdout`，并检查真实 manifest、源码目录、测试、文档、AGENTS.md、CLAUDE.md 和已有 instructions。
2. 创建或更新 .agent-engineering.yaml，填写准确的语言、source roots、模块边界、职责和 test/build/lint 命令。
3. 不得覆盖任何已有 Agent 规则或工程 artefact。
4. 执行 `aeng init --dry-run`，向我展示采用计划和冲突。
5. 等我批准后再执行 `aeng init`；只有我批准采用现有 engineering/ 时才使用 --adopt-existing。
6. 执行 `aeng check`，只修复初始化相关问题，再执行 `aeng report`。
7. 总结安装了什么、保留了什么、哪些需要人工复核，以及哪些命令仍未知。
```

Agent 必须读仓库，不得编造模块边界或测试成功结果。

## 初始化会创建什么

```text
AGENTS.md                              # 仅当不存在
CLAUDE.md                              # 仅当不存在
.github/instructions/agent-engineering/
  README.md
  core-engineering.md
  testing.md
  ui.md
  documentation.md
  security.md
  git-and-sessions.md
engineering/
  README.md
  PROJECT.md                           # 自动生成
  modules/<module-id>.md
  plans/INDEX.yaml                     # 自动生成
  decisions/README.md                  # 自动生成索引
  manual-tests/README.md               # 自动生成未结清单
  verification/test-matrix.yaml
  verification/known-failures.yaml
  technical/_TEMPLATE.md
  reports/_TEMPLATE.md
.agent-engineering/
  adoption-report.md
  integration-block.md                 # 保留已有 Agent 契约时生成
```

已有 instructions 不移动、不改写。框架规则放在独立命名空间，与项目或宿主规则共存。

## Plan 生命周期

跨会话、跨切片、跨模块、修改公共契约、包含迁移或需要顺序 gate 的工作，应开 Plan。方案不确定时，先开限时 `investigation`。

```text
draft -> in-progress -> dev-finished -> done -> retired
              |              |
           blocked       人工验证
              |
        superseded / abandoned
```

Plan 使用原子切片：

| ID | Scope | Verification | Status | Evidence |
|---|---|---|---|---|
| S1 | 领域契约 | 单元 + 契约测试 | landed | commit/test link |
| S2 | UI 行为 | Headless test | in-progress | — |

规则：

- 进度由切片状态计算，不手工填写百分比。
- 带未完成 tail 的切片不能标记 `landed`。
- `landed` 必须有证据。
- `dev-finished` 表示所有切片已落地，只剩必需的人工验证或文档收尾。
- 测试、文档影响、人工验证和长期决策都完成后，Plan 才退役。
- 已完成的 Plan 删除，Git history 就是档案。

## Decision

接受、拒绝、延期或推翻长期方向时写 Decision，不把 Decision 当 changelog。

ID 使用 `dec-YYYY-MM-DD-kebab-case-title`，避免并行 Agent 争抢全局编号。每条 Decision 包含 Context、Decision、Consequences 和重新讨论条件；可用 `enforced_by` 链接测试或守卫。

## Issue 与人工测试

- 外部 bug 报告、需要独立分诊的工作进入 Issue。
- Plan 内的小修复不重复开 Issue。
- 当前自动化无法验证的改动，添加人工测试条目。
- 新人工测试默认必须绑定 Issue；无 Issue 系统时设置 `github.issue_required: false`。
- 只有明确人工确认才能标记 `verified`，并记录 `verified_in`。
- 人工检查可自动化后，补测试并将条目标记 `obsolete`。

## 验证模型

| 层 | 用途 |
|---|---|
| Static/governance | 格式、链接、schema、索引、遗漏回写 |
| Unit | 纯逻辑和边界情况 |
| Component/contract | 模块边界、序列化、兼容性 |
| Integration | 多模块与临时依赖 |
| Headless/in-process | 无 OS chrome 的真实应用与 UI 行为 |
| Real-process E2E | 打包、OS 对话框、焦点、多窗口、可访问性 |
| Live external | 真实供应商、账号、网络、付费模型 |
| Manual | 视觉判断、语言细节、硬件、真实账号 |

关键规则：

1. 回归测试先在旧实现上证明会红。
2. 测试选择是优化，不是完整覆盖证明。
3. 共享契约、fixture、构建配置和大范围改动回退 fast/full gate。
4. `0 tests executed` 不算成功。
5. 等可观察状态，不用固定 sleep。
6. 用稳定 AutomationId，不按本地化文案定位。
7. 截图是产物，不是行为断言。
8. 已知失败必须有精确 test ID、owner、issue、原因和到期日。

如果仓库本身包含 Agent 产品，再增加一条正交 eval 轨：工具 schema、角色可见性、权限、确认、golden trajectory 和最终 artifact。软件测试与 Agent eval 回答不同问题。

## 哪些直接用，哪些谨慎用

### 可直接复用

- Plan / Decision / Manual Test 生命周期。
- 带证据的原子切片。
- 自动索引与完成门。
- 分层测试路由。
- 保留现有文件的安全初始化。
- 带到期日的已知失败机制。

### 需要按项目调整

- 模块边界与 owner。
- test/build/lint 命令。
- 文档位置和语言。
- 成熟度定义与复核阈值。
- CI 阻塞策略。
- Issue 标签和 tracker 集成。

### 需要谨慎

- **已有 `AGENTS.md`**：显式合并集成块，不直接替换有效规则。
- **已有 `engineering/`**：增量采用，先迁移 frontmatter 再信任校验门。
- **Headless UI**：不同框架支持与 OS 覆盖不同。
- **Live 测试**：凭据、成本、限流和不确定性需要显式控制。
- **已知失败**：allowlist 会变成长期债务，必须到期。
- **全局 Decision 编号**：新仓库不要再引入。
- **历史 Decision**：不得把私有产品决策当通用示例发布。
- **报告与截图**：清理客户数据、内部域名、token 和元数据。

完整迁移清单见 [docs/ADOPTION_GUIDE.md](docs/ADOPTION_GUIDE.md)。

## CLI 参考

| 命令 | 用途 |
|---|---|
| `aeng discover` | 根据文件和 manifest 生成配置草稿 |
| `aeng init --dry-run` | 预览创建与保留，不写文件 |
| `aeng init` | 只安装缺失契约和 artefact |
| `aeng init --adopt-existing` | 补齐已有 `engineering/` |
| `aeng check` | 无效或过期事实返回失败 |
| `aeng index` | 重生成索引和 `PROJECT.md` |
| `aeng report` | 输出派生进度 |
| `aeng plan new` | 创建 Plan |
| `aeng plan add-slice` | 增加原子切片 |
| `aeng plan set-slice` | 更新状态和证据 |
| `aeng plan status` | 推进生命周期 |
| `aeng plan retire` | 门通过后删除完成 Plan |
| `aeng decision add` | 记录长期裁决 |
| `aeng verify add` | 添加人工检查，可显式创建 Issue |
| `aeng verify close` | 记录明确人工验证 |
| `aeng test select` | 显示可能受影响的测试与回退原因 |
| `aeng test select --run` | 执行配置的测试命令 |

使用 `aeng <command> --help` 查看参数。操作其他目录时，把全局 `--root` 放在子命令前。

## 文档

- [快速开始](docs/QUICKSTART.md)
- [Agent 初始化提示词](docs/AGENT_INITIALIZATION.md)
- [采用与迁移指南](docs/ADOPTION_GUIDE.md)
- [配置参考](docs/CONFIGURATION.md)
- [生命周期与完成门](docs/LIFECYCLE.md)
- [测试策略](docs/TESTING.md)
- [安全](SECURITY.md)
- [贡献](CONTRIBUTING.md)

## 当前限制

0.1 有意保持较小：

- 测试选择基于路径，不是依赖图。
- Markdown 切片解析要求约定的表格结构。
- GitHub 集成走 CLI 且可选，没有托管同步服务。
- 没有 GUI、dashboard 服务或多仓 `moved` 工作流。
- 尚未提供 JSON Schema 文件；校验在 CLI 和测试中。
- 示例是合成数据，不证明适用于所有技术栈。

## 贡献

阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。生命周期语义变更需要测试和 Decision；模板变更需要干净初始化与现有项目保留两类测试。

## 许可证

[MIT](LICENSE)。
