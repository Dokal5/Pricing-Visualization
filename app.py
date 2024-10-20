# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Pricing and Price Sensitivity Analysis Tool")
st.write(
    """
    This tool helps analyze price sensitivity and survey data for pricing decisions.
    Input your survey details to calculate the margin of error, confidence intervals,
    and visualize demand and profit curves for different market segments.
    """
)

# SECTION 1: Define Market Segments
st.header("1. Define Market Segments")
num_segments = st.slider('Number of Segments:', min_value=1, max_value=3, value=2)
segments = []

for i in range(num_segments):
    segment_name = st.text_input(f'Segment {i+1} Name', value=f'Segment {i+1}')
    population_size = st.number_input(f'Population Size for {segment_name}:', min_value=1, value=10000, step=100)
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
st.header("2. Define Costs")
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)

# SECTION 3: Input PMC and PME from Van Westendorp Analysis
st.header("3. Input PMC and PME from Van Westendorp Analysis")
pmc = st.number_input('Point of Marginal Cheapness (PMC) (€):', min_value=0.0, value=70.0)
pme = st.number_input('Point of Marginal Expensiveness (PME) (€):', min_value=0.0, value=130.0)

# Input survey details for calculating margin of error and confidence interval
st.header("4. Survey Analysis for Margin of Error")
survey_population_size = st.number_input('Enter the Population Size for Survey:', min_value=1, value=10000, step=100)
survey_sample_size = st.number_input('Enter the Sample Size of the Survey:', min_value=1, value=300, step=10)

# Calculate proportion (p) as 0.5 for maximum variability
p = 0.5

# Calculate Z-score for 95% confidence (1.96)
z_score = 1.96

# Calculate the standard margin of error (without FPC)
margin_of_error = z_score * np.sqrt((p * (1 - p)) / survey_sample_size)

# Adjust for finite population if the sample is a significant part of the population
if survey_sample_size > 0 and survey_population_size > 0 and survey_sample_size < survey_population_size:
    fpc_factor = np.sqrt((survey_population_size - survey_sample_size) / (survey_population_size - 1))
    margin_of_error *= fpc_factor

# Calculate the confidence interval range for PMC and PME
confidence_interval_pmc = (pmc - margin_of_error * pmc, pmc + margin_of_error * pmc)
confidence_interval_pme = (pme - margin_of_error * pme, pme + margin_of_error * pme)

# Display the results for margin of error and confidence intervals
st.write(f"**Calculated Margin of Error:** ±{margin_of_error * 100:.2f}%")
st.write(f"**Confidence Interval for PMC:** ({confidence_interval_pmc[0]:.2f}€, {confidence_interval_pmc[1]:.2f}€)")
st.write(f"**Confidence Interval for PME:** ({confidence_interval_pme[0]:.2f}€, {confidence_interval_pme[1]:.2f}€)")

# SECTION 5: Calculate and Visualize Demand and Profit Curves with PMC and PME
st.header("5. Segment-Based Demand and Profit Curves with PMC and PME")

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
    st.header("6. Combined Profitability Analysis")
    st.write("""
        Although combining profits directly is not always feasible due to different demand behaviors, 
        this analysis helps compare how different strategies impact each segment. 
        Focus on the segment with the best potential while keeping in mind the overall market positioning.
    """)