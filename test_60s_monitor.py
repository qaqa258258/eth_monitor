"""
60秒模拟监控测试
模拟真实的市场监控场景，测试信号检测和Telegram推送功能
"""
import json
import sys
import time
from datetime import datetime
from signal_detector import SignalDetector, SignalType

sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """加载配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        sys.exit(1)


def print_header():
    """打印标题"""
    print("=" * 80)
    print("⏱️  60秒模拟监控测试")
    print("=" * 80)
    print("🎯 目标: 模拟真实市场波动，测试信号检测和Telegram推送")
    print("⏰ 时长: 60秒")
    print("🔔 检查间隔: 每5秒检查一次")
    print("=" * 80)
    print()


def simulate_market_scenario():
    """
    模拟12种市场场景，循环使用
    覆盖：做多、做空、平多、平空、中性等各种情况
    """
    scenarios = [
        {
            'name': '📉 暴跌至下轨',
            'indicators': {
                'close': 2850,
                'rsi': 22,
                'boll_upper': 3200,
                'boll_middle': 3050,
                'boll_lower': 2900
            },
            'expected_signal': '做多'
        },
        {
            'name': '💫 轻微反弹',
            'indicators': {
                'close': 2920,
                'rsi': 35,
                'boll_upper': 3180,
                'boll_middle': 3030,
                'boll_lower': 2880
            },
            'expected_signal': '中性'
        },
        {
            'name': '⬆️ 反弹至中轨',
            'indicators': {
                'close': 3030,
                'rsi': 48,
                'boll_upper': 3170,
                'boll_middle': 3020,
                'boll_lower': 2870
            },
            'expected_signal': '平多'
        },
        {
            'name': '😐 横盘整理',
            'indicators': {
                'close': 3050,
                'rsi': 52,
                'boll_upper': 3160,
                'boll_middle': 3020,
                'boll_lower': 2880
            },
            'expected_signal': '中性'
        },
        {
            'name': '🚀 快速拉升',
            'indicators': {
                'close': 3130,
                'rsi': 65,
                'boll_upper': 3200,
                'boll_middle': 3050,
                'boll_lower': 2900
            },
            'expected_signal': '中性'
        },
        {
            'name': '📈 触及上轨',
            'indicators': {
                'close': 3200,
                'rsi': 73,
                'boll_upper': 3200,
                'boll_middle': 3050,
                'boll_lower': 2900
            },
            'expected_signal': '做空'
        },
        {
            'name': '💥 突破上轨',
            'indicators': {
                'close': 3250,
                'rsi': 79,
                'boll_upper': 3210,
                'boll_middle': 3060,
                'boll_lower': 2910
            },
            'expected_signal': '做空'
        },
        {
            'name': '⬇️ 回落至中轨',
            'indicators': {
                'close': 3060,
                'rsi': 51,
                'boll_upper': 3220,
                'boll_middle': 3060,
                'boll_lower': 2900
            },
            'expected_signal': '平空'
        },
        {
            'name': '😴 横盘震荡',
            'indicators': {
                'close': 3070,
                'rsi': 49,
                'boll_upper': 3210,
                'boll_middle': 3055,
                'boll_lower': 2900
            },
            'expected_signal': '中性'
        },
        {
            'name': '📉 二次下跌',
            'indicators': {
                'close': 2890,
                'rsi': 28,
                'boll_upper': 3200,
                'boll_middle': 3040,
                'boll_lower': 2880
            },
            'expected_signal': '做多'
        },
        {
            'name': '🔥 V型反转',
            'indicators': {
                'close': 3080,
                'rsi': 58,
                'boll_upper': 3195,
                'boll_middle': 3035,
                'boll_lower': 2875
            },
            'expected_signal': '平多'
        },
        {
            'name': '⚖️ 均衡状态',
            'indicators': {
                'close': 3040,
                'rsi': 50,
                'boll_upper': 3190,
                'boll_middle': 3030,
                'boll_lower': 2870
            },
            'expected_signal': '中性'
        }
    ]
    
    return scenarios


def run_60s_test():
    """运行60秒测试"""
    print_header()
    
    # 加载配置
    config = load_config()
    
    # 初始化检测器
    detector = SignalDetector(
        rsi_overbought=config['rsi']['overbought'],
        rsi_oversold=config['rsi']['oversold'],
        telegram_token=config['telegram'].get('bot_token'),
        telegram_chat_id=config['telegram'].get('chat_id'),
        proxy_url=config.get('proxy')
    )
    
    print("📊 Telegram配置:")
    if config['telegram'].get('bot_token') and config['telegram'].get('bot_token') != 'YOUR_BOT_TOKEN_HERE':
        print(f"  ✅ Bot Token: {config['telegram']['bot_token'][:20]}...")
        print(f"  ✅ Chat ID: {config['telegram']['chat_id']}")
        print(f"  🔔 Telegram通知: 已启用")
    else:
        print("  ⚠️ Telegram未配置 (仅控制台输出)")
    
    print(f"  🌐 代理: {config.get('proxy', '未使用')}")
    print()
    
    # 获取场景列表
    scenarios = simulate_market_scenario()
    
    # 统计信息
    stats = {
        '做多': 0,
        '做空': 0,
        '平多': 0,
        '平空': 0,
        '中性': 0,
        'telegram_success': 0,
        'telegram_failed': 0
    }
    
    start_time = time.time()
    check_interval = 5  # 每5秒检查一次
    total_checks = 12  # 60秒 / 5秒 = 12次
    
    print("🚀 开始监控...\n")
    
    try:
        for i in range(total_checks):
            elapsed = int(time.time() - start_time)
            remaining = 60 - elapsed
            
            # 选择当前场景
            scenario = scenarios[i % len(scenarios)]
            
            print(f"{'=' * 80}")
            print(f"⏰ 第 {i+1}/{total_checks} 次检查 | 已运行: {elapsed}秒 | 剩余: {remaining}秒")
            print(f"{'=' * 80}")
            print(f"🎬 场景: {scenario['name']}")
            
            # 显示市场数据
            ind = scenario['indicators']
            print(f"  💰 价格: ${ind['close']:,.2f}")
            print(f"  📊 BOLL: 上=${ind['boll_upper']:,.2f} | 中=${ind['boll_middle']:,.2f} | 下=${ind['boll_lower']:,.2f}")
            print(f"  📈 RSI: {ind['rsi']:.1f}")
            
            # 检测信号
            signal = detector.detect_signal(ind)
            signal_type = signal['signal_type'].value
            
            # 更新统计
            stats[signal_type] += 1
            
            # 显示信号
            emoji_map = {
                '做多': '🟢',
                '做空': '🔴',
                '平多': '⬆️',
                '平空': '⬇️',
                '中性': '⚪'
            }
            emoji = emoji_map.get(signal_type, '⚪')
            
            print(f"\n  {emoji} 【信号】{signal_type} (预期: {scenario['expected_signal']})")
            print(f"  💪 强度: {signal['strength']:.1f}%")
            print(f"  📝 原因: {signal['reason']}")
            
            # 发送告警
            if signal_type != '中性':
                print(f"\n  📤 发送Telegram通知...")
                detector.send_alert(
                    symbol='ETH/USDT',
                    signal=signal,
                    via_telegram=True,
                    via_console=False
                )
            else:
                print(f"\n  ⚪ 中性信号，不发送Telegram")
            
            # 记录信号
            detector.record_signal('ETH/USDT', signal)
            
            print()
            
            # 等待下次检查（最后一次不等待）
            if i < total_checks - 1:
                print(f"⏳ 等待 {check_interval} 秒...\n")
                time.sleep(check_interval)
        
        # 打印统计
        print("\n")
        print("=" * 80)
        print("📊 测试统计")
        print("=" * 80)
        print(f"⏱️  总运行时间: {int(time.time() - start_time)} 秒")
        print(f"🔍 总检查次数: {total_checks} 次")
        print()
        print("信号分布:")
        for signal_type, count in stats.items():
            if signal_type not in ['telegram_success', 'telegram_failed']:
                emoji = emoji_map.get(signal_type, '⚪')
                percentage = (count / total_checks * 100) if total_checks > 0 else 0
                print(f"  {emoji} {signal_type}: {count} 次 ({percentage:.1f}%)")
        
        # 保存历史
        print("\n💾 保存测试历史...")
        detector.save_history('test_60s_history.json')
        print("✅ 已保存到 test_60s_history.json")
        
        print("\n" + "=" * 80)
        print("✅ 60秒测试完成！")
        print("=" * 80)
        print("\n📱 请检查您的Telegram，应该收到了非中性信号的通知")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
        detector.save_history('test_60s_history.json')
        print("💾 历史已保存")


if __name__ == '__main__':
    run_60s_test()
