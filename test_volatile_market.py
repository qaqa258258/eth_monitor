"""
模拟激烈市场波动测试
测试各种极端行情下的信号检测
"""
from signal_detector import SignalDetector, SignalType

def print_separator():
    print("=" * 80)

def test_volatile_market():
    """模拟激烈波动的市场行情"""
    print_separator()
    print("🌪️  激烈市场波动模拟测试")
    print_separator()
    print()
    
    # 初始化检测器
    detector = SignalDetector(rsi_overbought=70, rsi_oversold=30)
    
    # 模拟剧烈波动的市场数据
    scenarios = [
        {
            'name': '📉 暴跌开始 - 触及下轨',
            'indicators': {
                'close': 2900,
                'rsi': 25,
                'boll_upper': 3200,
                'boll_middle': 3050,
                'boll_lower': 2900
            }
        },
        {
            'name': '📉 继续下跌 - 跌破下轨',
            'indicators': {
                'close': 2850,
                'rsi': 20,
                'boll_upper': 3180,
                'boll_middle': 3030,
                'boll_lower': 2880
            }
        },
        {
            'name': '💫 轻微反弹',
            'indicators': {
                'close': 2920,
                'rsi': 32,
                'boll_upper': 3170,
                'boll_middle': 3020,
                'boll_lower': 2870
            }
        },
        {
            'name': '⬆️ 反弹至中轨',
            'indicators': {
                'close': 3025,
                'rsi': 48,
                'boll_upper': 3160,
                'boll_middle': 3020,
                'boll_lower': 2880
            }
        },
        {
            'name': '🚀 快速拉升',
            'indicators': {
                'close': 3100,
                'rsi': 62,
                'boll_upper': 3150,
                'boll_middle': 3000,
                'boll_lower': 2850
            }
        },
        {
            'name': '📈 触及上轨',
            'indicators': {
                'close': 3150,
                'rsi': 72,
                'boll_upper': 3150,
                'boll_middle': 3000,
                'boll_lower': 2850
            }
        },
        {
            'name': '📈📈 突破上轨',
            'indicators': {
                'close': 3180,
                'rsi': 78,
                'boll_upper': 3155,
                'boll_middle': 3005,
                'boll_lower': 2855
            }
        },
        {
            'name': '💥 暴涨顶峰',
            'indicators': {
                'close': 3220,
                'rsi': 85,
                'boll_upper': 3160,
                'boll_middle': 3010,
                'boll_lower': 2860
            }
        },
        {
            'name': '⬇️ 回落至中轨',
            'indicators': {
                'close': 3015,
                'rsi': 52,
                'boll_upper': 3165,
                'boll_middle': 3015,
                'boll_lower': 2865
            }
        },
        {
            'name': '😐 横盘整理',
            'indicators': {
                'close': 3000,
                'rsi': 48,
                'boll_upper': 3160,
                'boll_middle': 3010,
                'boll_lower': 2860
            }
        },
        {
            'name': '📉 二次探底',
            'indicators': {
                'close': 2880,
                'rsi': 28,
                'boll_upper': 3150,
                'boll_middle': 3000,
                'boll_lower': 2850
            }
        },
        {
            'name': '🔥 V型反转',
            'indicators': {
                'close': 3080,
                'rsi': 58,
                'boll_upper': 3145,
                'boll_middle': 2995,
                'boll_lower': 2845
            }
        }
    ]
    
    # 记录信号统计
    signal_stats = {
        '做多': 0,
        '做空': 0,
        '平多': 0,
        '平空': 0,
        '中性': 0
    }
    
    print("🎬 开始模拟...\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n【场景 {i}】{scenario['name']}")
        print("-" * 80)
        
        # 检测信号
        signal = detector.detect_signal(scenario['indicators'])
        
        # 打印指标信息
        ind = scenario['indicators']
        print(f"  💰 价格: ${ind['close']:,.2f}")
        print(f"  📊 BOLL: 上轨=${ind['boll_upper']:,.2f} | 中轨=${ind['boll_middle']:,.2f} | 下轨=${ind['boll_lower']:,.2f}")
        print(f"  📈 RSI: {ind['rsi']:.1f}")
        
        # 价格位置
        boll_range = ind['boll_upper'] - ind['boll_lower']
        position = ((ind['close'] - ind['boll_lower']) / boll_range * 100) if boll_range > 0 else 50
        print(f"  📍 BOLL位置: {position:.1f}%")
        
        # 信号信息
        signal_type = signal['signal_type'].value
        strength = signal['strength']
        reason = signal['reason']
        
        # 统计
        signal_stats[signal_type] += 1
        
        # 显示信号
        emoji_map = {
            '做多': '🟢',
            '做空': '🔴',
            '平多': '⬆️',
            '平空': '⬇️',
            '中性': '⚪'
        }
        emoji = emoji_map.get(signal_type, '⚪')
        
        print(f"\n  {emoji} 【信号】{signal_type}")
        print(f"  💪 强度: {strength:.1f}%")
        print(f"  📝 原因: {reason}")
        
        # 记录信号
        detector.record_signal('ETH/USDT', signal)
        
        # 发送告警(仅控制台)
        if signal_type != '中性':
            print(f"  🔔 【告警】{signal_type}信号已触发！")
    
    # 打印统计信息
    print("\n")
    print_separator()
    print("📊 信号统计")
    print_separator()
    
    total_signals = sum(signal_stats.values())
    for signal_type, count in signal_stats.items():
        emoji = emoji_map.get(signal_type, '⚪')
        percentage = (count / total_signals * 100) if total_signals > 0 else 0
        print(f"{emoji} {signal_type}: {count} 次 ({percentage:.1f}%)")
    
    print(f"\n总计: {total_signals} 次信号")
    
    # 保存历史
    print("\n💾 保存测试历史...")
    detector.save_history('test_volatile_market_history.json')
    print("✅ 已保存到 test_volatile_market_history.json")
    
    print("\n")
    print_separator()
    print("🎉 模拟完成！")
    print_separator()

if __name__ == '__main__':
    test_volatile_market()
