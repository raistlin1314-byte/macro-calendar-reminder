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
    """通过PushPlus发送微信通知"""
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
    
    # 构建HTML格式的消息内容
    message = f"<h2>【宏观日历提醒】{today}</h2>"
    message += f"<p><strong>即将到来的重要事件：</strong></p>"
    message += "<ul>"
    
    for event in sorted(events, key=lambda x: (x['days_until'], x['date'])):
        date_str = parse(event['date']).strftime("%Y-%m-%d")
        message += f"<li><strong>{date_str}</strong> ({event['days_until']}天后)<br><span style='color:#1E90FF;'>{event['event']}</span></li>"
    
    message += "</ul>"
    message += "<p><small>数据来源：2026年年度宏观日历<br>提醒规则：事件开始前2天和1天提醒</small></p>"
    
    # 发送请求到PushPlus - 群组推送版本
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": pushplus_token,
        "title": title,
        "content": message,
        "template": "html",
        "topic": "macro_reminder_group",  # 修改为您的群组编码
        "channel": "wechat",  # 指定使用微信渠道
        "sendType": 1  # 1=群发, 2=单发（默认是1，但显式指定更安全）
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"正在发送群组通知到PushPlus，事件数量: {len(events)}")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response_data = response.json()
        
        logger.info(f"群组通知发送结果: {response.status_code}, {response.text}")
        
        if response.status_code == 200 and response_data.get('code') == 200:
            logger.info("群组通知发送成功")
            return True
        else:
            logger.error(f"群组通知发送失败，响应: {response_data}")
            return False
            
    except Exception as e:
        logger.error(f"发送群组通知失败: {str(e)}")
        return False

def test_notification():
    """测试通知功能"""
    test_events = [
        {
            "date": "2026-01-01",
            "event": "【测试】欧洲央行货币政策会议",
            "days_until": 1
        }
    ]
    
    logger.info("发送测试通知...")
    success = send_pushplus_notification(test_events)
    
    if success:
        logger.info("测试通知发送成功，请检查微信是否收到")
    else:
        logger.error("测试通知发送失败")
    
    return success

def main(test_mode=False):
    """主函数"""
    logger.info("===== 宏观日历提醒工具开始运行 =====")
    
    if test_mode:
        logger.info("运行在测试模式")
        return test_notification()
    
    logger.info(f"当前日期: {datetime.date.today()}")
    upcoming_events = get_upcoming_events()
    
    if upcoming_events:
        logger.info(f"找到 {len(upcoming_events)} 个即将发生的事件，准备发送通知")
        return send_pushplus_notification(upcoming_events)
    else:
        logger.info("没有需要提醒的即将发生的事件")
        return True

if __name__ == "__main__":
    # 从环境变量获取是否运行测试模式
    test_mode = os.environ.get('TEST_MODE', 'false').lower() == 'true'
    main(test_mode)
