# 🚀 GitHub Actions 快速上传指南

## 第一步：本地测试 run_once.py

在上传前先测试脚本是否正常工作：

```bash
# 注意：本地测试需要代理，但GitHub Actions不需要
python run_once.py
```

如果看到价格、RSI、信号等信息，说明脚本正常。

---

## 第二步：上传到GitHub

### 1. 初始化Git仓库

```bash
cd d:\PythonProject\CascadeProjects\windsurf-project\eth_monitor
git init
git add .
git commit -m "Initial commit: ETH合约监控系统 with GitHub Actions"
```

### 2. 在GitHub创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`eth-trading-monitor`
3. 描述：`ETH合约开单提醒系统 - 基于BOLL+RSI策略，支持GitHub Actions自动运行`
4. 选择：**Private**（强烈推荐，保护你的策略）
5. **不要**勾选任何初始化选项
6. 点击 `Create repository`

### 3. 关联并推送

```bash
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/eth-trading-monitor.git
git branch -M main
git push -u origin main
```

---

## 第三步：配置GitHub Secrets（关键！）

### 进入Secrets设置页面

`仓库首页` → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

### 添加2个必需的Secrets

#### Secret 1: TELEGRAM_BOT_TOKEN
- **Name**: `TELEGRAM_BOT_TOKEN`
- **Value**: `8530556154:AAFr5Dhy1iXabnskMcx6H2nlqaWpOBYWbTQ`
- 点击 `Add secret`

#### Secret 2: TELEGRAM_CHAT_ID
- **Name**: `TELEGRAM_CHAT_ID`
- **Value**: `5785662116`
- 点击 `Add secret`

### ✅ 检查Secrets

确保看到：
- ✅ TELEGRAM_BOT_TOKEN
- ✅ TELEGRAM_CHAT_ID

---

## 第四步：手动触发测试

### 1. 进入Actions页面

`仓库首页` → `Actions` 标签

### 2. 启用Workflows

如果看到提示 "Workflows aren't being run on this repository"，点击 `I understand my workflows, go ahead and enable them`

### 3. 手动运行

1. 左侧选择 `ETH交易信号监控`
2. 点击右侧的 `Run workflow` 按钮（下拉菜单）
3. 点击绿色的 `Run workflow` 确认

### 4. 查看运行结果

1. 等待几秒，刷新页面
2. 点击刚创建的运行记录
3. 点击 `monitor` 查看详细日志
4. 检查是否有错误

### 5. 检查Telegram

🔔 **打开你的Telegram，应该会收到信号推送！**

---

## 第五步：验证自动运行

### 查看下次运行时间

在Actions页面，你会看到：
```
Next scheduled run in XX minutes
```

### 等待30分钟

系统会自动运行，无需任何操作

### 持续监控

每30分钟自动检查一次，有信号就推送到Telegram

---

## 🎯 完成检查清单

- [ ] 本地测试 `run_once.py` 成功
- [ ] 代码已上传到GitHub
- [ ] 设置了 `TELEGRAM_BOT_TOKEN` Secret
- [ ] 设置了 `TELEGRAM_CHAT_ID` Secret
- [ ] 手动触发Actions成功运行
- [ ] Telegram收到测试消息
- [ ] 等待30分钟验证自动运行

---

## 📊 监控运行状态

### 查看所有运行记录
```
Actions → ETH交易信号监控
```

### 下载信号历史
```
Actions → 选择运行记录 → Artifacts → signals-history
```

### 修改运行频率
编辑 `.github/workflows/monitor.yml`，修改cron表达式后提交

---

## 🔧 故障排查

### 问题1: Actions运行失败
**检查**: Actions日志中的错误信息
**常见原因**:
- Secrets未设置或设置错误
- 依赖安装失败

### 问题2: 没收到Telegram消息
**检查**: 
1. Secrets是否正确
2. 是否有交易信号产生（查看日志）
3. Telegram Bot是否活跃

### 问题3: 运行频率不对
**检查**: `.github/workflows/monitor.yml` 中的cron表达式

---

## 💡 进阶配置

### 修改监控参数

编辑 `.github/workflows/monitor.yml` 第32-47行，修改：
- `symbol`: 交易对（如改为 `BTC/USDT`）
- `timeframe`: 时间周期（如改为 `1h`）
- BOLL和RSI参数

修改后提交即可生效。

### 调整运行时间段

只在交易活跃时段运行（UTC 0-16点 = 北京时间 8-24点）：
```yaml
schedule:
  - cron: '*/30 0-16 * * *'
```

---

## ✅ 成功标志

当你看到：
- ✅ Actions每30分钟自动运行
- ✅ Telegram定期收到信号（有信号时）
- ✅ 绿色的✓在Actions页面

**恭喜！你的24/7自动监控系统已启动！** 🎉

---

## 🆘 需要帮助？

检查这些文档：
- `GITHUB_ACTIONS_GUIDE.md` - 详细配置说明
- `README.md` - 项目使用说明
- GitHub Actions日志 - 运行详情

或查看GitHub Issues寻求帮助。
