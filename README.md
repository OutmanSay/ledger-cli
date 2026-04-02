# ledger-cli 💰

**跟 AI 说句话就记好账。不用打开 APP，不用登录，数据全在本地。**

---

## 为什么做这个？

用了十几年随手记，每次记账要：打开 APP → 选分类 → 输金额 → 保存。

现在只需要跟 AI 说一句：

> "午饭 35"

搞定。

## 谁适合用

- 你已经在用 AI Agent（OpenClaw / Claude Code / Codex 等）
- 你懒得每次打开记账 APP
- 你不信任云端存你的消费数据
- 你想要的只是记下来、偶尔看看，不需要花哨的图表

## 30 秒上手

### 方式一：作为 OpenClaw Skill 安装

跟你的 Agent 说：

> "学习这个 skill：https://github.com/OutmanSay/ledger-cli"

然后直接开始：

> "午饭 35"
> "打车 18 去公司"
> "今天花了多少"

### 方式二：独立使用

```bash
git clone https://github.com/OutmanSay/ledger-cli.git
cd ledger-cli

# 记一笔
python3 ledger_tool.py add -a 35 -c 午饭

# 今天花了多少
python3 ledger_tool.py today

# 本月汇总
python3 ledger_tool.py month
```

无需安装依赖，Python 3 + SQLite（系统自带）就够了。

## 你可以这样说

| 你说的 | 它做的 |
|--------|--------|
| 午饭 35 | ✅ 记到「食品酒水」 |
| 打车 18 | ✅ 记到「行车交通」 |
| 停车费 15 | ✅ 记到「行车交通」 |
| 老婆买衣服 299 | ✅ 记到「人情往来」 |
| 买水果 25 | ✅ 记到「食品酒水」 |
| 咖啡 19.9 | ✅ 记到「食品酒水」 |
| 给孩子买文具 42 | ✅ 记到「人情往来」 |

## 你可以这样查

| 你说的 | 它返回的 |
|--------|---------|
| 今天花了多少 | 📅 今日支出明细 + 总额 |
| 本月花了多少 | 📊 本月分类汇总 + 占比 |
| 本月吃饭花了多少 | 🏷️ 餐饮分类明细 |
| 最近花了什么 | 📋 最近 10 笔流水 |
| 今年花了多少 | 📅 年度月度趋势 |
| 本月统计 | 📈 总计 + 日均 + 上月同比 |

## 数据存储

所有数据存在 `ledger.db`（SQLite 单文件），和脚本同目录。

- 不上传云端
- 不需要注册账号
- 可以用任何 SQLite 工具打开
- 可以随时导出 CSV

## 支持导入

如果你之前用随手记，可以导出 XLS 后一键导入历史数据。（导入脚本见项目内说明）

## 所有命令

```bash
# 记一笔
python3 ledger_tool.py add --amount 35 --category 午饭 --note "公司食堂"

# 查询
python3 ledger_tool.py today              # 今日支出
python3 ledger_tool.py month              # 本月汇总
python3 ledger_tool.py month 2026-03      # 指定月
python3 ledger_tool.py recent             # 最近 10 笔
python3 ledger_tool.py recent -n 20       # 最近 20 笔
python3 ledger_tool.py category 餐饮      # 查分类
python3 ledger_tool.py search 奶茶        # 搜索
python3 ledger_tool.py stats              # 本月统计
python3 ledger_tool.py year               # 年度汇总
python3 ledger_tool.py year 2025          # 指定年
```

## 自动分类映射

口语化输入，自动归类：

| 输入 | 归类 |
|------|------|
| 吃饭/早饭/午饭/晚饭/外卖/咖啡/奶茶/零食/水果 | 食品酒水 |
| 打车/地铁/公交/停车/加油 | 行车交通 |
| 买东西/超市/日用 | 居家物业 |
| 玩/电影/旅游 | 休闲娱乐 |
| 老婆/孩子/送礼/红包 | 人情往来 |
| 看病/药/体检 | 医疗保健 |
| 衣服/鞋 | 衣服饰品 |
| 话费/网费 | 交流通讯 |
| 数码/订阅 | 学习进修 |

## License

MIT
