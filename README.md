# Objective
This backtesting framework is designed for China's A-shares market, leveraging the advantages of Joinquant and Backtrader, based on my use experiences.

Joinquant(www.joinquant.com) is an online powerful backtesting framework that is easy to use. Even beginners can quickly figure out how to develop and share their own strategies with Joinquant. This attracts many users, making it the biggest quant forum in China. However, Joinquant cannot cater to the needs of modern data mining techniques. It does not support deep learning packages like Pytorch and TensorFlow and has serious speed problems while backtesting. This limits the diversity and complexity of my strategies and significantly drags the progress of my strategy development. To overcome its limitations while leveraging its advantages, I developed a local backtesting framework with well-designed APIs, strong speed performance, and good scalability.

# Instrument
## Datafeed
To use this framework, you should have access to two MySQL databases, named 'stock' and 'index'. The 'stock' database should contain tables, and each table contains time series data for one stock. Ensure the table name is like 'xxxxxx.sz' (Shenzhen Exchange) or 'xxxxxx.sh' (Shanghai Exchange). Similarly, the 'index' database should contain indexes such as CSI 300.

## Strategy
Develop your strategy in userStrategy.py, then run the following to backtest:
'
python run.py
'


# Todo
- support limit order
- support dynamic restoration of rights
- support other data feeds.
- provide additional APIs for training and testing machine learning models
- provide automatic metric calculations

# Requirements 
- matplotlib==3.7.1
- pandas==1.4.2
- numpy==1.24.4

