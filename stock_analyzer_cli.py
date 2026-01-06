import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_deviation(stock_returns, index_returns):
    """
    计算股票相对于大盘的偏离值
    偏离值 = 股票收益率 - 大盘收益率
    """
    if len(stock_returns) == 0 or len(index_returns) == 0:
        return 0.0
        
    stock_avg = np.mean(stock_returns)
    index_avg = np.mean(index_returns)
    
    return stock_avg - index_avg

def generate_advice(cumulative_deviation, avg_deviation):
    """
    根据偏离值生成异动监管建议
    """
    # 根据偏离值的大小和方向给出不同的建议
    abs_cumulative_deviation = abs(cumulative_deviation)
    abs_avg_deviation = abs(avg_deviation)
    
    # 综合评估偏离程度
    avg_deviation = (abs_cumulative_deviation + abs_avg_deviation) / 2
    
    # 生成建议
    if avg_deviation > 0.05:  # 偏离度较大
        if cumulative_deviation > 0:
            # 持续强势
            advice_1d = "股票表现强势，偏离大盘较多，注意监管风险，建议关注资金流向"
            advice_2d = "强势股需关注后续资金持续性，警惕高位调整风险"
            advice_3d = "若偏离度持续扩大，可能触发异动监管，建议谨慎操作"
        else:
            # 持续弱势
            advice_1d = "股票表现弱势，持续跑输大盘，关注基本面变化"
            advice_2d = "弱势股需关注是否有资金抄底，或存在利空消息"
            advice_3d = "若持续弱势，可能影响投资者信心，建议等待企稳信号"
    elif avg_deviation > 0.02:  # 中等偏离
        advice_1d = "股票有一定偏离，属于正常波动范围，继续观察"
        advice_2d = "偏离度中等，建议关注后续走势是否收敛"
        advice_3d = "偏离度适中，暂无明显监管风险，持续观察"
    else:  # 偏离较小
        advice_1d = "股票走势与大盘基本同步，偏离度较小，风险较低"
        advice_2d = "与大盘同步运行，符合市场预期，风险可控"
        advice_3d = "走势稳定，偏离度小，暂无监管风险"
    
    return advice_1d, advice_2d, advice_3d

def analyze_stock(stock_code, start_date, end_date):
    """
    分析股票的偏离值和生成监管建议
    """
    print(f"正在获取股票 {stock_code} 的数据...")
    
    # 根据股票代码格式确定对应的大盘指数
    if stock_code.startswith("6"):
        # 上证股票
        index_symbol = "sh000001"
        index_name = "上证指数"
    elif stock_code.startswith("300") or stock_code.startswith("301"):
        # 创业板股票
        index_symbol = "sz399006"
        index_name = "创业板指"
    elif stock_code.startswith("00"):
        # 深证股票
        index_symbol = "sz399001"
        index_name = "深证成指"
    else:
        # 默认使用上证指数
        index_symbol = "sh000001"
        index_name = "上证指数"
        
    # 将日期格式转换为YYYYMMDD
    start_date_formatted = start_date.replace("-", "")
    end_date_formatted = end_date.replace("-", "")
    
    # 获取股票历史数据
    try:
        stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="", start_date=start_date_formatted, end_date=end_date_formatted)
        
        if stock_hist.empty:
            print("无法获取股票数据，请检查股票代码和日期范围是否正确")
            return
    except Exception as e:
        print(f"获取股票数据时出现错误: {str(e)}")
        return

    print(f"正在获取{index_name}数据...")
    
    try:
        # 获取大盘数据
        index_data = ak.stock_zh_index_daily_em(symbol=index_symbol)
        
        if index_data.empty:
            print("无法获取大盘数据")
            return
    except Exception as e:
        print(f"获取大盘数据时出现错误: {str(e)}")
        return

    # 数据预处理
    stock_hist['日期'] = pd.to_datetime(stock_hist['日期'])
    index_data['date'] = pd.to_datetime(index_data['date'])
    
    # 按日期排序
    stock_hist = stock_hist.sort_values('日期', ascending=True)
    index_data = index_data.sort_values('date', ascending=True)
    
    # 计算累计涨幅
    stock_start_price = stock_hist.iloc[0]['收盘']
    stock_end_price = stock_hist.iloc[-1]['收盘']
    stock_cumulative_return = (stock_end_price - stock_start_price) / stock_start_price
    
    # 找到对应的大盘数据
    start_date_dt = pd.to_datetime(start_date)
    end_date_dt = pd.to_datetime(end_date)
    
    # 筛选指数数据在指定日期范围内
    index_filtered = index_data[(index_data['date'] >= start_date_dt) & (index_data['date'] <= end_date_dt)]
    
    if len(index_filtered) < 2:
        print("指数数据不足，无法进行分析")
        return
    
    index_start_price = index_filtered.iloc[0]['close']
    index_end_price = index_filtered.iloc[-1]['close']
    index_cumulative_return = (index_end_price - index_start_price) / index_start_price

    print("正在计算偏离值...")
    
    # 计算收益率
    stock_hist['收益率'] = stock_hist['收盘'].pct_change()
    index_filtered['收益率'] = index_filtered['close'].pct_change()
    
    # 重命名日期列以便合并
    stock_hist_renamed = stock_hist.rename(columns={'日期': 'date'})
    
    # 合并数据
    merged_data = pd.merge(stock_hist_renamed[['date', '收益率']], 
                         index_filtered[['date', '收益率']], 
                         on='date', 
                         suffixes=('_stock', '_index'))
    
    # 删除缺失值
    merged_data = merged_data.dropna()
    
    if len(merged_data) < 1:
        print("数据不足，无法进行分析")
        return
        
    # 计算平均收益率
    stock_avg_return = merged_data['收益率_stock'].mean()
    index_avg_return = merged_data['收益率_index'].mean()
    
    # 计算偏离值
    deviation = stock_cumulative_return - index_cumulative_return
    
    print("正在生成异动监管建议...")
    
    advice_1d, advice_2d, advice_3d = generate_advice(deviation, stock_avg_return - index_avg_return)
    
    # 显示结果
    result = f"""
股票代码: {stock_code}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
时间范围: {start_date} 至 {end_date}

涨跌幅分析:
- 股票区间累计涨幅: {stock_cumulative_return:.4f} ({stock_cumulative_return*100:.2f}%)
- {index_name}区间累计涨幅: {index_cumulative_return:.4f} ({index_cumulative_return*100:.2f}%)
- 累计涨幅偏离值: {deviation:.4f} ({deviation*100:.2f}%)

异动监管建议:
- 第1天: {advice_1d}
- 第2天: {advice_2d}
- 第3天: {advice_3d}

分析完成！
    """
    
    print(result)
    return stock_cumulative_return, index_cumulative_return, deviation, advice_1d, advice_2d, advice_3d

if __name__ == "__main__":
    print("A股股票异动监管建议工具（命令行版）")
    stock_code = input("请输入A股股票代码（如：000001）: ")
    
    # 获取时间范围
    print("请选择时间范围:")
    print("1. 近10天")
    print("2. 近30天")
    print("3. 自定义时间范围")
    
    choice = input("请输入选择（1/2/3）: ")
    
    if choice == "1":
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
    elif choice == "2":
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif choice == "3":
        start_date = input("请输入起始日期（格式：YYYY-MM-DD）: ")
        end_date = input("请输入结束日期（格式：YYYY-MM-DD）: ")
    else:
        print("无效选择，使用默认近30天")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    if stock_code.strip() and start_date.strip() and end_date.strip():
        analyze_stock(stock_code.strip(), start_date.strip(), end_date.strip())
    else:
        print("请输入有效的股票代码和日期范围")