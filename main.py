import ccxt
import pandas as pd
import numpy as np
from datetime import datetime



# Функция для получения исторических данных
def get_historical_data(symbol, timeframe, start_date, end_date):
    exchange = ccxt.binance()  # Используем Binance для получения данных
    since = exchange.parse8601(start_date)
    end_timestamp = exchange.parse8601(end_date)

    all_ohlcv = []
    while since < end_timestamp:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
        if not ohlcv:
            break
        since = ohlcv[-1][0] + 1  # Переход к следующему временному интервалу
        all_ohlcv.extend(ohlcv)

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df


# Функция для расчета grid-стратегии
def grid_bot_analysis(df, profit_percent, grid_levels):
    # Создаем grid-уровни (цены)
    grid_prices = np.linspace(df['low'].min(), df['high'].max(), grid_levels)

    # Имитация сделок
    trades = []
    position = None
    for price in df['close']:
        if position is None:
            # Ищем уровень для покупки
            for buy_price in grid_prices:
                if price <= buy_price:
                    position = buy_price
                    break
        else:
            # Ищем уровень для продажи
            sell_price = position * (1 + profit_percent / 100)
            if price >= sell_price:
                profit = (sell_price - position) / position * 100
                trades.append(profit)
                position = None

    if trades:
        total_profit = sum(trades)
        annualized_return = (total_profit / len(trades)) * (365 / (df.index[-1] - df.index[0]).days)
        return len(trades), total_profit, annualized_return
    else:
        return 0, 0, 0


# Основная функция
def main():
    symbol = 'BTC/USDT'  # Пара для торговли
    timeframe = '1m'  # Таймфрейм (1 час)
    start_date = '2025-01-01T00:00:00Z'  # Начальная дата
    end_date = '2025-01-05T00:00:00Z'  # Конечная дата
    profit_percent = 0.1  # Процент прибыли для каждой сделки
    grid_levels = 1000  # Количество уровней grid-сетки

    # Получаем исторические данные
    df = get_historical_data(symbol, timeframe, start_date, end_date)

    # Анализируем grid-стратегию
    num_trades, total_profit, annualized_return = grid_bot_analysis(df, profit_percent, grid_levels)

    # Выводим результаты
    print(f"Количество успешных сделок: {num_trades}")
    print(f"Общая прибыль: {total_profit:.2f}%")
    print(f"Годовая доходность: {annualized_return:.2f}%")


if __name__ == "__main__":
    main()
