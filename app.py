# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Segment-Based Profit Curve and Demand Curve Analysis")
st.write(
    """
    Adjust the parameters below to see how they impact the profit and demand curves 
    for different market segments. This tool helps to analyze the optimal pricing points 
    for each segment based on their unique price sensitivity.
    """
)

# SECTION 1: Define Segments and Their Characteristics
st.header("1. Define Market Segments")
num_segments = st.slider('Number of Segments:', min_value=1, max_value=3, value=2)
segments = []

for i in range(num_segments):
    segment_name = st.text_input(f'Segment {i+1} Name', value=f'Segment {i+1}')
    price_elasticity = st.slider(f'Price Elasticity for {segment_name}:', min_value=0.1, max_value=3.0, value=1.0, step=0.1)
    max_sales_quantity = st.number_input(f'Max Sales Quantity for {segment_name} (units):', min_value=100, value=1000, step=100)
    min_sales_quantity = st.number_input(f'Min Sales Quantity for {segment_name} (units):', min_value=0, value=200, step=50)
    segments.append({
        'name': segment_name,
        'elasticity': price_elasticity,
        'max_quantity': max_sales_quantity,
        'min_quantity': min_sales_quantity
    })

# SECTION 2: Define Costs
st.header("2. Costs")
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)

# SECTION 3: Calculate and Visualize Demand and Profit Curves
st.header("3. Segment-Based Demand and Profit Curves")

# Function to calculate demand and profit for each segment
def calculate_demand_and_profit(segment, prices):
    demand_slope = (segment['min_quantity'] - segment['max_quantity']) / (max(prices) - min(prices)) * segment['elasticity']
    sales_quantity = segment['max_quantity'] + demand_slope * (prices - min(prices))
    sales_quantity = np.maximum(sales_quantity, 0)  # Ensure no negative demand
    
    # Calculate revenue, costs, and profit
    revenue = prices * sales_quantity
    total_variable_costs = variable_cost * sales_quantity
    profit = revenue - (total_variable_costs + fixed_cost)
    
    return sales_quantity, profit

# Prepare the plot
fig, ax1 = plt.subplots(figsize=(12, 8))

# Generate a range of prices
prices = np.linspace(50, 200, 100)  # Price range from €50 to €200

# Iterate over segments to plot their demand and profit curves
for segment in segments:
    sales_quantity, profit = calculate_demand_and_profit(segment, prices)
    
    # Plot demand curve
    ax1.plot(prices, sales_quantity, label=f"Demand for {segment['name']}", linestyle='--')
    
    # Calculate the optimal price and plot profit curve
    optimal_price = prices[np.argmax(profit)]
    optimal_profit = np.max(profit)
    ax1.plot(prices, profit, label=f"Profit for {segment['name']}", linestyle='-')
    ax1.scatter(optimal_price, optimal_profit, color='r', label=f"Optimal Price for {segment['name']}: €{optimal_price:.2f}")

# Formatting the plot
ax1.set_xlabel('Price (€)')
ax1.set_ylabel('Quantity / Profit (€)')
ax1.set_title('Demand and Profit Curves for Different Segments')
ax1.grid(True)
ax1.legend(loc='upper right')

# Show the plot in Streamlit
st.pyplot(fig)

# Display additional results for each segment
for segment in segments:
    st.write(f"### Analysis for {segment['name']}")
    sales_quantity, profit = calculate_demand_and_profit(segment, np.array([segment['min_quantity'], segment['max_quantity']]))
    optimal_price = prices[np.argmax(profit)]
    optimal_profit = np.max(profit)
    st.write(f"**Optimal Price:** €{optimal_price:.2f}")
    st.write(f"**Estimated Sales Quantity at Optimal Price:** {sales_quantity[np.argmax(profit)]:.2f} units")
    st.write(f"**Profit at Optimal Price:** €{optimal_profit:.2f}")

# Display combined analysis (if relevant)
if num_segments > 1:
    st.header("4. Combined Profitability Analysis (Not Directly Combined)")
    st.write("""
        Although combining profits directly is not always feasible due to different demand behaviors, 
        this analysis helps compare how different strategies impact each segment. 
        Focus on the segment with the best potential while keeping in mind the overall market positioning.
    """)