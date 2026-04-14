import pandas as pd
import matplotlib.pyplot as plt

"""
Question C
Can we identify seasonal patterns (Month-level trends) in Revenue_EUR and Units_Sold,
and do these patterns interact differently with regional economic indicators (GDP_Growth, Fuel_Price_Index)?

Answer:
Both Units_Sold and Revenue_EUR show a clear and recurring monthly seasonal pattern.

• Revenue_EUR and Units_Sold are relatively lower in January–February, April–May, July–August, and October–November
• Strong peaks are observed in March (~8966 units, ~574 million EUR), June (~8987 units, ~577 million EUR),
 September (~8581 units, ~550 million EUR) and December (~8749 units, ~565 million EUR)

This suggests a repeated three-month cycle, 
the third month of each cycle records higher Revenue_EUR and Units_Sold than the preceding two months.

Overall, Units_Sold and Revenue_EUR move very closely together across months, 
indicating that seasonal demand affects both sales volume and revenue in a consistent way.


Regional economic indicator: GDP_Growth
GDP_Growth is grouped into Low, Medium, and High levels using quantiles.

Seasonal patterns remain consistent across different GDP growth levels.

• Across all GDP_growth groups, peaks consistently occur in March, June, September, and December
 
This indicates that the overall seasonal structure is stable and not significantly altered by GDP growth.

However, the magnitude of these patterns varies with GDP levels:

• Under High GDP growth, both Units_Sold and Revenue_EUR are higher
• Under Low GDP growth, both Units_Sold and Revenue_EUR are lower
• Under Medium GDP growth, values fall in between, but still follow the same seasonal pattern
 
Therefore, seasonality does not change structurally with GDP growth, 
but stronger GDP growth amplifies overall demand, leading to higher Revenue_EUR, Units_Sold and peaks.

Regional economic indicator: Fuel_Price_Index
Fuel_Price_Index is grouped into Low, Medium, and High levels using quantiles.

Seasonal patterns remain consistent across different fuel price.

• Across all Fuel_Price_Index groups, peaks consistently occur in March, June, September, and December
 
This indicates that the overall seasonal structure is stable and not significantly altered by fuel price.

However, the magnitude of these patterns varies with fuel price levels:

• Under High fuel price, both Units_Sold and Revenue_EUR are higher
• Under Low fuel price, both Units_Sold and Revenue_EUR are lower
• Under Medium fuel price, values fall in between, but still follow the same seasonal pattern

Therefore, seasonality does not change structurally with fuel price, 
but stronger fuel price amplifies overall demand, leading to higher Revenue_EUR, Units_Sold and peaks.
"""
df = pd.read_csv("bmw_global_sales_2018_2025.csv")

# Aggregate by Month
monthly_trend = df.groupby('Month').agg({
    'Units_Sold': 'mean',
    'Revenue_EUR': 'mean'
})

monthly_trend['Revenue_m'] = monthly_trend['Revenue_EUR'] / 1e6
monthly_trend = monthly_trend.drop(columns=['Revenue_EUR'])

# Plot a line chart for better illustration
# Usage: uncomment plt.show() to display the plot when running locally
fig, ax1 = plt.subplots(figsize=(10, 6))
plt.xticks(range(1, 13))

# Units Sold
ax1.plot(monthly_trend.index, monthly_trend['Units_Sold'], color='blue', marker='o', label='Units Sold')
ax1.set_xlabel('Month')
ax1.set_ylabel('Units Sold', color='blue')

# Revenue
ax2 = ax1.twinx()
ax2.plot(monthly_trend.index, monthly_trend['Revenue_m'], color='red', marker='o', label='Revenue')
ax2.set_ylabel('Revenue (Million EUR)', color='red')

plt.title("Monthly Seasonality (Global)")
plt.grid()

# Regional economic indicator: GDP_Growth
# Split GDP_Growth into Low / Medium / High using quantiles
df['GDP_Group'] = pd.qcut(
    df['GDP_Growth'],
    q=3,
    labels=['Low', 'Medium', 'High']
)

# Aggregate monthly seasonality under different GDP levels
gdp_monthly_trend = df.groupby(['GDP_Group', 'Month']).agg({
    'Units_Sold': 'mean',
    'Revenue_EUR': 'mean'
})

# Convert revenue to millions
gdp_monthly_trend['Revenue_m'] = gdp_monthly_trend['Revenue_EUR'] / 1e6
gdp_monthly_trend = gdp_monthly_trend.drop(columns=['Revenue_EUR'])

# Regional economic indicator: Fuel_Price_Index
# Split Fuel_Price_Index into Low / Medium / High using quantiles
df['Fuel_Group'] = pd.qcut(
    df['Fuel_Price_Index'],
    q=3,
    labels=['Low', 'Medium', 'High']
)

# Aggregate monthly seasonality under different fuel prices
fuel_monthly_trend = df.groupby(['Fuel_Group', 'Month']).agg({
    'Units_Sold': 'mean',
    'Revenue_EUR': 'mean'
})

# Convert revenue to millions
fuel_monthly_trend['Revenue_m'] = fuel_monthly_trend['Revenue_EUR'] / 1e6
fuel_monthly_trend = fuel_monthly_trend.drop(columns=['Revenue_EUR'])

if __name__ == '__main__':
    print("Monthly Seasonality:")
    print(monthly_trend.round(3))

    # Uncomment the following line to display the plot when running locally
    # plt.show()

    print("\nSeasonality under GDP Growth")
    print(gdp_monthly_trend.round(3))

    print("\n Seasonality under Fuel Price")
    print(fuel_monthly_trend.round(3))
