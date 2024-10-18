# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Profit Curve and Demand Curve Analysis")
st.write(
    """
    Adjust the parameters below to see how they impact the profit curve.
    The tool calculates potential profit based on demand, cost structure, 
    and specified price points, and displays the optimal pricing point.
    """
)

# Define UI elements using Streamlit
# User-defined estimates for market size (TAM) and penetration rate
market_size = st.number_input('Total Addressable Market (TAM):', min_value=1000, value=10000, step=500)
penetration_rate = st.slider('Expected Market Penetration Rate (%):', min_value=1.0, max_value=100.0, value=10.0, step=0.1)

# Calculate max sales quantity based on market size and penetration rate
max_sales_quantity = int(market_size * (penetration_rate / 100))
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
    # Price range to test (from variable cost to max price)
    prices = np.linspace(variable_cost, max_price, 100)
    
    # Demand curve with price elasticity affecting the slope
    demand_slope = (min_sales_quantity - max_sales_quantity) / (max_price - min_price) * price_elasticity
    sales_quantity = max_sales_quantity + demand_slope * (prices - min_price)

    # Calculating total revenue, total costs, and profit
    total_revenue = prices * sales_quantity
    total_costs = (variable_cost * sales_quantity) + fixed_cost
    profit = total_revenue - total_costs

    # Prepare the plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Profit curve
    ax1.plot(prices, profit, label='Profit Curve', color='b')
    ax1.axhline(0, color='black', linewidth=0.5)  # Zero profit line for reference
    ax1.set_xlabel('Price (€)')
    ax1.set_ylabel('Profit (€)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Highlighting the optimal price point
    optimal_price = prices[np.argmax(profit)]
    optimal_profit = np.max(profit)
    ax1.scatter(optimal_price, optimal_profit, color='r', label=f'Optimal Price: €{optimal_price:.2f}')

    # Demand curve on the same plot but different axis
    ax2 = ax1.twinx()
    ax2.plot(prices, sales_quantity, label='Demand Curve', color='g')
    ax2.set_ylabel('Sales Quantity', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Shading the price acceptance range (between min and max acceptable price) in light blue
    ax1.axvspan(min_price, max_price, color='lightblue', alpha=0.5, label='Price Acceptance Range')

    # Marking the variable cost on the x-axis with a bold dashed line
    ax1.axvline(x=variable_cost, color='k', linestyle='-', linewidth=2, label=f'Variable Cost: €{variable_cost}')

    # Iterate through specified prices and calculate corresponding profits
    for i, specified_price in enumerate(specified_prices):
        # Calculate sales quantity and profit at each specified price
        sales_quantity_at_specified = max_sales_quantity + demand_slope * (specified_price - min_price)
        specified_profit = (
            specified_price * sales_quantity_at_specified
            - (fixed_cost + variable_cost * sales_quantity_at_specified)
        )
        
        # Plot specified price points on the graph
        ax1.scatter(specified_price, specified_profit, color='magenta', zorder=5, label=f'Specified Price {i+1}: €{specified_price:.2f}')
        ax1.axvline(x=specified_price, color='magenta', linestyle='--', linewidth=2, label=f'Specified Price {i+1} Line: €{specified_price:.2f}')
        
        # Shade the area to the right of the specified price and under the demand curve
        right_prices = prices[prices >= specified_price]
        right_sales_quantity = sales_quantity[prices >= specified_price]
        ax2.fill_between(right_prices, right_sales_quantity, color='orange', alpha=0.3, label=f'Shaded Area for Price {i+1}' if i == 0 else "")

    # Add hover text for specified prices
    for i, specified_price in enumerate(specified_prices):
        ax1.annotate(f"Price {i+1}: €{specified_price}\nProfit: €{specified_profit:.2f}",
                     xy=(specified_price, specified_profit), 
                     xytext=(specified_price + 10, specified_profit + 5000),
                     bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightyellow'),
                     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.5"))

    # Title and labels
    fig.suptitle('Profit Curve and Demand Curve vs. Price')
    ax1.grid(True)
    ax1.legend(loc='upper left', bbox_to_anchor=(0, -0.1), title="Profit Curve Legend")
    ax2.legend(loc='upper right', bbox_to_anchor=(1, -0.1), title="Demand Curve Legend")

    # Show the plots
    st.pyplot(fig)

    # Display additional results for each specified price
    for i, specified_price in enumerate(specified_prices):
        st.write(f"**Specified Price {i+1}:** €{specified_price:.2f}")
        st.write(f"**Sales Quantity at Specified Price {i+1}:** {sales_quantity_at_specified:.2f} units")
        st.write(f"**Profit at Specified Price {i+1}:** €{specified_profit:.2f}")

# Call the function to update and display the profit curve
update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_prices)
