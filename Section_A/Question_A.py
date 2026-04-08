import pandas as pd

"""
Question A
How does BEV_Share growth over time (2018–2025) correlate with Units_Sold and Revenue_EUR across different regions,
and which region shows the strongest transition toward electrification?

Answer:
BEV_Share shows a strong positive correlation with both Units_Sold and Revenue_EUR across all regions.

 - USA (~0.98) and China (~0.95) exhibit the strongest correlations
 - Europe (~0.81–0.84) shows a slightly weaker correlation
 - Rest of World (~0.79) demonstrates the weakest correlation
 
In terms of growth, all regions experienced a very similar increase in BEV_Share (≈0.173–0.174) from 2018 to 2025, 
indicating a globally consistent electrification trend. However, since growth differences are minimal, 
the strongest transition should be evaluated based on overall impact rather than magnitude alone.

While BEV adoption is increasing globally, Europe shows the strongest transition toward electrification, 
as it combines steady growth with strong and consistent links to both sales and revenue.
"""
df = pd.read_csv("bmw_global_sales_2018_2025.csv")

# Aggregate to yearly region level (remove monthly noise)
df_year_region = df.groupby(['Year', 'Region']).agg({
    'BEV_Share': 'mean',
    'Units_Sold': 'sum',
    'Revenue_EUR': 'sum'
}).reset_index()

# Compute correlation across different regions
corr_results = df_year_region.groupby('Region').apply(
    lambda x: x[['BEV_Share', 'Units_Sold', 'Revenue_EUR']].corr()
)

# Reorder regions
region_order = ['China', 'Europe', 'USA', 'RestOfWorld']
corr_results = corr_results.reindex(region_order, level=0)

# Sort for growth calculation
df_sorted = df_year_region.sort_values(['Region', 'Year'])

# BEV adoption growth (2018 → 2025)
bev_growth = df_sorted.groupby('Region')['BEV_Share'].agg(
    start=lambda x: x.iloc[0],
    end=lambda x: x.iloc[-1]
)

# Compute absolute growth
bev_growth['growth'] = bev_growth['end'] - bev_growth['start']

# Rank regions by electrification transition strength
bev_growth = bev_growth.sort_values('growth', ascending=False)

if __name__ == '__main__':
    print("Correlation between BEV_Share and Units_Sold, Revenue_EUR across different regions:")
    # print(corr_results)
    print(corr_results.round(4))
    print("\nBEV_Share growth from 2018 to 2025 across different regions:")
    # print(bev_growth)
    print(bev_growth.round(4))
