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
    and specified price, and displays the optimal pricing point.
    """
)

# Define UI elements using Streamlit
# User-defined estimates for market size (TAM) and penetration rate
market_size = st.number_input('Total Addressable Market (TAM):', min_value=1000, value=10000, step=500)
penetration_rate = st.slider('Expected Market Penetration Rate (%):', min_value=1.0, max_value=100.0, value=10.0, step=0.1)

# Calculate max sales quantity based on market size and penetration rate
max_sales_quantity = int(market_size * (penetration_rate / 100))
min_sales_quantity = st.slider('Min Sales Quantity at Max Price:', min_value=100, max_value=max_sales_quantity, value=200, step=50)

# Other input sliders for price and costs
min_price = st.slider('Min Price (€):', min_value=1, max_value=500, value=80, step=1)
max_price = st.slider('Max Price (€):', min_value=1, max_value=500, value=200, step=1)
fixed_cost = st.slider('Fixed Cost (€):', min_value=0, max_value=50000, value=10000, step=1000)
variable_cost = st.slider('Variable Cost (€):', min_value=1, max_value=200, value=50, step=1)
price_elasticity = st.slider('Price Elasticity:', min_value=0.1, max_value=2.0, value=1.0, step=0.1)
specified_price = st.number_input('Specified Price (€):', value=150)

# Function to calculate profit, gross margin, and display results
def update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_price):
    # Price range to test (from variable cost to max price)
    prices = np.linspace(variable_cost, max_price, 100)
    
    # Demand curve with price elasticity affecting the slope
    demand_slope = (min_sales_quantity - max_sales_quantity) / (max_price - min_price) * price_elasticity
    sales_quantity = max_sales_quantity + demand_slope * (prices - min_price)

    # Calculating total revenue, total costs, and profit
    total_revenue = prices * sales_quantity
    total_costs = (variable_cost * sales_quantity) + fixed_cost
    profit = total_revenue - total_costs

    # Calculating gross margin at the specified price
    if specified_price > variable_cost:
        gross_margin = (specified_price - variable_cost) / specified_price * 100
    else:
        gross_margin = 0

    # Determine deviation from price acceptance range
    if specified_price < min_price:
        price_deviation = f"Price is below the minimum acceptable price."
    elif specified_price > max_price:
        price_deviation = f"Price is above the maximum acceptable price."
    else:
        price_deviation = f"Price is within the acceptable range."

    # Calculate profit at the specified price
    specified_profit = (
        specified_price * (max_sales_quantity + demand_slope * (specified_price - min_price))
        - (fixed_cost + variable_cost * (max_sales_quantity + demand_slope * (specified_price - min_price)))
    )

    # Plotting the profit curve and demand curve
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

    # Mark the specified price on the graph
    ax1.scatter(specified_price, specified_profit, color='magenta', zorder=5, label=f'Specified Price: €{specified_price:.2f}')

    # Create vertical lines for the optimal price and specified price
    ax1.axvline(x=optimal_price, color='red', linestyle='--', linewidth=2, label=f'Optimal Price Line: €{optimal_price:.2f}')
    ax1.axvline(x=specified_price, color='magenta', linestyle='--', linewidth=2, label=f'Specified Price Line: €{specified_price:.2f}')

    # Shade the area to the right of the specified price and under the demand curve
    right_prices = prices[prices >= specified_price]
    right_sales_quantity = sales_quantity[prices >= specified_price]
    ax2.fill_between(right_prices, right_sales_quantity, color='orange', alpha=0.3, label='Shaded Triangle Area')

    # Add a text box for the specified price details
    hover_text = (f"At the specified price (€{specified_price:.2f}):\n"
                  f" - Gross Margin: {gross_margin:.2f}%\n"
                  f" - Price Acceptance Range Deviation: {price_deviation}")

    ax1.annotate(hover_text,
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

    # Display additional results
    st.write(f"**Optimal Price:** €{optimal_price:.2f}")
    st.write(f"**Optimal Profit:** €{optimal_profit:.2f}")
    st.write(f"**Specified Price Profit:** €{specified_profit:.2f}")
    st.write(f"**Gross Margin at Specified Price:** {gross_margin:.2f}%")
    st.write(f"**Price Deviation Message:** {price_deviation}")

# Call the function to update and display the profit curve
update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_price)
