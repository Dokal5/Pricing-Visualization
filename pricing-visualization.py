
# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display

# Define the UI elements (sliders for min/max prices with range 1 to 500, and variable cost from 1 to 200)
min_price_slider = widgets.FloatSlider(value=80, min=1, max=500, step=1, description='Min Price (€):')
max_price_slider = widgets.FloatSlider(value=200, min=1, max=500, step=1, description='Max Price (€):')
fixed_cost_slider = widgets.FloatSlider(value=10000, min=0, max=50000, step=1000, description='Fixed Cost (€):')
variable_cost_slider = widgets.FloatSlider(value=50, min=1, max=200, step=1, description='Variable Cost (€):')
price_elasticity_slider = widgets.FloatSlider(value=1, min=0.1, max=2.0, step=0.1, description='Price Elasticity:')
specified_price_input = widgets.FloatText(value=150, description='Specified Price (€):')

# Function to enforce min/max price constraints
def update_min_price(*args):
    if min_price_slider.value > max_price_slider.value:
        min_price_slider.value = max_price_slider.value

def update_max_price(*args):
    if max_price_slider.value < min_price_slider.value:
        max_price_slider.value = min_price_slider.value

# Attach the validation functions to the sliders
min_price_slider.observe(update_min_price, names='value')
max_price_slider.observe(update_max_price, names='value')

# Function to calculate profit, gross margin, and display all results
def update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_price):
    # Price range to test (from variable cost to max price)
    prices = np.linspace(variable_cost, max_price, 100)
    
    # Demand curve with price elasticity affecting the slope
    max_sales_quantity = 1000  # Maximum sales at minimum price
    min_sales_quantity = 200  # Minimum sales at maximum price
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
    specified_profit = (specified_price * (max_sales_quantity + demand_slope * (specified_price - min_price))) - (fixed_cost + variable_cost * (max_sales_quantity + demand_slope * (specified_price - min_price)))

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
    right_prices = prices[prices >= specified_price]  # Filter prices to the right of the specified price
    right_sales_quantity = sales_quantity[prices >= specified_price]  # Corresponding sales quantities
    ax2.fill_between(right_prices, right_sales_quantity, color='orange', alpha=0.3, label='Shaded Triangle Area')

    # Create the hoverable text block near the specified price point (no transparency)
    hover_text = (f"At the specified price (€{specified_price:.2f}):\n"
                  f" - Gross Margin: {gross_margin:.2f}%\n"
                  f" - Price Acceptance Range Deviation: {price_deviation}")
    
    ax1.annotate(hover_text,
                 xy=(specified_price, specified_profit), 
                 xytext=(specified_price + 10, specified_profit + 5000),
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightyellow'),  # Fully opaque box
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.5"))

    # Title and labels
    fig.suptitle('Profit Curve and Demand Curve vs. Price')
    ax1.grid(True)
    
    # Move the legends further to the left, outside the plot and away from y-axis
    ax1.legend(loc='center left', bbox_to_anchor=(-0.5, 0.5), title="Profit Curve Legend")
    ax2.legend(loc='center left', bbox_to_anchor=(-0.5, 0.25), title="Demand Curve Legend")

    # Show the plots
    plt.show()

# Interactive display function
widgets.interactive(update_profit_curve, 
                    min_price=min_price_slider, 
                    max_price=max_price_slider, 
                    fixed_cost=fixed_cost_slider, 
                    variable_cost=variable_cost_slider, 
                    price_elasticity=price_elasticity_slider,
                    specified_price=specified_price_input)
