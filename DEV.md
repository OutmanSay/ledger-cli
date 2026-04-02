# 开发与维护指南

> 给 Claude Code / 小龙虾 / 未来的自己看的操作手册。
> 用户是 Danco，所有操作在他的 Mac 上执行。

---

## 项目结构

```
/Users/danco/projects/ledger-cli/          ← GitHub 仓库（发布用）
├── ledger_tool.py                         ← 核心代码
├── SKILL.md                               ← OpenClaw skill 定义
├── README.md                              ← 给人看的说明
├── CHANGELOG.md                           ← 版本更新日志
├── DEV.md                                 ← 本文件（开发指南）
├── LICENSE                                ← MIT
└── .gitignore                             ← 忽略 .db / .xls 等

/Users/danco/.openclaw/workspace/ledger/   ← 实际运行目录
├── ledger_tool.py                         ← 和上面同一个文件（改完要同步）
└── ledger.db                              ← 用户真实数据（不上传 GitHub）
```

**重要**：用户日常使用的是 `workspace/ledger/` 下的文件。改代码后需要同步到两个地方。

---

## 日常开发流程

### 1. 用户提需求
用户在 Telegram / Claude Code 里说"记账加个 XXX 功能"。

### 2. 改代码
修改 `/Users/danco/.openclaw/workspace/ledger/ledger_tool.py`（实际运行的那个）。

### 3. 测试
```bash
cd /Users/danco/.openclaw/workspace/ledger
python3 ledger_tool.py today
python3 ledger_tool.py add -a 1 -c 测试 -n "测试"
python3 ledger_tool.py today
# 确认没问题后删除测试数据
python3 -c "import sqlite3; c=sqlite3.connect('ledger.db'); c.execute(\"DELETE FROM transactions WHERE note='测试'\"); c.commit()"
```

### 4. 同步到 GitHub 仓库
```bash
cp /Users/danco/.openclaw/workspace/ledger/ledger_tool.py /Users/danco/projects/ledger-cli/
```

### 5. 用户说"推上去"时，执行发版

---

## 发版流程

用户说"发个新版本"或"推上去"时执行：

### Step 1：确定版本号
- 加功能：小版本号 +1（v1.0.0 → v1.1.0）
- 修 bug：补丁号 +1（v1.0.0 → v1.0.1）
- 大改：大版本号 +1（v1.x → v2.0.0）

### Step 2：更新 CHANGELOG.md
在文件顶部追加新版本段落：
```markdown
## vX.Y.Z (YYYY-MM-DD)

### 新功能
- 具体功能描述

### 修复
- 具体修复描述
```

### Step 3：同步代码
```bash
cp /Users/danco/.openclaw/workspace/ledger/ledger_tool.py /Users/danco/projects/ledger-cli/
```

### Step 4：提交 + 打标签 + 推送
```bash
cd /Users/danco/projects/ledger-cli
git add -A
git commit -m "vX.Y.Z: 一句话描述

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

### Step 5：创建 GitHub Release
```bash
gh release create vX.Y.Z --title "vX.Y.Z — 标题" --notes "更新内容"
```

### Step 6：更新 Obsidian 项目说明
更新 `02-Project/2026-04-02 极简记账系统/项目说明.md`：
- 把完成的功能从"下一版本"移到"已完成版本"
- 记录日期

---

## 数据库结构

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL DEFAULT 'expense',    -- expense / income
    category TEXT NOT NULL,                  -- 食品酒水 / 行车交通 / ...
    subcategory TEXT DEFAULT '',             -- 早午晚餐 / 打车租车 / ...
    amount REAL NOT NULL,                    -- 金额
    date TEXT NOT NULL,                      -- YYYY-MM-DD HH:MM:SS
    account TEXT DEFAULT '现金',              -- 账户
    note TEXT DEFAULT '',                    -- 备注
    source TEXT DEFAULT 'import',            -- import / manual
    created_at TEXT                          -- 创建时间
);
```

## 分类体系

沿用用户随手记 10+ 年的分类习惯：

| 标准分类 | 占比 | 典型内容 |
|---------|------|---------|
| 食品酒水 | ~48% | 三餐、零食、饮料、咖啡 |
| 人情往来 | ~25% | 老婆花的（"慈善捐助"）、孩子、送礼 |
| 行车交通 | ~15% | 打车、地铁、停车、加油 |
| 居家物业 | ~4% | 日用品、超市 |
| 休闲娱乐 | ~3% | 玩、电影、旅游 |
| 其他 | ~5% | 学习/通讯/医疗/衣服 |

**注意**："慈善捐助"子分类 = 老婆花的钱，这是用户的个人习惯，不要改。

---

## 注意事项

- `ledger.db` 是用户真实数据（19773 条，2013~2026），**绝对不能删除或覆盖**
- `.gitignore` 已排除 `.db` 文件，不会上传到 GitHub
- 改代码前先看懂现有的分类映射逻辑（`CATEGORY_ALIASES` 和 `SUBCATEGORY_HINTS`）
- 用户的记账习惯很简单：几乎只记支出，不记收入，分类粗，几乎无备注
