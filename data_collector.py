import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import warnings
warnings.filterwarnings('ignore')

import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, AccDistIndexIndicator


class AdvancedDataCollector:
    def __init__(self, alpha_vantage_key=None):
        self.av_key = alpha_vantage_key
        self.db_path = 'market_data.db'
        self.setup_database()
        self.symbols_info = {
            'SPY': {'name': 'S&P 500', 'type': 'Stock Index'},
            'QQQ': {'name': 'NASDAQ', 'type': 'Tech Index'},
            'GLD': {'name': 'Gold', 'type': 'Commodity'}
        }

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS daily_data (
            date TEXT, symbol TEXT,
            open REAL, high REAL, low REAL, close REAL, volume INTEGER,
            sma_20 REAL, sma_50 REAL, sma_200 REAL, ema_12 REAL, ema_26 REAL,
            rsi REAL, macd REAL, macd_signal REAL, macd_hist REAL,
            bb_upper REAL, bb_middle REAL, bb_lower REAL, bb_width REAL,
            atr REAL, obv REAL, ad_line REAL,
            price_change REAL, volume_change REAL,
            high_low_pct REAL, open_close_pct REAL,
            target_direction INTEGER, target_return REAL,
            PRIMARY KEY (date, symbol))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS predictions (
            date TEXT, symbol TEXT, prediction TEXT, confidence REAL,
            up_prob REAL, down_prob REAL, actual_direction TEXT, actual_return REAL,
            correct INTEGER, PRIMARY KEY (date, symbol))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS performance_metrics (
            date TEXT, symbol TEXT, strategy_return REAL, benchmark_return REAL,
            cumulative_strategy REAL, cumulative_benchmark REAL,
            drawdown REAL, trades_count INTEGER, win_rate REAL, sharpe_ratio REAL,
            PRIMARY KEY (date, symbol))''')
        conn.commit()
        conn.close()

    def download_stock_data(self, symbols=['SPY','QQQ','GLD'], period='3y'):
        all_data = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                data = stock.history(period=period)
                if len(data) > 0:
                    all_data[symbol] = data
            except Exception as e:
                print(f"Error downloading {symbol}: {e}")
        return all_data

    def calculate_all_indicators(self, df):
        df = df.copy()
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        df['SMA_20'] = SMAIndicator(close, window=20).sma_indicator()
        df['SMA_50'] = SMAIndicator(close, window=50).sma_indicator()
        df['SMA_200'] = SMAIndicator(close, window=200).sma_indicator()
        df['EMA_12'] = EMAIndicator(close, window=12).ema_indicator()
        df['EMA_26'] = EMAIndicator(close, window=26).ema_indicator()

        macd_obj = MACD(close, window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd_obj.macd()
        df['MACD_Signal'] = macd_obj.macd_signal()
        df['MACD_Hist'] = macd_obj.macd_diff()

        df['RSI'] = RSIIndicator(close, window=14).rsi()

        bb = BollingerBands(close, window=20, window_dev=2)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'] * 100

        df['ATR'] = AverageTrueRange(high, low, close, window=14).average_true_range()
        df['OBV'] = OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        df['AD_Line'] = AccDistIndexIndicator(high, low, close, volume).acc_dist_index()

        df['Price_Change'] = close.pct_change()
        df['Volume_Change'] = volume.pct_change()
        df['High_Low_Pct'] = (high - low) / close * 100
        df['Open_Close_Pct'] = (close - df['Open']) / df['Open'] * 100

        df['Next_Open'] = df['Open'].shift(-1)
        df['Next_Close'] = close.shift(-1)
        df['Target_Direction'] = (df['Next_Close'] > df['Next_Open']).astype(int)
        df['Target_Return'] = (df['Next_Close'] - close) / close

        df = df.dropna()
        return df

    def save_to_database(self, df, symbol):
        conn = sqlite3.connect(self.db_path)
        for index, row in df.iterrows():
            conn.execute('''INSERT OR REPLACE INTO daily_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (index.strftime('%Y-%m-%d'), symbol,
                 row['Open'], row['High'], row['Low'], row['Close'], row['Volume'],
                 row['SMA_20'], row['SMA_50'], row['SMA_200'], row['EMA_12'], row['EMA_26'],
                 row['RSI'], row['MACD'], row['MACD_Signal'], row['MACD_Hist'],
                 row['BB_Upper'], row['BB_Middle'], row['BB_Lower'], row['BB_Width'], row['ATR'],
                 row['OBV'], row['AD_Line'],
                 row['Price_Change'], row['Volume_Change'], row['High_Low_Pct'], row['Open_Close_Pct'],
                 row['Target_Direction'], row['Target_Return']))
        conn.commit()
        conn.close()

    def collect_all_data(self, symbols=['SPY','QQQ','GLD']):
        raw_data = self.download_stock_data(symbols)
        for symbol, data in raw_data.items():
            processed_data = self.calculate_all_indicators(data)
            self.save_to_database(processed_data, symbol)
        return len(raw_data)

    def get_latest_features(self, symbol):
        conn = sqlite3.connect(self.db_path)
        query = '''SELECT sma_20,sma_50,ema_12,ema_26,rsi,macd,macd_signal,macd_hist,
                          bb_upper,bb_middle,bb_lower,bb_width,atr,obv,ad_line,
                          price_change,volume_change,high_low_pct,open_close_pct
                   FROM daily_data WHERE symbol=? ORDER BY date DESC LIMIT 1'''
        result = pd.read_sql_query(query, conn, params=(symbol,))
        conn.close()
        if len(result) > 0:
            return result.iloc[0].values
        return None
