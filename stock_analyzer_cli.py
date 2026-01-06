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

def generate_advice(deviation_10d, deviation_30d):
    """
    根据偏离值生成异动监管建议
    """
    # 根据偏离值的大小和方向给出不同的建议
    abs_dev_10d = abs(deviation_10d)
    abs_dev_30d = abs(deviation_30d)
    
    # 综合评估偏离程度
    avg_deviation = (abs_dev_10d + abs_dev_30d) / 2
    
    # 生成建议
    if avg_deviation > 0.05:  # 偏离度较大
        if deviation_10d > 0 and deviation_30d > 0:
            # 持续强势
            advice_1d = "股票表现强势，偏离大盘较多，注意监管风险，建议关注资金流向"
            advice_2d = "强势股需关注后续资金持续性，警惕高位调整风险"
            advice_3d = "若偏离度持续扩大，可能触发异动监管，建议谨慎操作"
        elif deviation_10d < 0 and deviation_30d < 0:
            # 持续弱势
            advice_1d = "股票表现弱势，持续跑输大盘，关注基本面变化"
            advice_2d = "弱势股需关注是否有资金抄底，或存在利空消息"
            advice_3d = "若持续弱势，可能影响投资者信心，建议等待企稳信号"
        else:
            # 交叉情况
            advice_1d = "股票短期偏离与长期偏离方向不一致，需关注趋势变化"
            advice_2d = "注意短期波动可能放大，建议控制仓位"
            advice_3d = "密切关注后续走势，判断是短期修正还是趋势转换"
    elif avg_deviation > 0.02:  # 中等偏离
        advice_1d = "股票有一定偏离，属于正常波动范围，继续观察"
        advice_2d = "偏离度中等，建议关注后续走势是否收敛"
        advice_3d = "偏离度适中，暂无明显监管风险，持续观察"
    else:  # 偏离较小
        advice_1d = "股票走势与大盘基本同步，偏离度较小，风险较低"
        advice_2d = "与大盘同步运行，符合市场预期，风险可控"
        advice_3d = "走势稳定，偏离度小，暂无监管风险"
    
    return advice_1d, advice_2d, advice_3d

def analyze_stock(stock_code):
    """
    分析股票的偏离值和生成监管建议
    """
    print(f"正在获取股票 {stock_code} 的数据...")
    
    # 根据股票代码格式添加后缀
    if stock_code.startswith("6"):
        stock_code_full = f"{stock_code}.SH"
    else:
        stock_code_full = f"{stock_code}.SZ"
        
    # 获取股票历史数据
    try:
        stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="")
        
        if stock_hist.empty:
            print("无法获取股票数据，请检查股票代码是否正确")
            return
    except Exception as e:
        print(f"获取股票数据时出现错误: {str(e)}")
        return

    print("正在获取大盘数据...")
    
    try:
        # 获取大盘数据（上证指数）
        index_data = ak.stock_zh_index_daily_em(symbol="sh000001")
        
        if index_data.empty:
            print("无法获取大盘数据")
            return
    except Exception as e:
        print(f"获取大盘数据时出现错误: {str(e)}")
        return

    print("正在计算偏离值...")
    
    # 数据预处理
    stock_hist['日期'] = pd.to_datetime(stock_hist['日期'])
    index_data['date'] = pd.to_datetime(index_data['date'])
    
    # 按日期排序
    stock_hist = stock_hist.sort_values('日期', ascending=False)
    index_data = index_data.sort_values('date', ascending=False)
    
    # 计算收益率
    stock_hist['收益率'] = stock_hist['收盘'].pct_change()
    index_data['收益率'] = index_data['close'].pct_change()
    
    # 重命名日期列以便合并
    stock_hist_renamed = stock_hist.rename(columns={'日期': 'date'})
    
    # 合并数据
    merged_data = pd.merge(stock_hist_renamed[['date', '收益率']], 
                         index_data[['date', '收益率']], 
                         on='date', 
                         suffixes=('_stock', '_index'))
    
    # 删除缺失值
    merged_data = merged_data.dropna()
    
    if len(merged_data) < 30:
        print("数据不足，无法进行分析")
        return
        
    # 计算10天和30天偏离值
    recent_data = merged_data.head(33)  # 多取3天以确保有足够数据
    stock_returns = recent_data['收益率_stock'].values
    index_returns = recent_data['收益率_index'].values
    
    # 计算偏离值
    deviation_10d = calculate_deviation(stock_returns[:10], index_returns[:10])
    deviation_30d = calculate_deviation(stock_returns[:30], index_returns[:30])
    
    print("正在生成异动监管建议...")
    
    advice_1d, advice_2d, advice_3d = generate_advice(deviation_10d, deviation_30d)
    
    # 显示结果
    result = f"""
股票代码: {stock_code}
分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

偏离值分析:
- 10天相对大盘偏离值: {deviation_10d:.4f}
- 30天相对大盘偏离值: {deviation_30d:.4f}

异动监管建议:
- 第1天: {advice_1d}
- 第2天: {advice_2d}
- 第3天: {advice_3d}

分析完成！
    """
    
    print(result)
    return deviation_10d, deviation_30d, advice_1d, advice_2d, advice_3d

if __name__ == "__main__":
    print("A股股票异动监管建议工具（命令行版）")
    stock_code = input("请输入A股股票代码（如：000001）: ")
    
    if stock_code.strip():
        analyze_stock(stock_code.strip())
    else:
        print("请输入有效的股票代码")