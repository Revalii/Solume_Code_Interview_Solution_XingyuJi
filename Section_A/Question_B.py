import pandas as pd

"""
Question B
Which models demonstrate the highest price elasticity, based on changes in Avg_Price_EUR vs Units_Sold, 
and how does this vary across economic conditions (GDP_Growth levels)?

Answer:
i4 (~-0.75) shows the strongest negative correlation among all models, indicating the highest price elasticity.
Followed by MINI (-0.55) and X5 (-0.48), which also demonstrate high price sensitivity.

This analysis uses correlation as a proxy for price elasticity in an exploratory context.

Price elasticity varies significantly across different GDP growth conditions:

 - Under Low GDP growth, several models such as i4 (~-0.996) and X3 (~-0.998) show strong negative correlations, 
 indicating very high price sensitivity as consumers become more price-conscious.
 - Under Medium GDP growth, elasticity remains strong for some models (e.g., X7 (-1.00), i4 (-0.83)), 
 but becomes more mixed across models.
 - Under High GDP growth, correlations become extreme (±1.00) due to limited observations, 
but generally indicate weaker or less reliable price sensitivity patterns.

Overall, price elasticity tends to be stronger and more consistent under lower GDP growth conditions, 
while under higher GDP growth, demand becomes less predictably sensitive to price changes.
"""
df = pd.read_csv("bmw_global_sales_2018_2025.csv")

# Aggregate to yearly region level (remove monthly noise)
df_year_model = df.groupby(['Year', 'Model']).agg({
    'Avg_Price_EUR': 'mean',
    'Units_Sold': 'sum',
    'GDP_Growth': 'mean'
}).reset_index()

# Price elasticity (correlation between price and units sold)
model_elasticity = df_year_model.groupby('Model').apply(
    lambda x: x[['Avg_Price_EUR', 'Units_Sold']].corr().iloc[0, 1]
).to_frame(name='price_units_corr')

# Rank models by elasticity (most negative = highest elasticity)
model_elasticity = model_elasticity.sort_values('price_units_corr')

# Split GDP into economic conditions
df_year_model['GDP_Group'] = pd.qcut(
    df_year_model['GDP_Growth'],
    q=3,
    labels=['Low', 'Medium', 'High']
)

# Elasticity under different GDP conditions
elasticity_by_gdp = df_year_model.groupby(['GDP_Group', 'Model']).apply(
    lambda x: x[['Avg_Price_EUR', 'Units_Sold']].corr().iloc[0, 1]
).to_frame(name='price_units_corr')

# Sort within each GDP group
elasticity_by_gdp = elasticity_by_gdp.sort_index(level=0)

if __name__ == '__main__':
    print("Models ranked by price elasticity:")
    print(model_elasticity.round(3))
    print("\nPrice elasticity by model under different GDP growth conditions:")
    print(elasticity_by_gdp.round(3))
