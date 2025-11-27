"""
信号检测与告警模块 - 基于BOLL+RSI策略生成交易信号
"""
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class SignalType(Enum):
    """信号类型"""
    LONG = "做多"  # 开多单
    SHORT = "做空"  # 开空单
    EXIT_LONG = "平多"  # 平多单
    EXIT_SHORT = "平空"  # 平空单
    NEUTRAL = "中性"  # 无信号


class SignalDetector:
    """交易信号检测器"""
    
    def __init__(self, rsi_overbought: float = 70, rsi_oversold: float = 30,
                 telegram_token: str = None, telegram_chat_id: str = None,
                 proxy_url: str = None):
        """
        初始化信号检测器
        
        Args:
            rsi_overbought: RSI超买阈值，默认70
            rsi_oversold: RSI超卖阈值，默认30
            telegram_token: Telegram Bot Token
            telegram_chat_id: Telegram Chat ID
            proxy_url: 代理地址
        """
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        
        self.proxies = None
        if proxy_url:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
        
        # 信号历史
        self.signals_history = []
        self.last_signal = None
    
    def detect_signal(self, indicators: Dict) -> Dict:
        """
        检测交易信号
        
        策略说明:
        - 做多信号: RSI < 30 且价格 <= 下轨
        - 做空信号: RSI > 70 且价格 >= 上轨
        - 平多信号: 持有多单 且 (RSI > 50 或 价格 >= 中轨)
        - 平空信号: 持有空单 且 (RSI < 50 或 价格 <= 中轨)
        
        Args:
            indicators: 指标字典，包含close, rsi, boll_upper, boll_middle, boll_lower
            
        Returns:
            信号字典，包含signal_type, strength, reason等信息
        """
        close = indicators.get('close')
        rsi = indicators.get('rsi')
        boll_upper = indicators.get('boll_upper')
        boll_middle = indicators.get('boll_middle')
        boll_lower = indicators.get('boll_lower')
        
        # 数据验证
        if None in [close, rsi, boll_upper, boll_middle, boll_lower]:
            return {
                'signal_type': SignalType.NEUTRAL,
                'strength': 0,
                'reason': '数据不完整'
            }
        
        signal_type = SignalType.NEUTRAL
        strength = 0  # 信号强度 0-100
        reasons = []
        
        # 检测做多信号
        if rsi < self.rsi_oversold and close <= boll_lower:
            signal_type = SignalType.LONG
            strength = min(100, (self.rsi_oversold - rsi) * 3 + 
                         ((boll_lower - close) / close * 100) * 10)
            reasons.append(f"RSI超卖({rsi:.1f})")
            reasons.append(f"触及下轨(${close:.2f} <= ${boll_lower:.2f})")
        
        # 检测做空信号
        elif rsi > self.rsi_overbought and close >= boll_upper:
            signal_type = SignalType.SHORT
            strength = min(100, (rsi - self.rsi_overbought) * 3 + 
                         ((close - boll_upper) / close * 100) * 10)
            reasons.append(f"RSI超买({rsi:.1f})")
            reasons.append(f"触及上轨(${close:.2f} >= ${boll_upper:.2f})")
        
        # 检测平仓信号（基于上一个信号）
        elif self.last_signal:
            if self.last_signal['signal_type'] == SignalType.LONG:
                if rsi > 50 or close >= boll_middle:
                    signal_type = SignalType.EXIT_LONG
                    strength = 50
                    reasons.append(f"RSI回到中性区({rsi:.1f})" if rsi > 50 else f"价格回到中轨(${close:.2f})")
            
            elif self.last_signal['signal_type'] == SignalType.SHORT:
                if rsi < 50 or close <= boll_middle:
                    signal_type = SignalType.EXIT_SHORT
                    strength = 50
                    reasons.append(f"RSI回到中性区({rsi:.1f})" if rsi < 50 else f"价格回到中轨(${close:.2f})")
        
        # 构建信号字典
        signal = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signal_type': signal_type,
            'strength': round(strength, 2),
            'reason': ' + '.join(reasons) if reasons else '无明显信号',
            'indicators': {
                'price': close,
                'rsi': round(rsi, 2),
                'boll_upper': round(boll_upper, 2),
                'boll_middle': round(boll_middle, 2),
                'boll_lower': round(boll_lower, 2)
            }
        }
        
        # 更新最后信号（仅记录开仓信号）
        if signal_type in [SignalType.LONG, SignalType.SHORT]:
            self.last_signal = signal
        elif signal_type in [SignalType.EXIT_LONG, SignalType.EXIT_SHORT]:
            self.last_signal = None
        
        return signal
    
    def send_alert(self, symbol: str, signal: Dict, via_telegram: bool = True, 
                   via_console: bool = True) -> None:
        """
        发送告警消息
        
        Args:
            symbol: 交易对
            signal: 信号字典
            via_telegram: 是否通过Telegram发送
            via_console: 是否在控制台显示
        """
        signal_type = signal['signal_type']
        
        # 仅对开仓和平仓信号发送告警
        if signal_type == SignalType.NEUTRAL:
            return
        
        # 构建消息
        emoji_map = {
            SignalType.LONG: "🟢",
            SignalType.SHORT: "🔴",
            SignalType.EXIT_LONG: "⬆️",
            SignalType.EXIT_SHORT: "⬇️"
        }
        
        emoji = emoji_map.get(signal_type, "⚪")
        
        message = f"{emoji} {signal_type.value}信号\n"
        message += f"交易对: {symbol}\n"
        message += f"价格: ${signal['indicators']['price']:.2f}\n"
        message += f"RSI: {signal['indicators']['rsi']:.2f}\n"
        message += f"信号强度: {signal['strength']:.1f}%\n"
        message += f"原因: {signal['reason']}\n"
        message += f"时间: {signal['timestamp']}"
        
        # 控制台输出
        if via_console:
            print(f"\n{'='*60}")
            print(message)
            print('='*60)
        
        # Telegram推送
        if via_telegram and self.telegram_token and self.telegram_chat_id:
            self._send_telegram(message)
        
        # 保存到历史
        self.signals_history.append({
            'symbol': symbol,
            **signal
        })
    
    def _send_telegram(self, message: str) -> bool:
        """
        发送Telegram消息
        
        Args:
            message: 消息内容
            
        Returns:
            发送成功返回True
        """
        if not self.telegram_token or not self.telegram_chat_id:
            return False
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        try:
            response = requests.post(
                url,
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                },
                proxies=self.proxies,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Telegram发送失败] {e}")
            return False
    
    def save_history(self, filepath: str = 'signals_history.json') -> None:
        """
        保存信号历史到文件
        
        Args:
            filepath: 保存路径
        """
        try:
            # 转换Enum为字符串
            history_to_save = []
            for signal in self.signals_history:
                signal_copy = signal.copy()
                signal_copy['signal_type'] = signal_copy['signal_type'].value
                history_to_save.append(signal_copy)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存历史失败: {e}")
    
    def load_history(self, filepath: str = 'signals_history.json') -> None:
        """
        从文件加载信号历史，并恢复最后一个开仓信号状态
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                self.signals_history = history_data
                
                # 恢复最后一个开仓信号状态（从最新到最旧遍历）
                for signal in reversed(history_data):
                    signal_type_str = signal.get('signal_type')
                    # 查找最后一个开仓信号（LONG或SHORT）
                    if signal_type_str in ['做多', '做空']:
                        # 恢复信号，将字符串类型转换回Enum
                        signal_copy = signal.copy()
                        if signal_type_str == '做多':
                            signal_copy['signal_type'] = SignalType.LONG
                        elif signal_type_str == '做空':
                            signal_copy['signal_type'] = SignalType.SHORT
                        
                        self.last_signal = signal_copy
                        print(f"✅ 已从历史恢复持仓状态: {signal_type_str} @ {signal.get('timestamp', 'N/A')}")
                        break
                
        except FileNotFoundError:
            self.signals_history = []
            print("ℹ️ 未找到历史文件，从空白状态开始")
        except Exception as e:
            print(f"❌ 加载历史失败: {e}")
            self.signals_history = []


if __name__ == '__main__':
    # 测试代码
    detector = SignalDetector(rsi_overbought=70, rsi_oversold=30)
    
    # 模拟不同场景
    test_cases = [
        {
            'name': '做多信号',
            'indicators': {
                'close': 3000,
                'rsi': 25,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        },
        {
            'name': '做空信号',
            'indicators': {
                'close': 3200,
                'rsi': 75,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        },
        {
            'name': '中性信号',
            'indicators': {
                'close': 3100,
                'rsi': 50,
                'boll_upper': 3200,
                'boll_middle': 3100,
                'boll_lower': 3000
            }
        }
    ]
    
    print("📊 测试信号检测模块...\n")
    
    for test in test_cases:
        print(f"\n测试场景: {test['name']}")
        signal = detector.detect_signal(test['indicators'])
        detector.send_alert('ETH/USDT', signal, via_telegram=False)
