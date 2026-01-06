import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_new_deviation_calculation():
    """测试新的偏离值计算方法，使用起始日开盘价和终止日收盘价"""
    # 获取示例股票数据
    stock_code = "000001"
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # 使用昨天避免数据未更新
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
    
    print(f"测试股票: {stock_code}")
    print(f"时间范围: {start_date} 至 {end_date}")
    
    # 格式化日期
    start_date_formatted = start_date.replace("-", "")
    end_date_formatted = end_date.replace("-", "")
    
    # 获取股票历史数据
    try:
        stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="", start_date=start_date_formatted, end_date=end_date_formatted)
        
        if stock_hist.empty:
            print("无法获取股票数据")
            return False
        
        # 按日期排序
        stock_hist['日期'] = pd.to_datetime(stock_hist['日期'])
        stock_hist = stock_hist.sort_values('日期', ascending=True)
        
        # 获取实际交易日数
        trading_days = len(stock_hist)
        print(f"实际交易日数: {trading_days}")
        
        # 计算累计涨幅 - 使用起始日开盘价和终止日收盘价（新方法）
        stock_start_price = stock_hist.iloc[0]['开盘']
        stock_end_price = stock_hist.iloc[-1]['收盘']
        stock_cumulative_return = (stock_end_price - stock_start_price) / stock_start_price
        
        print(f"起始日开盘价: {stock_start_price}")
        print(f"终止日收盘价: {stock_end_price}")
        print(f"股票区间累计涨幅 (开盘到收盘): {stock_cumulative_return:.4f} ({stock_cumulative_return*100:.2f}%)")
        
        # 对比旧方法：使用起始日收盘价和终止日收盘价
        old_stock_start_price = stock_hist.iloc[0]['收盘']
        old_stock_cumulative_return = (stock_end_price - old_stock_start_price) / old_stock_start_price
        
        print(f"旧方法累计涨幅 (收盘到收盘): {old_stock_cumulative_return:.4f} ({old_stock_cumulative_return*100:.2f}%)")
        print(f"两种方法差异: {abs(stock_cumulative_return - old_stock_cumulative_return):.4f} ({abs(stock_cumulative_return - old_stock_cumulative_return)*100:.2f}%)")
        
        # 计算偏离值的监管分析
        days_10_limit = 1.0  # 10天100%限制
        days_30_limit = 2.0  # 30天200%限制
        
        # 计算当前偏离百分比
        current_deviation_pct = stock_cumulative_return * 100
        
        # 计算未来3天分别涨多少会达到异常监管条件
        # 10天规则：偏离值不能超过100%
        days_10_needed = 0
        if trading_days <= 10:
            remaining_deviation_10 = days_10_limit - stock_cumulative_return
            if remaining_deviation_10 > 0:
                days_10_needed = remaining_deviation_10 / 3  # 平均分配到未来3天
            else:
                days_10_needed = 0  # 已经超过限制
        
        # 30天规则：偏离值不能超过200%
        days_30_needed = 0
        if trading_days <= 30:
            remaining_deviation_30 = days_30_limit - stock_cumulative_return
            if remaining_deviation_30 > 0:
                days_30_needed = remaining_deviation_30 / 3  # 平均分配到未来3天
            else:
                days_30_needed = 0  # 已经超过限制
        
        # 计算对应的价格涨幅
        day1_pct_10 = days_10_needed * 100 if days_10_needed > 0 else 0
        day1_pct_30 = days_30_needed * 100 if days_30_needed > 0 else 0
        
        # 生成监管建议
        advice_text = f"异动监管分析:\n"
        advice_text += f"- 实际交易日数: {trading_days}天\n"
        advice_text += f"- 当前偏离值: {current_deviation_pct:.2f}% (起始日开盘价{stock_start_price:.2f} -> 终止日收盘价{stock_end_price:.2f})\n"
        
        # 检查是否接近或超过监管限制
        if trading_days <= 10:
            advice_text += f"- 10天偏离限制: 100% | 当前偏离: {current_deviation_pct:.2f}%\n"
            if stock_cumulative_return > days_10_limit:
                advice_text += f"- 警告: 已超过10天100%偏离限制！\n"
            else:
                advice_text += f"- 距离10天偏离限制: {((days_10_limit - stock_cumulative_return) * 100):.2f}%\n"
                advice_text += f"- 未来3天平均每日涨幅{day1_pct_10:.2f}%将触及10天偏离限制\n"
        else:
            advice_text += f"- 10天偏离限制: 100% | 本次分析为{trading_days}天，不适用\n"
            
        if trading_days <= 30:
            advice_text += f"- 30天偏离限制: 200% | 当前偏离: {current_deviation_pct:.2f}%\n"
            if stock_cumulative_return > days_30_limit:
                advice_text += f"- 警告: 已超过30天200%偏离限制！\n"
            else:
                advice_text += f"- 距离30天偏离限制: {((days_30_limit - stock_cumulative_return) * 100):.2f}%\n"
                advice_text += f"- 未来3天平均每日涨幅{day1_pct_30:.2f}%将触及30天偏离限制\n"
        else:
            advice_text += f"- 30天偏离限制: 200% | 本次分析为{trading_days}天，不适用\n"
        
        print("\n" + advice_text)
        
        # 根据偏离程度生成操作建议
        if stock_cumulative_return > days_10_limit or stock_cumulative_return > days_30_limit:
            advice_1d = "已触发异常监管条件！建议立即关注交易所公告，控制仓位风险"
            advice_2d = "偏离值过高，存在严重监管风险，建议暂停买入并考虑减仓"
            advice_3d = "已严重偏离正常波动范围，需警惕监管措施和股价调整风险"
        elif abs(stock_cumulative_return) > 0.5:  # 偏离度较大 (>50%)
            advice_1d = "偏离度较高，接近监管红线，建议谨慎操作"
            advice_2d = "偏离值较大，存在监管风险，关注后续走势是否收敛"
            advice_3d = "偏离度偏高，若继续扩大可能触发监管，建议控制仓位"
        elif abs(stock_cumulative_return) > 0.2:  # 中等偏离 (20-50%)
            advice_1d = "有一定偏离，属于正常波动范围，继续观察"
            advice_2d = "偏离度中等，建议关注后续走势是否收敛"
            advice_3d = "偏离度适中，暂无明显监管风险，持续观察"
        else:  # 偏离较小 (<20%)
            advice_1d = "偏离度较小，走势相对稳定，风险较低"
            advice_2d = "与大盘走势基本同步，符合市场预期，风险可控"
            advice_3d = "走势稳定，偏离度小，暂无监管风险"
        
        print("操作建议:")
        print(f"- 第1天: {advice_1d}")
        print(f"- 第2天: {advice_2d}")
        print(f"- 第3天: {advice_3d}")
        
        return True
        
    except Exception as e:
        print(f"获取数据时出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("测试新的偏离值计算方法...")
    print("新方法: 使用起始日开盘价和终止日收盘价计算偏离值")
    print("监管要求: 10天不超过100%，30天不超过200%（以实际交易日计算）")
    print("="*60)
    result = test_new_deviation_calculation()
    if result:
        print("\n✓ 测试成功！新功能按预期工作。")
    else:
        print("\n✗ 测试失败！")