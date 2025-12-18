import json
import datetime
import requests
import os
from dateutil.parser import parse
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_events():
    """加载事件数据"""
    try:
        with open('data/events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
        logger.info(f"成功加载 {len(events)} 个事件")
        return events
    except Exception as e:
        logger.error(f"加载事件数据失败: {str(e)}")
        return []

def get_upcoming_events():
    """获取未来1-2天内将发生的事件"""
    today = datetime.date.today()
    events = load_events()
    upcoming_events = []
    
    for event in events:
        try:
            event_date = parse(event['date']).date()
            days_until = (event_date - today).days
            
            # 选择1-2天内发生的事件
            if 1 <= days_until <= 2:
                event['days_until'] = days_until
                upcoming_events.append(event)
                logger.info(f"找到即将发生的事件: {event['event']} (在{days_until}天后)")
        except Exception as e:
            logger.error(f"处理事件日期失败: {str(e)} - 事件: {event}")
            continue
    
    return upcoming_events

def send_pushplus_notification(events):
    """通过PushPlus发送微信通知（优化格式版）"""
    if not events:
        logger.info("没有需要提醒的即将发生的事件")
        return False
    
    pushplus_token = os.environ.get('PUSHPLUS_TOKEN')
    if not pushplus_token:
        logger.error("未设置PUSHPLUS_TOKEN环境变量")
        return False
    
    # 构建消息内容
    today = datetime.date.today().strftime("%Y-%m-%d")
    title = f"【{len(events)}个】宏观事件提醒 - {today}"
    
    # =============== 优化后的微信消息格式 ===============
    message = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    
    <!-- 顶部标题栏 -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 22px; font-weight: 600;">🌍 宏观日历提醒</h1>
        <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 16px;">{today}</p>
    </div>
    
    <!-- 提示信息 -->
    <div style="background: #fff8e6; padding: 15px 20px; border-bottom: 1px solid #ffe066;">
        <p style="margin: 0; color: #e67e22; font-weight: 500; line-height: 1.5;">
            ⚠️ <strong>重要提醒：</strong>以下事件将在 <span style="color: #e74c3c; font-weight: bold;">1-2天内</span> 发生，请提前做好准备。
        </p>
    </div>
    
    <!-- 事件列表 -->
    <div style="padding: 20px;">
        {generate_events_html(events)}
    </div>
    
    <!-- 页脚说明 -->
    <div style="background: #2c3e50; padding: 15px 20px; color: #ecf0f1; font-size: 13px; line-height: 1.5;">
        <p style="margin: 0 0 8px 0; display: flex; align-items: center;">
            <span style="margin-right: 8px;">📌</span> <strong>提醒规则：</strong> 事件开始前2天和1天提醒
        </p>
        <p style="margin: 0 0 8px 0; display: flex; align-items: center;">
            <span style="margin-right: 8px;">📊</span> <strong>数据来源：</strong> 2026年年度宏观日历
        </p>
        <p style="margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 8px;">⏰</span> <strong>更新时间：</strong> 每天北京时间 09:00
        </p>
    </div>
</div>
"""

    # 发送请求到PushPlus
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": pushplus_token,
        "title": title,
        "content": message,
        "template": "html",
        "topic": ""  # 空主题表示个人推送
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"正在发送优化格式的通知，事件数量: {len(events)}")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_data = response.json()
        
        logger.info(f"通知发送结果: {response.status_code}, {response.text}")
        
        if response.status_code == 200 and response_data.get('code') == 200:
            logger.info("优化格式的通知发送成功")
            return True
        else:
            logger.error(f"通知发送失败，响应: {response_data}")
            return False
            
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        return False

def generate_events_html(events):
    """生成事件列表的HTML"""
    if not events:
        return '<p style="text-align: center; color: #7f8c8d; padding: 20px;">暂无即将发生的事件</p>'
    
    html = '<div style="background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden;">'
    
    for i, event in enumerate(sorted(events, key=lambda x: (x['days_until'], x['date']))):
        date_str = parse(event['date']).strftime("%Y-%m-%d")
        urgency_icon = "🔥" if event['days_until'] == 1 else "⚡"
        urgency_color = "#e74c3c" if event['days_until'] == 1 else "#3498db"
        
        # 添加分隔线（除了第一个事件）
        if i > 0:
            html += '<div style="height: 1px; background: #eee; margin: 0;"></div>'
        
        html += f"""
<div style="padding: 16px 20px; {'background: #f8f9fa;' if i % 2 == 0 else ''}">
    <div style="display: flex; align-items: flex-start; gap: 12px;">
        <div style="min-width: 24px; text-align: center;">
            <div style="background: {urgency_color}; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;">
                {urgency_icon}
            </div>
        </div>
        <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                <span style="font-weight: 600; font-size: 16px; color: #2c3e50;">{event['event']}</span>
                <span style="background: {urgency_color}15; color: {urgency_color}; padding: 2px 8px; border-radius: 12px; font-size: 13px; font-weight: 500;">
                    {event['days_until']}天后
                </span>
            </div>
            <div style="color: #7f8c8d; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                <span>📅 {date_str}</span>
                <span style="color: #3498db; font-weight: 500;">|</span>
                <span style="color: #e67e22; font-weight: 500;">重点事件</span>
            </div>
        </div>
    </div>
</div>
"""
    
    html += '</div>'
    return html

def test_notification():
    """测试通知功能"""
    test_events = [
        {
            "date": "2026-01-02",
            "event": "欧洲央行货币政策会议 - 利率决策及经济展望",
            "days_until": 1
        },
        {
            "date": "2026-01-03",
            "event": "美国12月非农就业数据发布",
            "days_until": 2
        }
    ]
    
    logger.info("发送测试通知...")
    success = send_pushplus_notification(test_events)
    
    if success:
        logger.info("测试通知发送成功，请检查微信是否收到优化格式的消息")
    else:
        logger.error("测试通知发送失败")
    
    return success

def main(test_mode=False):
    """主函数"""
    logger.info("===== 宏观日历提醒工具开始运行（优化格式版）=====")
    
    if test_mode:
        logger.info("运行在测试模式")
        return test_notification()
    
    logger.info(f"当前日期: {datetime.date.today()}")
    upcoming_events = get_upcoming_events()
    
    if upcoming_events:
        logger.info(f"找到 {len(upcoming_events)} 个即将发生的事件，准备发送优化格式的通知")
        return send_pushplus_notification(upcoming_events)
    else:
        logger.info("没有需要提醒的即将发生的事件")
        return True

if __name__ == "__main__":
    # 从环境变量获取是否运行测试模式
    test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
    main(test_mode)
