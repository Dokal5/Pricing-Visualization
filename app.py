# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Pricing and Price Sensitivity Analysis Tool")
st.write(
    """
    This tool helps analyze price sensitivity and survey data for pricing decisions.
    Input your market and survey details, competitor pricing, and visualize demand and 
    profit curves for a single market segment.
    """
)

# SECTION 1: Market Definition
st.header("1. Define Your Market")
segment_name = st.text_input('Segment Name', value='Main Segment')
population_size = st.number_input(f'Population Size for {segment_name}:', min_value=1, value=10000, step=100)

# SECTION 2: Define Costs
st.header("2. Define Costs")
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)

# SECTION 3: Input Van Westendorp PSM Data
st.header("3. Input PSM Survey Data")
survey_sample_size = st.number_input('Enter the Sample Size of the Survey:', min_value=1, value=300, step=10)
pmc = st.number_input('Point of Marginal Cheapness (PMC) (€):', min_value=0.0, value=70.0)
pme = st.number_input('Point of Marginal Expensiveness (PME) (€):', min_value=0.0, value=130.0)

# Calculate proportion (p) as 0.5 for maximum variability
p = 0.5

# Calculate Z-score for 95% confidence (1.96)
z_score = 1.96

# Calculate the standard margin of error (without FPC)
margin_of_error = z_score * np.sqrt((p * (1 - p)) / survey_sample_size)

# Adjust for finite population if the sample is a significant part of the population
if survey_sample_size > 0 and population_size > 0 and survey_sample_size < population_size:
    fpc_factor = np.sqrt((population_size - survey_sample_size) / (population_size - 1))
    margin_of_error *= fpc_factor

# Calculate the confidence interval range for PMC and PME
confidence_interval_pmc = (pmc - margin_of_error * pmc, pmc + margin_of_error * pmc)
confidence_interval_pme = (pme - margin_of_error * pme, pme + margin_of_error * pme)

# Display the results for margin of error and confidence intervals
st.write(f"**Calculated Margin of Error:** ±{margin_of_error * 100:.2f}%")
st.write(f"**Confidence Interval for PMC:** ({confidence_interval_pmc[0]:.2f}€, {confidence_interval_pmc[1]:.2f}€)")
st.write(f"**Confidence Interval for PME:** ({confidence_interval_pme[0]:.2f}€, {confidence_interval_pme[1]:.2f}€)")

# SECTION 4: Input Competitor Pricing
st.header("4. Input Competitors' Pricing")
num_competitors = st.slider('Number of Competitors:', min_value=0, max_value=5, value=2)
competitors = []

for i in range(num_competitors):
    brand = st.text_input(f'Competitor {i + 1} Brand', value=f'Brand {i + 1}')
    product_spec = st.text_input(f'Product Specification for {brand}', value=f'Spec {i + 1}')
    competitor_price = st.number_input(f'Price for {brand} ({product_spec}) (€):', min_value=0.0, value=100.0)
    competitors.append({
        'brand': brand,
        'spec': product_spec,
        'price': competitor_price
    })

# SECTION 5: Calculate and Visualize Demand and Profit Curves with PMC, PME, and Competitors
st.header("5. Demand and Profit Curves with PMC, PME, and Competitors")

# Function to calculate demand and profit for the segment
def calculate_demand_and_profit(prices):
    # Assume max sales quantity is based on a hypothetical penetration rate (e.g., 10%)
    max_sales_quantity = int(population_size * 0.1)
    demand_slope = (-max_sales_quantity) / (max(prices) - min(prices))
    sales_quantity = max_sales_quantity + demand_slope * (prices - min(prices))
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

# Calculate demand and profit for the segment
sales_quantity, profit = calculate_demand_and_profit(prices)

# Plot demand curve
ax1.plot(prices, sales_quantity, label=f"Demand for {segment_name}", linestyle='--')

# Calculate the optimal price and plot profit curve
optimal_price = prices[np.argmax(profit)]
optimal_profit = np.max(profit)
ax1.plot(prices, profit, label=f"Profit for {segment_name}", linestyle='-')
ax1.scatter(optimal_price, optimal_profit, color='r', label=f"Optimal Price: €{optimal_price:.2f}")

# Highlight PMC and PME on the plot
ax1.axvline(x=pmc, color='orange', linestyle='--', label=f"PMC: €{pmc}")
ax1.axvline(x=pme, color='purple', linestyle='--', label=f"PME: €{pme}")

# Draw shaded areas for the confidence intervals of PMC and PME
ax1.fill_betweenx([0, max(sales_quantity)], confidence_interval_pmc[0], confidence_interval_pmc[1], color='orange', alpha=0.2, label='Confidence Interval for PMC')
ax1.fill_betweenx([0, max(sales_quantity)], confidence_interval_pme[0], confidence_interval_pme[1], color='purple', alpha=0.2, label='Confidence Interval for PME')

# Plot competitor prices as points
for competitor in competitors:
    ax1.scatter(competitor['price'], 0, color='green', label=f"{competitor['brand']} ({competitor['spec']}): €{competitor['price']}", zorder=5)
    ax1.annotate(f"{competitor['brand']}\n{competitor['price']}€",
                 xy=(competitor['price'], 0), 
                 xytext=(competitor['price'], 100),
                 textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", color='green'),
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightyellow'))

# Formatting the plot
ax1.set_xlabel('Price (€)')
ax1.set_ylabel('Quantity / Profit (€)')
ax1.set_title(f'Demand and Profit Curves for {segment_name} with PMC, PME, and Competitors')
ax1.grid(True)
ax1.legend(loc='upper right')

# Show the plot in Streamlit
st.pyplot(fig)

# Display additional results for the segment
st.write(f"### Analysis for {segment_name}")
st.write(f"**Population Size:** {population_size}")
st.write(f"**Estimated Max Sales Quantity (10% Hypothetical Penetration):** {int(population_size * 0.1)} units")
st.write(f"**Optimal Price:** €{optimal_price:.2f}")
st.write(f"**Estimated Sales Quantity at Optimal Price:** {sales_quantity[np.argmax(profit)]:.2f} units")
st.write(f"**Profit at Optimal Price:** €{optimal_profit:.2f}")