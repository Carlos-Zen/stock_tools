#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试A股股票异动监管建议工具的功能
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_date_format_conversion():
    """测试日期格式转换功能"""
    print("测试日期格式转换...")
    start_date = "2025-12-01"
    end_date = "2026-01-01"
    
    start_date_formatted = start_date.replace("-", "")
    end_date_formatted = end_date.replace("-", "")
    
    print(f"原始日期: {start_date} -> {end_date}")
    print(f"转换后: {start_date_formatted} -> {end_date_formatted}")
    
    assert start_date_formatted == "20251201"
    assert end_date_formatted == "20260101"
    print("✓ 日期格式转换测试通过\n")

def test_stock_data_fetch():
    """测试股票数据获取功能"""
    print("测试股票数据获取...")
    
    stock_code = '000001'
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # 昨天
    start_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')  # 15天前
    
    # 将日期格式转换为YYYYMMDD
    start_date_formatted = start_date.replace('-', '')
    end_date_formatted = end_date.replace('-', '')
    
    print(f"获取股票 {stock_code} 从 {start_date_formatted} 到 {end_date_formatted} 的数据...")
    
    try:
        stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust='', start_date=start_date_formatted, end_date=end_date_formatted)
        
        if not stock_hist.empty:
            print(f"✓ 成功获取股票数据，共{len(stock_hist)}条记录")
            print(f"  股票数据列: {list(stock_hist.columns)}")
            return True
        else:
            print("✗ 无法获取股票数据")
            return False
    except Exception as e:
        print(f"✗ 获取股票数据时出现错误: {str(e)}")
        return False

def test_index_data_fetch():
    """测试指数数据获取功能"""
    print("\n测试指数数据获取...")
    
    # 根据股票代码确定对应的大盘指数
    stock_code = '000001'
    if stock_code.startswith('6'):
        index_symbol = 'sh000001'
        index_name = '上证指数'
    elif stock_code.startswith('300') or stock_code.startswith('301'):
        index_symbol = 'sz399006'
        index_name = '创业板指'
    elif stock_code.startswith('00'):
        index_symbol = 'sz399001'
        index_name = '深证成指'
    else:
        index_symbol = 'sh000001'
        index_name = '上证指数'
    
    try:
        index_data = ak.stock_zh_index_daily_em(symbol=index_symbol)
        
        if not index_data.empty:
            print(f"✓ 成功获取{index_name}数据，共{len(index_data)}条记录")
            return True
        else:
            print(f"✗ 无法获取{index_name}数据")
            return False
    except Exception as e:
        print(f"✗ 获取{index_name}数据时出现错误: {str(e)}")
        return False

def test_calculate_returns():
    """测试收益率计算功能"""
    print("\n测试收益率计算...")
    
    stock_code = '000001'
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
    
    # 将日期格式转换为YYYYMMDD
    start_date_formatted = start_date.replace('-', '')
    end_date_formatted = end_date.replace('-', '')
    
    # 获取股票历史数据
    stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period='daily', adjust='', start_date=start_date_formatted, end_date=end_date_formatted)
    
    if stock_hist.empty:
        print("✗ 无法获取股票数据进行收益率计算测试")
        return False
    
    # 数据预处理
    stock_hist['日期'] = pd.to_datetime(stock_hist['日期'])
    stock_hist = stock_hist.sort_values('日期', ascending=True)
    
    # 计算累计涨幅
    stock_start_price = stock_hist.iloc[0]['收盘']
    stock_end_price = stock_hist.iloc[-1]['收盘']
    stock_cumulative_return = (stock_end_price - stock_start_price) / stock_start_price
    
    print(f"股票累计涨幅: {stock_cumulative_return:.4f} ({stock_cumulative_return*100:.2f}%)")
    
    # 计算日收益率
    stock_hist['收益率'] = stock_hist['收盘'].pct_change()
    avg_daily_return = stock_hist['收益率'].mean()
    
    print(f"股票平均日收益率: {avg_daily_return:.4f} ({avg_daily_return*100:.2f}%)")
    print("✓ 收益率计算测试通过")
    return True

def test_market_detection():
    """测试市场识别功能"""
    print("\n测试市场识别...")
    
    test_cases = [
        ('000001', '深证成指'),
        ('600000', '上证指数'),
        ('300750', '创业板指'),
        ('002001', '深证成指')
    ]
    
    for stock_code, expected_index in test_cases:
        if stock_code.startswith('6'):
            index_symbol = 'sh000001'
            index_name = '上证指数'
        elif stock_code.startswith('300') or stock_code.startswith('301'):
            index_symbol = 'sz399006'
            index_name = '创业板指'
        elif stock_code.startswith('00'):
            index_symbol = 'sz399001'
            index_name = '深证成指'
        else:
            index_symbol = 'sh000001'
            index_name = '上证指数'
        
        print(f"股票代码: {stock_code} -> 识别为: {index_name} (期望: {expected_index})")
        assert index_name == expected_index, f"市场识别错误: 期望{expected_index}, 实际{index_name}"
    
    print("✓ 市场识别测试通过")
    return True

def main():
    """主测试函数"""
    print("开始测试A股股票异动监管建议工具功能...\n")
    
    all_tests_passed = True
    
    try:
        test_date_format_conversion()
        all_tests_passed &= test_stock_data_fetch()
        all_tests_passed &= test_index_data_fetch()
        all_tests_passed &= test_calculate_returns()
        all_tests_passed &= test_market_detection()
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        all_tests_passed = False
    
    print("\n" + "="*50)
    if all_tests_passed:
        print("✓ 所有测试通过！工具功能正常。")
    else:
        print("✗ 部分测试失败，请检查代码。")
    print("="*50)
    
    return all_tests_passed

if __name__ == "__main__":
    main()