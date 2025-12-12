import akshare as ak
import pandas as pd

def get_cb_data(date='20231229'):
    """
    获取指定日期的全市场转债基本数据
    """
    # 获取可转债每日行情
    cb_market_df = ak.bond_cb_jsl()
    # 这个接口数据很全，包含价格、转股价值、溢价率等
    # 你需要从中筛选出你需要的列，并进行清洗
    return cb_market_df

# 尝试获取一天的数据看看
df = get_cb_data()
print(df.columns) # 查看有哪些列
print(df[['债券代码', '债券名称', '现价', '转股价值', '转股溢价率']].head())


def calculate_dual_low(df):
    """
    计算双低值
    """
    # 确保数据是数值类型，非数值转为NaN
    df['现价'] = pd.to_numeric(df['现价'], errors='coerce')
    df['转股溢价率'] = pd.to_numeric(df['转股溢价率'], errors='coerce')

    # 计算双低值：价格 + 溢价率 * 100
    df['双低值'] = df['现价'] + df['转股溢价率'] * 100

    # 按双低值排序
    df = df.sort_values(by='双低值', ascending=True)
    return df