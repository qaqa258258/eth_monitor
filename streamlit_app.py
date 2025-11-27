"""
ETH合约开单提醒系统 - Streamlit可视化界面
基于BOLL + RSI策略的实时监控和可视化
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime

from data_fetcher import DataFetcher
from indicator import calculate_all_indicators, get_latest_indicators
from signal_detector import SignalDetector, SignalType


# 页面配置
st.set_page_config(
    page_title="ETH合约开单提醒系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .signal-long {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    .signal-short {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    .signal-neutral {
        background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_config():
    """加载配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'proxy': 'http://127.0.0.1:10808',
            'symbol': 'ETH/USDT',
            'timeframe': '15m',
            'boll': {'period': 20, 'std_dev': 2},
            'rsi': {'period': 14, 'overbought': 70, 'oversold': 30},
            'telegram': {'bot_token': '', 'chat_id': ''}
        }


@st.cache_resource
def init_modules(_config):
    """初始化模块（使用下划线前缀避免缓存配置对象）"""
    data_fetcher = DataFetcher(proxy_url=_config['proxy'])
    signal_detector = SignalDetector(
        rsi_overbought=_config['rsi']['overbought'],
        rsi_oversold=_config['rsi']['oversold'],
        telegram_token=_config['telegram'].get('bot_token'),
        telegram_chat_id=_config['telegram'].get('chat_id'),
        proxy_url=_config['proxy']
    )
    return data_fetcher, signal_detector


def create_candlestick_chart(df, config):
    """创建K线图和指标图表"""
    # 创建子图：K线+BOLL, RSI
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=('价格 & 布林带 (BOLL)', 'RSI指标')
    )
    
    # === 第1行：K线和BOLL ===
    # K线图
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # BOLL上轨
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['boll_upper'],
            name='BOLL上轨',
            line=dict(color='rgba(255, 99, 132, 0.8)', width=1, dash='dot')
        ),
        row=1, col=1
    )
    
    # BOLL中轨
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['boll_middle'],
            name='BOLL中轨',
            line=dict(color='rgba(54, 162, 235, 0.8)', width=2)
        ),
        row=1, col=1
    )
    
    # BOLL下轨
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['boll_lower'],
            name='BOLL下轨',
            line=dict(color='rgba(255, 99, 132, 0.8)', width=1, dash='dot')
        ),
        row=1, col=1
    )
    
    # === 第2行：RSI ===
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['rsi'],
            name='RSI',
            line=dict(color='rgba(156, 39, 176, 1)', width=2)
        ),
        row=2, col=1
    )
    
    # RSI超买线
    fig.add_hline(
        y=config['rsi']['overbought'],
        line_dash="dash",
        line_color="red",
        annotation_text="超买",
        row=2, col=1
    )
    
    # RSI超卖线
    fig.add_hline(
        y=config['rsi']['oversold'],
        line_dash="dash",
        line_color="green",
        annotation_text="超卖",
        row=2, col=1
    )
    
    # RSI中线
    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="gray",
        row=2, col=1
    )
    
    # 更新布局
    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    fig.update_xaxes(title_text="时间", row=2, col=1)
    fig.update_yaxes(title_text="价格 (USDT)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    
    return fig


def display_signal_card(signal):
    """显示信号卡片"""
    signal_type = signal['signal_type']
    
    if signal_type == SignalType.LONG:
        st.markdown(f"""
        <div class="signal-long">
            🟢 <strong>做多信号</strong><br>
            信号强度: {signal['strength']:.1f}%<br>
            原因: {signal['reason']}<br>
            时间: {signal['timestamp']}
        </div>
        """, unsafe_allow_html=True)
    elif signal_type == SignalType.SHORT:
        st.markdown(f"""
        <div class="signal-short">
            🔴 <strong>做空信号</strong><br>
            信号强度: {signal['strength']:.1f}%<br>
            原因: {signal['reason']}<br>
            时间: {signal['timestamp']}
        </div>
        """, unsafe_allow_html=True)
    elif signal_type == SignalType.EXIT_LONG:
        st.markdown(f"""
        <div class="signal-neutral">
            ⬆️ <strong>平多信号</strong><br>
            原因: {signal['reason']}<br>
            时间: {signal['timestamp']}
        </div>
        """, unsafe_allow_html=True)
    elif signal_type == SignalType.EXIT_SHORT:
        st.markdown(f"""
        <div class="signal-neutral">
            ⬇️ <strong>平空信号</strong><br>
            原因: {signal['reason']}<br>
            时间: {signal['timestamp']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-neutral">
            ⚪ <strong>无明显信号</strong><br>
            建议: 观望等待<br>
            时间: {signal['timestamp']}
        </div>
        """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-header">📈 ETH合约开单提醒系统</div>', unsafe_allow_html=True)
    st.markdown('---')
    
    # 加载配置
    config = load_config()
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 参数配置")
        
        # 交易对
        symbol = st.text_input("交易对", value=config['symbol'])
        config['symbol'] = symbol
        
        # 时间周期
        timeframe = st.selectbox(
            "时间周期",
            options=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
            index=['1m', '5m', '15m', '30m', '1h', '4h', '1d'].index(config['timeframe'])
        )
        config['timeframe'] = timeframe
        
        st.markdown("---")
        st.subheader("📊 BOLL参数")
        boll_period = st.slider("BOLL周期", 10, 50, config['boll']['period'])
        boll_std = st.slider("BOLL标准差", 1.0, 3.0, float(config['boll']['std_dev']), 0.1)
        config['boll']['period'] = boll_period
        config['boll']['std_dev'] = boll_std
        
        st.markdown("---")
        st.subheader("📉 RSI参数")
        rsi_period = st.slider("RSI周期", 5, 30, config['rsi']['period'])
        rsi_overbought = st.slider("RSI超买线", 60, 90, config['rsi']['overbought'])
        rsi_oversold = st.slider("RSI超卖线", 10, 40, config['rsi']['oversold'])
        config['rsi']['period'] = rsi_period
        config['rsi']['overbought'] = rsi_overbought
        config['rsi']['oversold'] = rsi_oversold
        
        st.markdown("---")
        auto_refresh = st.checkbox("自动刷新", value=True)
        refresh_interval = st.slider("刷新间隔(秒)", 10, 300, 60)
        
        if st.button("🔄 立即刷新", use_container_width=True):
            st.rerun()
    
    # 初始化模块
    data_fetcher, signal_detector = init_modules(config)
    
    # 获取数据
    with st.spinner('📡 正在获取数据...'):
        df = data_fetcher.fetch_kline_data(
            symbol=config['symbol'],
            timeframe=config['timeframe'],
            limit=100
        )
    
    if df is None:
        st.error("❌ 无法获取数据，请检查网络连接和代理设置")
        return
    
    # 计算指标
    df = calculate_all_indicators(
        df,
        boll_period=config['boll']['period'],
        boll_std=config['boll']['std_dev'],
        rsi_period=config['rsi']['period']
    )
    
    # 获取最新指标
    indicators = get_latest_indicators(df)
    
    # 检测信号
    signal = signal_detector.detect_signal(indicators)
    
    # === 显示指标面板 ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 当前价格",
            value=f"${indicators['close']:,.2f}",
            delta=None
        )
    
    with col2:
        rsi_val = indicators['rsi']
        rsi_delta = "超买" if rsi_val > config['rsi']['overbought'] else "超卖" if rsi_val < config['rsi']['oversold'] else "中性"
        st.metric(
            label="📊 RSI指标",
            value=f"{rsi_val:.2f}",
            delta=rsi_delta
        )
    
    with col3:
        st.metric(
            label="📈 BOLL位置",
            value=f"{indicators['boll_position']:.1f}%",
            delta="上轨附近" if indicators['boll_position'] > 80 else "下轨附近" if indicators['boll_position'] < 20 else "中轨附近"
        )
    
    with col4:
        st.metric(
            label="🎯 信号强度",
            value=f"{signal['strength']:.1f}%",
            delta=signal['signal_type'].value if signal['strength'] > 0 else "无信号"
        )
    
    st.markdown("---")
    
    # === 信号提醒 ===
    st.subheader("🚨 交易信号")
    display_signal_card(signal)
    
    st.markdown("---")
    
    # === 图表展示 ===
    st.subheader("📊 技术图表")
    fig = create_candlestick_chart(df, config)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # === 历史信号 ===
    st.subheader("📜 历史信号记录")
    
    # 尝试加载历史
    try:
        with open('signals_history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if history:
            # 只显示最近10条
            recent_history = history[-10:][::-1]  # 倒序
            
            history_df = pd.DataFrame(recent_history)
            st.dataframe(
                history_df[['timestamp', 'symbol', 'signal_type', 'strength', 'reason']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("暂无历史信号记录")
    except:
        st.info("暂无历史信号记录")
    
    # 自动刷新
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == '__main__':
    main()
