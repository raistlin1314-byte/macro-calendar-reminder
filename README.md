# 2026年宏观日历微信提醒工具 (PushPlus版)

![Workflow Status](https://github.com/raistlin1314-byte/macro-calendar-reminder/actions/workflows/daily_reminder.yml/badge.svg)

这是一个自动提醒工具，会在2026年重大宏观经济事件开始前两天，每天通过微信推送提醒。

## 功能特点

- 每天自动扫描即将发生的宏观事件
- 在事件开始前两天和前一天发送微信提醒
- 完整的2026年宏观日历数据
- 支持手动触发测试
- 详细的执行日志
- 使用稳定的PushPlus消息推送服务

## 部署指南

### 准备工作

1. **注册PushPlus账号**
   - 访问 [https://www.pushplus.plus](https://www.pushplus.plus)
   - 使用微信扫码注册/登录
   - 在"我的资料"页面获取您的Token
   - 在微信公众号"PushPlus推送加"中发送"微信"获取个人消息推送二维码
   - 扫码绑定后才能接收个人消息

### 配置GitHub Secrets

1. 进入您的GitHub仓库
2. 点击"Settings" > "Secrets and variables" > "Actions"
3. 点击"New repository secret"按钮
4. 添加以下Secret:
   - **Name**: `PUSHPLUS_TOKEN`
   - **Value**: 您从PushPlus获取的Token
5. 点击"Add secret"保存

### 首次运行测试

1. 点击顶部导航的"Actions"标签
2. 在左侧选择"Daily Macro Calendar Reminder"工作流
3. 点击"Run workflow"下拉按钮
4. 选择分支(通常为main)
5. 将"test_mode"设置为`true`以发送测试通知
6. 点击"Run workflow"

### 验证通知

- 检查您的微信是否收到测试通知
- 检查GitHub Actions日志，确认执行成功

## 常见问题解答

### 为什么没有收到微信通知？
1. 检查是否在PushPlus公众号完成了微信绑定
   - 在公众号发送"微信"获取绑定二维码
   - 一定要扫码完成绑定
2. 检查PUSHPLUS_TOKEN是否正确设置
3. 查看GitHub Actions执行日志，确认是否有错误
4. 检查是否超出PushPlus每日推送限制（免费版每天100条）

## 技术细节

- **编程语言**: Python 3.10
- **通知服务**: PushPlus (https://www.pushplus.plus)
- **调度系统**: GitHub Actions
- **依赖库**: requests, python-dateutil
- **执行频率**: 每天一次 (北京时间9:00)
- **消息格式**: HTML (支持富文本格式)

---

**注意**: 本工具完全在GitHub上运行，无需额外服务器。请妥善保管您的PUSHPLUS_TOKEN，不要将其公开提交到代码中。
