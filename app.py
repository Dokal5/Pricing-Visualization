# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Segment-Based Profit Curve and Demand Curve Analysis with Van Westendorp Method")
st.write(
    """
    Adjust the parameters below to see how they impact the profit and demand curves 
    for different market segments. This tool also incorporates the Van Westendorp 
    Price Sensitivity Meter to visualize the Point of Marginal Cheapness (PMC) 
    and the Point of Marginal Expensiveness (PME).
    """
)

# SECTION 1: Define Segments and Their Characteristics
st.header("1. Define Market Segments")
num_segments = st.slider('Number of Segments:', min_value=1, max_value=3, value=2)
segments = []

for i in range(num_segments):
    segment_name = st.text_input(f'Segment {i+1} Name', value=f'Segment {i+1}')
    population_size = st.number_input(f'Population Size for {segment_name}:', min_value=100, value=10000, step=500)
    penetration_rate = st.slider(f'Expected Market Penetration for {segment_name} (%):', min_value=1.0, max_value=100.0, value=10.0, step=0.1)
    price_elasticity = st.slider(f'Price Elasticity for {segment_name}:', min_value=0.1, max_value=3.0, value=1.0, step=0.1)
    
    # Calculate max sales quantity based on population size and penetration rate
    max_sales_quantity = int(population_size * (penetration_rate / 100))
    segments.append({
        'name': segment_name,
        'elasticity': price_elasticity,
        'max_quantity': max_sales_quantity,
        'population_size': population_size,
        'penetration_rate': penetration_rate
    })

# SECTION 2: Define Costs
st.header("2. Costs")
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)

# SECTION 3: Van Westendorp Price Sensitivity Analysis
st.header("3. Van Westendorp Price Sensitivity Analysis")
price_points = st.multiselect("Select Price Points (€):", options=[50, 70, 100, 130, 150], default=[50, 70, 100, 130, 150])
survey_data = {
    "Price (€)": price_points,
    "% Too Cheap": [st.slider(f"% Too Cheap at {price}€", min_value=0, max_value=100, value=100 - 2 * i) for i, price in enumerate(price_points)],
    "% Cheap": [st.slider(f"% Cheap at {price}€", min_value=0, max_value=100, value=80 - 2 * i) for i, price in enumerate(price_points)],
    "% Expensive": [st.slider(f"% Expensive at {price}€", min_value=0, max_value=100, value=20 + 2 * i) for i, price in enumerate(price_points)],
    "% Too Expensive": [st.slider(f"% Too Expensive at {price}€", min_value=0, max_value=100, value=5 + 5 * i) for i, price in enumerate(price_points)],
}

# Convert survey data to DataFrame
df_psm = pd.DataFrame(survey_data).sort_values(by="Price (€)")

# Plot the cumulative curves for Van Westendorp
fig_psm, ax_psm = plt.subplots(figsize=(10, 6))
ax_psm.plot(df_psm["Price (€)"], df_psm["% Too Cheap"], label="% Too Cheap", linestyle='--')
ax_psm.plot(df_psm["Price (€)"], df_psm["% Cheap"], label="% Cheap", linestyle='-')
ax_psm.plot(df_psm["Price (€)"], df_psm["% Expensive"], label="% Expensive", linestyle='-.')
ax_psm.plot(df_psm["Price (€)"], df_psm["% Too Expensive"], label="% Too Expensive", linestyle=':')

# Formatting for PSM plot
ax_psm.set_xlabel("Price (€)")
ax_psm.set_ylabel("Cumulative Percentage (%)")
ax_psm.set_title("Van Westendorp Price Sensitivity Curves")
ax_psm.grid(True)
ax_psm.legend(loc='best')

# Show PSM plot in Streamlit
st.pyplot(fig_psm)

# Calculate PMC and PME
try:
    pmc = df_psm[df_psm["% Too Cheap"] <= df_psm["% Expensive"]]["Price (€)"].max()
    pme = df_psm[df_psm["% Too Expensive"] >= df_psm["% Cheap"]]["Price (€)"].min()
    st.write(f"**Point of Marginal Cheapness (PMC):** €{pmc}")
    st.write(f"**Point of Marginal Expensiveness (PME):** €{pme}")
except Exception as e:
    st.write("Error calculating PMC and PME:", e)

# SECTION 4: Calculate and Visualize Demand and Profit Curves with PMC and PME
st.header("4. Segment-Based Demand and Profit Curves with PMC and PME")

# Function to calculate demand and profit for each segment
def calculate_demand_and_profit(segment, prices):
    # Use max quantity as a basis for demand curve
    demand_slope = (-segment['max_quantity']) / (max(prices) - min(prices)) * segment['elasticity']
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

# Highlight PMC and PME on the plot
ax1.axvline(x=pmc, color='orange', linestyle='--', label=f"PMC: €{pmc}")
ax1.axvline(x=pme, color='purple', linestyle='--', label=f"PME: €{pme}")

# Formatting the plot
ax1.set_xlabel('Price (€)')
ax1.set_ylabel('Quantity / Profit (€)')
ax1.set_title('Demand and Profit Curves for Different Segments with PMC and PME')
ax1.grid(True)
ax1.legend(loc='upper right')

# Show the plot in Streamlit
st.pyplot(fig)

# Display additional results for each segment
for segment in segments:
    st.write(f"### Analysis for {segment['name']}")
    st.write(f"**Population Size:** {segment['population_size']}")
    st.write(f"**Penetration Rate:** {segment['penetration_rate']}%")
    st.write(f"**Estimated Max Sales Quantity:** {segment['max_quantity']} units")
    sales_quantity, profit = calculate_demand_and_profit(segment, prices)
    optimal_price = prices[np.argmax(profit)]
    optimal_profit = np.max(profit)
    st.write(f"**Optimal Price:** €{optimal_price:.2f}")
    st.write(f"**Estimated Sales Quantity at Optimal Price:** {sales_quantity[np.argmax(profit)]:.2f} units")
    st.write(f"**Profit at Optimal Price:** €{optimal_profit:.2f}")

# Display combined analysis (if relevant)
if num_segments > 1:
    st.header("5. Combined Profitability Analysis (Not Directly Combined)")
    st.write("""
        Although combining profits directly is not always feasible due to different demand behaviors, 
        this analysis helps compare how different strategies impact each segment. 
        Focus on the segment with the best potential while keeping in mind the overall market positioning.
    """)