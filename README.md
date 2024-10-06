# Objective
This backtesting framework is designed for China's A-shares market, leveraging the advantages of Joinquant and Backtrader, based on my use experiences.

Joinquant(www.joinquant.com) is an online powerful backtesting framework that is easy to use. Even beginners can quickly figure out how to develop and share their own strategies with Joinquant. This attracts many users, making it the biggest quant forum in China. However, Joinquant cannot cater to the needs of modern data mining techniques. It does not support deep learning packages like Pytorch and TensorFlow and has serious speed problems while backtesting. This limits the diversity and complexity of strategies and significantly drags the progress of strategy development. To overcome its limitations while leveraging its advantages, I developed a local backtesting framework with well-designed APIs, strong speed performance, and good scalability.

# Instrument
## Datafeed
To use this framework, you should have access to two MySQL databases, named 'stock' and 'index'. The 'stock' database should contain tables, and each table contains time series data for one stock. Ensure the table name is like 'xxxxxx.sz' (Shenzhen Exchange) or 'xxxxxx.sh' (Shanghai Exchange). Similarly, the 'index' database should contain indexes such as CSI 300.

You can construct your MySQL databases easily using https://github.com/cpu9xx/MySQLdb-Initial-and-Update-based-on-Tushare.

## Strategy
Develop your strategy in userStrategy.py. If it is the first time loading data, set the "if_load_data" in "userconfig" dict to False. Once you load, a new pickle file named 'data.pkl' will be created, it is used for save data loading time. Then you can directly load data from 'data.pkl' rather than the database by setting "if_load_data" to True. Run the following to backtest:
```
python run.py
```

After backtesting, the profit and loss curve will be automatically presented like this:
<p align="center">
  <img src ="[https://github.com/cpu9xx/LiquidQuant-backtest-framework/blob/main/pnl.png](https://github.com/cpu9xx/LiquidQuant-backtest-framework/blob/main/pnl.png)"/, width=250>
</p>

# Todo
- support limit order
- support dynamic restoration of rights
- support other data feeds
- provide additional APIs for training and testing machine learning models
- provide automatic metric calculations

# Requirements 
- matplotlib==3.7.1
- pandas==1.4.2
- numpy==1.24.4

