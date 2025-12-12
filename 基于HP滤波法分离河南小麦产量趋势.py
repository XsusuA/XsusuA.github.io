import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.filters.hp_filter import hpfilter
from sklearn.metrics import mean_absolute_percentage_error
import os

# ================= 全局样式设置 =================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 支持中文
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = "#C0C0C0"
plt.rcParams['grid.linestyle'] = "--"
plt.rcParams['grid.alpha'] = 0.4
plt.rcParams['axes.facecolor'] = "white"

# ================= 文件路径 =================
data_path = r"E:\game\大创\小麦数据.xlsx"
save_dir = r"E:\game\大创\hp"
os.makedirs(save_dir, exist_ok=True)

# ================= 读取数据 =================
df = pd.read_excel(data_path, header=None)

years = df.iloc[0, 1:].astype(float).astype(int).tolist()
valid_cols = [i for i, y in enumerate(years, start=1) if 2002 <= y <= 2021]
years = [y for y in years if 2002 <= y <= 2021]

yield_df = df.iloc[1:4, valid_cols].copy()
yield_df.insert(0, '城市', df.iloc[1:4, 0])

area_df = df.iloc[5:8, valid_cols].copy()
area_df.insert(0, '城市', df.iloc[5:8, 0])

cities = yield_df['城市'].tolist()
results_summary = []

# EViews 论文色系 RGB
color_yield = (0/255, 102/255, 204/255)   # 蓝色 YIELD
color_trend = (192/255, 0/255, 0/255)     # 红色 TREND
color_cycle = (0/255, 153/255, 0/255)     # 绿色 CYCLE

# ================= 主循环 =================
for city in cities:
    y_data = yield_df[yield_df['城市'] == city].iloc[0, 1:].astype(float).values
    a_data = area_df[area_df['城市'] == city].iloc[0, 1:].astype(float).values
    yield_per_area = y_data * 10 / a_data  # 吨/公顷

    data = pd.DataFrame({'year': years, 'yield_per_area': yield_per_area})
    data.set_index('year', inplace=True)

    # HP滤波
    cycle, trend = hpfilter(data['yield_per_area'], lamb=100)
    data['trend'] = trend
    data['cycle'] = cycle

    # 计算统计量
    rc = np.corrcoef(data['yield_per_area'], data['trend'])[0, 1]
    mape = mean_absolute_percentage_error(data['yield_per_area'], data['trend']) * 100

    results_summary.append({
        '城市': city,
        '相关系数 r_c': round(rc, 4),
        'MAPE(%)': round(mape, 2)
    })

    # ================= 绘制论文风格图 =================
    plt.figure(figsize=(8, 5))
    plt.plot(data.index, data['yield_per_area'], color=color_yield, linewidth=1.8, label="Yield")
    plt.plot(data.index, data['trend'], color=color_trend, linewidth=2.4, label="Trend")
    plt.plot(data.index, data['cycle'], color=color_cycle, linestyle="--", linewidth=1.4, alpha=0.6, label="Cycle")

    plt.title("Hodrick-Prescott Filter (lambda=100)", fontsize=13, weight='bold', pad=10)
    plt.xlabel("Year", fontsize=11)
    plt.ylabel("Yield (ton/hectare)", fontsize=11)
    plt.grid(True)
    plt.xticks(np.arange(2002, 2022, 1))
    plt.xlim(2002, 2021)

    # 图例放在下方居中
    plt.legend(
        loc='lower center',
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        frameon=False,
        fontsize=10
    )

    # 城市标签放在左上角
    plt.text(2002.2, max(data['yield_per_area']) * 0.98, city, fontsize=12, weight='bold')

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    # ================= 保存 =================
    img_path = os.path.join(save_dir, f"{city}_HP滤波结果_论文风格.png")
    excel_path = os.path.join(save_dir, f"{city}_HP滤波数据.xlsx")
    plt.savefig(img_path, dpi=400, bbox_inches='tight')
    plt.close()
    data.to_excel(excel_path)

    print(f"✅ {city} 完成：r_c={rc:.4f}, MAPE={mape:.2f}%")

# ================= 汇总 =================
summary_df = pd.DataFrame(results_summary)
summary_path = os.path.join(save_dir, "HP滤波结果汇总.xlsx")
summary_df.to_excel(summary_path, index=False)

print("\n🎯 所有城市处理完成！输出路径：")
print(summary_df)
