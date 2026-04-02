# ledger-cli

极简命令行记账工具。一条命令记一笔，SQLite 存储，本地数据可控。

## 特点

- **极简录入**：`ledger add -a 35 -c 午饭` 搞定
- **自动分类**：输入"午饭"自动归到"食品酒水"
- **本地存储**：SQLite 单文件，无需服务器
- **多种查询**：今日/本月/年度/分类/搜索
- **AI 友好**：可直接被 AI Agent 调用（OpenClaw / Claude Code 等）

## 快速开始

```bash
# 记一笔
python3 ledger_tool.py add --amount 35 --category 午饭 --note "公司食堂"

# 今天花了多少
python3 ledger_tool.py today

# 本月汇总
python3 ledger_tool.py month

# 本月统计（含日均、同比）
python3 ledger_tool.py stats
```

## 所有命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `add` | 记一笔 | `add -a 35 -c 午饭 -n "食堂"` |
| `today` | 今日支出 | `today` |
| `month` | 月度汇总 | `month` 或 `month 2026-03` |
| `recent` | 最近 N 笔 | `recent -n 20` |
| `category` | 查某分类 | `category 餐饮` |
| `search` | 搜索备注 | `search 奶茶` |
| `stats` | 本月统计 | `stats` |
| `year` | 年度汇总 | `year` 或 `year 2025` |

## 分类自动映射

你可以输入口语化的分类，工具会自动映射：

| 你说的 | 自动归类 |
|--------|---------|
| 吃饭/午饭/外卖/咖啡/奶茶 | 食品酒水 |
| 打车/地铁/停车/加油 | 行车交通 |
| 买东西/超市/日用 | 居家物业 |
| 玩/电影/旅游 | 休闲娱乐 |
| 老婆/孩子/送礼/红包 | 人情往来 |
| 看病/药/体检 | 医疗保健 |

## 数据存储

数据存在 `ledger.db`（SQLite），和脚本同目录。可直接用任何 SQLite 工具打开查看。

## 与 AI Agent 集成

### OpenClaw

在 `AGENTS.md` 中添加记账规则，用户对 Agent 说"午饭 35"即可自动记账。

### Claude Code

直接调用：
```bash
python3 /path/to/ledger_tool.py add -a 35 -c 午饭
```

## License

MIT
