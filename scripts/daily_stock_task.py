#!/usr/bin/env python3
"""
股票晚间综合任务
1. 生成当日复盘报告
2. 整合到飞书消息
"""
import subprocess
import json
import os
from datetime import datetime

def run():
    date_str = datetime.now().strftime('%Y%m%d')
    output_dir = "/home/dhtaiyi/.openclaw/workspace/stock-analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # 运行分析脚本
    result = subprocess.run(
        ['python3', '/home/dhtaiyi/.openclaw/workspace/scripts/stock_analyzer.py'],
        capture_output=True,
        text=True,
        timeout=30,
        cwd='/home/dhtaiyi/.openclaw/workspace'
    )
    
    report_text = result.stdout
    
    # 保存文本报告
    text_file = f"{output_dir}/report_text_{date_str}.txt"
    with open(text_file, 'w') as f:
        f.write(report_text)
    
    # 读取JSON报告
    json_file = f"{output_dir}/report_{date_str}.json"
    try:
        with open(json_file) as f:
            report_data = json.load(f)
    except:
        report_data = {}
    
    return report_text, report_data

if __name__ == "__main__":
    text, data = run()
    print(text)
    print("\n✅ 报告已保存")
