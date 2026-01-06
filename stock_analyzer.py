import customtkinter as ctk
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
from tkinter import ttk

class StockAnalyzerApp:
    def __init__(self):
        # 设置外观
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("A股股票异动监管建议工具")
        self.root.geometry("800x700")
        
        # 创建UI元素
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = ctk.CTkLabel(self.root, text="A股股票异动监管建议工具", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)
        
        # 股票代码输入
        input_frame = ctk.CTkFrame(self.root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        stock_code_label = ctk.CTkLabel(input_frame, text="股票代码:")
        stock_code_label.pack(side="left", padx=10, pady=10)
        
        self.stock_code_entry = ctk.CTkEntry(input_frame, placeholder_text="输入A股股票代码，如：000001")
        self.stock_code_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # 分析按钮
        analyze_button = ctk.CTkButton(input_frame, text="开始分析", command=self.start_analysis)
        analyze_button.pack(side="right", padx=10, pady=10)
        
        # 时间范围选择
        time_frame = ctk.CTkFrame(self.root)
        time_frame.pack(pady=10, padx=20, fill="x")
        
        time_label = ctk.CTkLabel(time_frame, text="时间范围:")
        time_label.pack(side="left", padx=10, pady=10)
        
        # 快捷选项
        quick_buttons_frame = ctk.CTkFrame(time_frame)
        quick_buttons_frame.pack(side="right", padx=10, pady=10)
        
        quick_10d_button = ctk.CTkButton(quick_buttons_frame, text="近10天", command=lambda: self.set_time_range(10))
        quick_10d_button.pack(side="left", padx=5)
        
        quick_30d_button = ctk.CTkButton(quick_buttons_frame, text="近30天", command=lambda: self.set_time_range(30))
        quick_30d_button.pack(side="left", padx=5)
        
        # 自定义时间范围
        custom_frame = ctk.CTkFrame(time_frame)
        custom_frame.pack(pady=5, padx=10, fill="x", expand=True)
        
        # 起始日期
        start_date_label = ctk.CTkLabel(custom_frame, text="起始日期:")
        start_date_label.pack(side="left", padx=5, pady=5)
        
        self.start_date_entry = ctk.CTkEntry(custom_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=5, pady=5)
        
        # 结束日期
        end_date_label = ctk.CTkLabel(custom_frame, text="结束日期:")
        end_date_label.pack(side="left", padx=5, pady=5)
        
        self.end_date_entry = ctk.CTkEntry(custom_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=5, pady=5)
        
        # 设置默认日期为最近30天
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.start_date_entry.insert(0, start_date)
        self.end_date_entry.insert(0, end_date)
        
        # 结果显示区域
        self.result_textbox = ctk.CTkTextbox(self.root, width=760, height=500)
        self.result_textbox.pack(pady=20, padx=20, fill="both", expand=True)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        
    def set_time_range(self, days):
        """设置时间范围为最近N天"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, start_date)
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, end_date)
    
    def start_analysis(self):
        # 在新线程中执行分析，避免UI冻结
        thread = threading.Thread(target=self.analyze_stock)
        thread.daemon = True
        thread.start()
        
    def analyze_stock(self):
        # 更新UI
        self.root.after(0, self.update_ui_for_analysis)
        
        try:
            stock_code = self.stock_code_entry.get().strip()
            if not stock_code:
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "请输入股票代码\n"))
                return
                
            # 获取时间范围
            start_date = self.start_date_entry.get().strip()
            end_date = self.end_date_entry.get().strip()
            
            if not start_date or not end_date:
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "请输入起止日期\n"))
                return
                
            # 获取股票数据
            self.root.after(0, lambda: self.result_textbox.insert("0.0", f"正在获取股票 {stock_code} 的数据...\n"))
            self.root.after(0, lambda: self.progress_bar.set(0.2))
            
            # 根据股票代码格式添加后缀
            if stock_code.startswith("6"):
                stock_code_full = f"{stock_code}.SH"
                # 获取上证指数数据
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
            stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="", start_date=start_date_formatted, end_date=end_date_formatted)
            
            if stock_hist.empty:
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "无法获取股票数据，请检查股票代码和日期范围是否正确\n"))
                return
                
            # 获取大盘数据
            self.root.after(0, lambda: self.result_textbox.insert("0.0", f"正在获取{index_name}数据...\n"))
            self.root.after(0, lambda: self.progress_bar.set(0.4))
            
            index_data = ak.stock_zh_index_daily_em(symbol=index_symbol)
            
            if index_data.empty:
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "无法获取大盘数据\n"))
                return
            
            # 计算累计涨幅
            self.root.after(0, lambda: self.progress_bar.set(0.5))
            
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
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "指数数据不足，无法进行分析\n"))
                return
            
            index_start_price = index_filtered.iloc[0]['close']
            index_end_price = index_filtered.iloc[-1]['close']
            index_cumulative_return = (index_end_price - index_start_price) / index_start_price
            
            # 计算偏离值
            self.root.after(0, lambda: self.result_textbox.insert("0.0", "正在计算偏离值...\n"))
            self.root.after(0, lambda: self.progress_bar.set(0.6))
            
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
                self.root.after(0, lambda: self.result_textbox.insert("0.0", "数据不足，无法进行分析\n"))
                return
                
            # 计算平均收益率
            stock_avg_return = merged_data['收益率_stock'].mean()
            index_avg_return = merged_data['收益率_index'].mean()
            
            # 计算偏离值
            deviation = stock_cumulative_return - index_cumulative_return
            
            # 生成异动监管建议
            self.root.after(0, lambda: self.result_textbox.insert("0.0", "正在生成异动监管建议...\n"))
            self.root.after(0, lambda: self.progress_bar.set(0.8))
            
            advice_1d, advice_2d, advice_3d = self.generate_advice(deviation, stock_avg_return - index_avg_return)
            
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
            
            self.root.after(0, lambda: self.result_textbox.delete("0.0", "end"))
            self.root.after(0, lambda: self.result_textbox.insert("0.0", result))
            
        except Exception as e:
            error_msg = f"分析过程中出现错误: {str(e)}\n"
            self.root.after(0, lambda: self.result_textbox.insert("0.0", error_msg))
        
        # 完成分析
        self.root.after(0, lambda: self.progress_bar.set(1.0))
        self.root.after(0, self.reset_ui_after_analysis)
    
    def calculate_deviation(self, stock_returns, index_returns):
        """
        计算股票相对于大盘的偏离值
        偏离值 = 股票收益率 - 大盘收益率
        """
        if len(stock_returns) == 0 or len(index_returns) == 0:
            return 0.0
            
        stock_avg = np.mean(stock_returns)
        index_avg = np.mean(index_returns)
        
        return stock_avg - index_avg
    
    def generate_advice(self, cumulative_deviation, avg_deviation):
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
    
    def update_ui_for_analysis(self):
        """分析开始时更新UI"""
        self.result_textbox.delete("0.0", "end")
        self.progress_bar.set(0.0)
        self.result_textbox.insert("0.0", "开始分析...\n")
    
    def reset_ui_after_analysis(self):
        """分析完成后重置UI"""
        self.progress_bar.set(0.0)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StockAnalyzerApp()
    app.run()