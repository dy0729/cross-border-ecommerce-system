import pandas as pd
import numpy as np
import datetime

# --- Configuration ---
start_date = "2022-01-01"
end_date = "2024-07-21"
products = {
    "Women's T-shirt": {"base_price": 15, "seasonality_strength": 0.5, "base_sales": 50},
    "Women's shorts": {"base_price": 25, "seasonality_strength": 1.5, "base_sales": 70},
    "Women's pants": {"base_price": 35, "seasonality_strength": -0.5, "base_sales": 60},
}

# --- Generate Date Range ---
dates = pd.to_datetime(pd.date_range(start=start_date, end=end_date, freq='D'))
df = pd.DataFrame({'order_date': dates})

# --- Generate Sales Data ---
all_orders = []

for index, row in df.iterrows():
    current_date = row['order_date']
    day_of_year = current_date.dayofyear
    year_fraction = day_of_year / 365.25
    
    # Introduce a general upward trend over the years
    trend = 1 + (current_date - pd.to_datetime(start_date)).days / (365 * 3) * 0.5 # 50% growth over 3 years

    for product_name, props in products.items():
        # Seasonal fluctuation (using a sine wave)
        # T-shirts/shorts peak in summer, pants peak in winter
        seasonality = 1 + props['seasonality_strength'] * np.sin(2 * np.pi * (year_fraction - 0.25))

        # Base daily sales with some randomness
        base_quantity = props['base_sales']
        random_factor = np.random.uniform(0.8, 1.2)
        
        # Calculate final quantity
        quantity_sold = int(base_quantity * seasonality * trend * random_factor)
        
        # Ensure non-negative sales
        if quantity_sold > 0:
            # Add some randomness to the price
            price = round(props['base_price'] * np.random.uniform(0.95, 1.05), 2)
            
            all_orders.append({
                'order_date': current_date,
                'product_name': product_name,
                'category': 'Women\'s Apparel',
                'quantity': quantity_sold,
                'price': price,
                'total_revenue': round(quantity_sold * price, 2)
            })

# --- Create DataFrame and Save ---
customer_orders_df = pd.DataFrame(all_orders)

# Save the generated data to a CSV file
output_filename = 'data/customer_orders.csv'
customer_orders_df.to_csv(output_filename, index=False)

print(f"Generated {len(customer_orders_df)} customer orders.")
print(f"Saved data to '{output_filename}'")
print(customer_orders_df.head())
