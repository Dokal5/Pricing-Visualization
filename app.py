# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Profit Curve and Demand Curve Analysis with Market Size Dynamics")
st.write(
    """
    Adjust the parameters below to see how they impact the profit curve.
    The tool calculates potential profit based on demand, cost structure, 
    and specified price points, and displays the optimal pricing point.
    This version includes market size dynamics, allowing you to see how changes in the market 
    size over time influence demand and profitability.
    """
)

# Define UI elements using Streamlit
# User-defined estimates for market size (TAM) and penetration rate
initial_market_size = st.number_input('Initial Total Addressable Market (TAM):', min_value=1000, value=10000, step=500)
market_growth_rate = st.slider('Annual Market Growth Rate (%):', min_value=0.0, max_value=20.0, value=5.0, step=0.1)
years = st.slider('Number of Years for Market Growth Simulation:', min_value=1, max_value=10, value=3)

# Calculate projected market size over the selected number of years
market_sizes = [initial_market_size * (1 + market_growth_rate / 100) ** year for year in range(years)]
st.write(f"Projected Market Sizes over {years} years:", market_sizes)

# User-defined penetration rate
penetration_rate = st.slider('Expected Market Penetration Rate (%):', min_value=1.0, max_value=100.0, value=10.0, step=0.1)

# Calculate max sales quantities based on market size and penetration rate over time
max_sales_quantities = [int(size * (penetration_rate / 100)) for size in market_sizes]
min_sales_quantity = 200  # Set as a constant or adjust based on your model needs.

# Input sliders for price and costs
min_price = st.slider('Minimum Acceptable Price (€):', min_value=1, max_value=500, value=80, step=1)
max_price = st.slider('Maximum Acceptable Price (€):', min_value=1, max_value=500, value=200, step=1)
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)
price_elasticity = st.slider('Price Elasticity:', min_value=0.1, max_value=2.0, value=1.0, step=0.1)

# Ensure min_price and max_price are greater than the variable cost
if min_price < variable_cost:
    st.error(f"Minimum acceptable price must be at least equal to the variable cost (€{variable_cost}).")
    min_price = variable_cost

if max_price < variable_cost:
    st.error(f"Maximum acceptable price must be at least equal to the variable cost (€{variable_cost}).")
    max_price = variable_cost

# Let the user choose the number of specified price points
num_price_points = st.slider('Number of Specified Prices:', min_value=1, max_value=5, value=1)
specified_prices = []

# Create input fields for the specified price points with validation
for i in range(num_price_points):
    specified_price = st.number_input(
        f'Specified Price {i+1} (€):',
        min_value=variable_cost,  # Ensure specified price is at least equal to the variable cost
        value=max(variable_cost, 150 + i * 10)
    )
    specified_prices.append(specified_price)

# Function to calculate profit, gross margin, and display results
def update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_prices):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Loop through each year and plot the results
    for year, max_sales_quantity in enumerate(max_sales_quantities):
        # Price range to test (from variable cost to max price)
        prices = np.linspace(variable_cost, max_price, 100)
        
        # Demand curve with price elasticity affecting the slope
        demand_slope = (min_sales_quantity - max_sales_quantity) / (max_price - min_price) * price_elasticity
        sales_quantity = max_sales_quantity + demand_slope * (prices - min_price)

        # Calculating total revenue, total costs, and profit
        total_revenue = prices * sales_quantity
        total_costs = (variable_cost * sales_quantity) + fixed_cost
        profit = total_revenue - total_costs

        # Profit curve for each year
        ax1.plot(prices, profit, label=f'Year {year + 1} Profit Curve', linestyle='--', alpha=0.7)
        
        # Highlighting the optimal price point for each year
        optimal_price = prices[np.argmax(profit)]
        optimal_profit = np.max(profit)
        ax1.scatter(optimal_price, optimal_profit, label=f'Year {year + 1} Optimal Price: €{optimal_price:.2f}', zorder=5)

    # Basic plot setup
    ax1.axhline(0, color='black', linewidth=0.5)  # Zero profit line for reference
    ax1.set_xlabel('Price (€)')
    ax1.set_ylabel('Profit (€)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Demand curve on the same plot but different axis
    ax2 = ax1.twinx()
    ax2.plot(prices, sales_quantity, label='Demand Curve (Final Year)', color='g')
    ax2.set_ylabel('Sales Quantity', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Shading the price acceptance range (between min and max acceptable price) in light blue
    ax1.axvspan(min_price, max_price, color='lightblue', alpha=0.5, label='Price Acceptance Range')

    # Marking the variable cost on the x-axis with a bold dashed line
    ax1.axvline(x=variable_cost, color='k', linestyle='-', linewidth=2, label=f'Variable Cost: €{variable_cost}')

    # Iterate through specified prices and calculate corresponding profits
    for i, specified_price in enumerate(specified_prices):
        # Calculate sales quantity and profit at each specified price for the final year
        sales_quantity_at_specified = max_sales_quantities[-1] + demand_slope * (specified_price - min_price)
        specified_profit = (
            specified_price * sales_quantity_at_specified
            - (fixed_cost + variable_cost * sales_quantity_at_specified)
        )
        
        # Plot specified price points on the graph
        ax1.scatter(specified_price, specified_profit, color='magenta', zorder=5, label=f'Specified Price {i+1}: €{specified_price:.2f}')
        ax1.axvline(x=specified_price, color='magenta', linestyle='--', linewidth=2, label=f'Specified Price {i+1} Line: €{specified_price:.2f}')
        
    # Title and labels
    fig.suptitle('Profit Curve and Demand Curve vs. Price with Market Size Dynamics')
    ax1.grid(True)
    ax1.legend(loc='upper left', bbox_to_anchor=(0, -0.2), title="Profit Curve Legend")
    ax2.legend(loc='upper right', bbox_to_anchor=(1, -0.2), title="Demand Curve Legend")

    # Show the plots
    st.pyplot(fig)

    # Display additional results for each specified price
    for i, specified_price in enumerate(specified_prices):
        st.write(f"**Specified Price {i+1}:** €{specified_price:.2f}")
        st.write(f"**Sales Quantity at Specified Price {i+1} (Final Year):** {sales_quantity_at_specified:.2f} units")
        st.write(f"**Profit at Specified Price {i+1} (Final Year):** €{specified_profit:.2f}")

# Call the function to update and display the profit curve
update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_prices)