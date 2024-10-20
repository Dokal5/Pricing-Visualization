# Function to calculate profit, gross margin, and display results
def update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_prices):
    # Price range to test (from variable cost to max price)
    prices = np.linspace(variable_cost, max_price, 100)
    
    # Demand curve with price elasticity affecting the slope
    demand_slope = (min_sales_quantity - max_sales_quantity) / (max_price - min_price) * price_elasticity
    sales_quantity = max_sales_quantity + demand_slope * (prices - min_price)
    
    # Ensure sales quantity is not less than zero
    sales_quantity = np.maximum(sales_quantity, 0)

    # Calculating total revenue, total costs, and profit
    total_revenue = prices * sales_quantity
    total_costs = (variable_cost * sales_quantity) + fixed_cost
    profit = total_revenue - total_costs

    # Break-even analysis
    break_even_price = None
    break_even_quantity = None

    for price in prices:
        quantity = max_sales_quantity + demand_slope * (price - min_price)
        quantity = max(quantity, 0)  # Ensure quantity is not less than zero
        revenue = price * quantity
        costs = fixed_cost + (variable_cost * quantity)
        profit_at_price = revenue - costs
        if profit_at_price >= 0:
            break_even_price = price
            break_even_quantity = quantity
            break

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

    # Plot the break-even point if available
    if break_even_price is not None and break_even_quantity is not None:
        ax1.scatter(break_even_price, 0, color='orange', label=f'Break-even Price: €{break_even_price:.2f}')
        ax2.scatter(break_even_price, break_even_quantity, color='orange', label=f'Break-even Quantity: {break_even_quantity:.2f}')
        st.write(f"**Break-even Price:** €{break_even_price:.2f}")
        st.write(f"**Break-even Quantity:** {break_even_quantity:.2f} units")

    # Title and labels
    fig.suptitle('Profit Curve and Demand Curve vs. Price')
    ax1.grid(True)
    ax1.legend(loc='upper left', bbox_to_anchor=(0, -0.1), title="Profit Curve Legend")
    ax2.legend(loc='upper right', bbox_to_anchor=(1, -0.1), title="Demand Curve Legend")

    # Show the plots
    st.pyplot(fig)

    # Display additional results for each specified price
    for i, specified_price in enumerate(specified_prices):
        # Calculate sales quantity at each specified price
        sales_quantity_at_specified = max_sales_quantity + demand_slope * (specified_price - min_price)
        sales_quantity_at_specified = max(sales_quantity_at_specified, 0)  # Ensure it is not less than zero

        # Calculate profit at each specified price
        specified_profit = (
            specified_price * sales_quantity_at_specified
            - (fixed_cost + variable_cost * sales_quantity_at_specified)
        )
        
        # Display the results for each specified price
        st.write(f"**Specified Price {i+1}:** €{specified_price:.2f}")
        st.write(f"**Sales Quantity at Specified Price {i+1}:** {sales_quantity_at_specified:.2f} units")
        st.write(f"**Profit at Specified Price {i+1}:** €{specified_profit:.2f}")

# Call the function to update and display the profit curve with break-even analysis
update_profit_curve(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_prices)