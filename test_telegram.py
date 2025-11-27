"""
Telegram推送测试脚本
"""
import json
import requests
import sys

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """加载配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        sys.exit(1)


def test_telegram(bot_token, chat_id, proxy_url=None):
    """测试Telegram推送"""
    
    # 设置代理
    proxies = None
    if proxy_url:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    
    # 测试消息
    test_message = """
🧪 <b>Telegram推送测试</b>

✅ 配置信息：
- Bot Token: {}...
- Chat ID: {}
- 代理: {}

📊 如果你看到这条消息，说明Telegram推送配置成功！

接下来系统会在检测到交易信号时自动推送消息。
    """.format(
        bot_token[:20],
        chat_id,
        proxy_url if proxy_url else "未使用代理"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    print("📤 正在发送测试消息到Telegram...")
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    print(f"代理: {proxy_url if proxy_url else '未使用'}")
    print()
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": test_message,
                "parse_mode": "HTML"
            },
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 测试消息发送成功！")
            print("请检查你的Telegram查看消息")
            result = response.json()
            if result.get('ok'):
                print(f"\n📱 消息ID: {result['result']['message_id']}")
                print(f"📅 发送时间: {result['result']['date']}")
            return True
        else:
            print(f"❌ 发送失败！HTTP状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
            # 常见错误提示
            if response.status_code == 400:
                print("\n💡 可能的原因：")
                print("- Chat ID 不正确")
                print("- 还没有先给Bot发送过消息（请先在Telegram中搜索你的Bot并发送 /start）")
            elif response.status_code == 401:
                print("\n💡 可能的原因：")
                print("- Bot Token 不正确")
                print("- Bot Token 已过期或被撤销")
            elif response.status_code == 404:
                print("\n💡 可能的原因：")
                print("- Bot不存在或已被删除")
            
            return False
            
    except requests.exceptions.ProxyError:
        print("❌ 代理连接失败！")
        print("\n💡 请检查：")
        print("- 代理是否正在运行")
        print(f"- 代理地址是否正确: {proxy_url}")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时！")
        print("\n💡 请检查网络连接和代理设置")
        return False
        
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


def send_signal_example(bot_token, chat_id, proxy_url=None):
    """发送模拟交易信号示例"""
    
    proxies = None
    if proxy_url:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    
    # 模拟做多信号
    signal_message = """
🟢 <b>做多信号</b>

<b>交易对:</b> ETH/USDT
<b>价格:</b> $3,250.50
<b>RSI:</b> 28.5
<b>信号强度:</b> 85.3%
<b>原因:</b> RSI超卖(28.5) + 触及下轨($3,250.50 <= $3,251.20)
<b>时间:</b> 2025-11-27 15:00:00

💡 建议：等待价格回升至下轨上方后入场
    """
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    print("\n📤 发送模拟交易信号...")
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": signal_message,
                "parse_mode": "HTML"
            },
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 模拟信号发送成功！")
            print("这就是实际交易信号的样子")
            return True
        else:
            print(f"❌ 发送失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Telegram推送功能测试")
    print("=" * 60)
    print()
    
    # 加载配置
    config = load_config()
    
    bot_token = config['telegram'].get('bot_token')
    chat_id = config['telegram'].get('chat_id')
    proxy_url = config.get('proxy')
    
    if not bot_token or not chat_id:
        print("❌ 配置不完整！")
        print("请在 config.json 中配置 telegram.bot_token 和 telegram.chat_id")
        sys.exit(1)
    
    # 测试基本推送
    success = test_telegram(bot_token, chat_id, proxy_url)
    
    if success:
        # 发送模拟信号
        print()
        input("按Enter键发送模拟交易信号示例...")
        send_signal_example(bot_token, chat_id, proxy_url)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
