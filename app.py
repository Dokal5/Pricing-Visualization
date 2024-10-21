# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit title and description
st.title("Pricing and PSM Price Sensitivity Analysis Tool")
st.write(
    """
    This tool helps analyze price sensitivity and survey data for pricing decisions.
    Input your market and survey details, competitor pricing, and visualize demand and 
    profit curves for a single market segment. You can also input a price to see the break-even quantity.
    """
)

# SECTION 1: Market Definition
st.header("1. Define Your Market")
segment_name = st.text_input('Segment Name', value='Main Segment')
population_size = st.number_input(f'Population Size for {segment_name}:', min_value=1, value=10000, step=100)

# SECTION 2: Define Costs
st.header("2. Define Costs")
variable_cost = st.slider('Variable Cost per Product/Service (€):', min_value=1, max_value=200, value=50, step=1)
fixed_cost = st.number_input('Fixed Cost (€):', min_value=0, value=0, step=1000)

# SECTION 3: Input Van Westendorp PSM Data
st.header("3. Input PSM Survey Data")
survey_sample_size = st.number_input('Enter the Sample Size of the Survey:', min_value=1, value=300, step=10)
pmc = st.number_input('Point of Marginal Cheapness (PMC) (€):', min_value=0.0, value=70.0)
pme = st.number_input('Point of Marginal Expensiveness (PME) (€):', min_value=0.0, value=130.0)

# Display explanation of PSM using an expander
with st.expander("What is the Price Sensitivity Meter (PSM)?"):
    st.write(
        """
        The Van Westendorp Price Sensitivity Meter (PSM) is a technique for determining the 
        acceptable price range for a product or service based on consumer perceptions. It involves 
        asking respondents four key questions:
        
        1. **At what price would you consider the product to be too expensive to consider?** (Too expensive)
        2. **At what price would you consider the product to be too cheap, so that you would question its quality?** (Too cheap)
        3. **At what price would you consider the product to be a bargain—a great buy for the money?** (Cheap)
        4. **At what price would you consider the product to be getting expensive, but still worth considering?** (Expensive)
        
        From the responses, two key points are derived:
        
        - **Point of Marginal Cheapness (PMC)**: The price where the proportion of respondents who consider the product "too cheap" equals the proportion who consider it "cheap."
        - **Point of Marginal Expensiveness (PME)**: The price where the proportion of respondents who consider the product "too expensive" equals the proportion who consider it "expensive."
        
        These points help identify the acceptable price range and guide pricing decisions.
        """
    )

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

# Display the margin of error and provide a collapsible explanation
st.write(f"**Calculated Margin of Error:** ±{margin_of_error * 100:.2f}%")

# Use an expander to show the explanation when the user clicks on it
with st.expander("How is the Margin of Error calculated?"):
    st.write(
        r"""
        The Calculated Margin of Error (MoE) is essential in pricing decisions because it quantifies 
        the uncertainty in survey results, providing a range within which the true values 
        (like PMC and PME) are likely to fall. It helps businesses understand the reliability of 
        their estimates, especially when making data-driven pricing decisions.
        """
    )
    st.latex(r"\text{MoE} = Z \times \sqrt{\frac{p \times (1 - p)}{n}}")
    st.write(
        r"""
        Where:
        - \( Z \): Z-score corresponding to the confidence level (1.96 for 95% confidence level).
        - \( p \): Proportion estimate, set to 0.5 for maximum variability.
        - \( n \): Sample size.
        """
    )
    st.latex(r"\text{FPC} = \sqrt{\frac{N - n}{N - 1}}")
    st.latex(r"\text{MoE (adjusted)} = \text{MoE} \times \text{FPC}")
    st.write(
        r"""
        If the sample size (\( n \)) is a significant proportion of the population size (\( N \)), 
        the finite population correction (FPC) is applied to adjust the margin of error.
        """
    )

# Display the results for confidence intervals
st.write(f"**Confidence Interval for PMC:** ({confidence_interval_pmc[0]:.2f}€, {confidence_interval_pmc[1]:.2f}€)")
st.write(f"**Confidence Interval for PME:** ({confidence_interval_pme[0]:.2f}€, {confidence_interval_pme[1]:.2f}€)")

# SECTION 4: Input Competitor Pricing for Benchmarking
st.header("4. Input Competitors' Pricing for Benchmarking")

# Default competitors' data from the sneaker market
default_competitors = [
    {'brand': 'Nike', 'spec': 'Air Max 270, Casual Running Shoe', 'price': 140},
    {'brand': 'Adidas', 'spec': 'Ultraboost 21, High-performance Running Shoe', 'price': 180},
    {'brand': 'Puma', 'spec': 'RS-X3, Retro-style Training Sneaker', 'price': 120},
    {'brand': 'New Balance', 'spec': '990v5, Classic Athletic Shoe', 'price': 175},
    {'brand': 'Converse', 'spec': 'Chuck Taylor All Star, High-top Casual Sneaker', 'price': 90}
]

num_competitors = st.slider('Number of Competitors:', min_value=0, max_value=len(default_competitors), value=len(default_competitors))
competitors = []

for i in range(num_competitors):
    competitor = default_competitors[i]
    brand = st.text_input(f'Competitor {i + 1} Brand', value=competitor['brand'])
    product_spec = st.text_input(f'Product Specification for {brand}', value=competitor['spec'])
    competitor_price = st.number_input(f'Price for {brand} ({product_spec}) (€):', min_value=0.0, value=float(competitor['price']))
    competitors.append({
        'brand': brand,
        'spec': product_spec,
        'price': competitor_price
    })
    
# SECTION 5: User-Determined Price and Break-Even Analysis
st.header("5. Set Your Price and Calculate Break-Even Quantity")
user_price = st.number_input('Enter Your Price Setting (€):', min_value=0.0, value=100.0)

# Calculate break-even quantity: fixed costs divided by contribution margin (price - variable cost)
if user_price > variable_cost:
    break_even_quantity = fixed_cost / (user_price - variable_cost)
    st.write(f"**Break-Even Quantity at €{user_price:.2f}:** {break_even_quantity:.2f} units")
else:
    st.write("The price must be greater than the variable cost to calculate the break-even point.")

# Use an expander to show the explanation for Break-Even Quantity
with st.expander("How is the Break-Even Quantity calculated?"):
    st.latex(r"\text{Break-Even Quantity} = \frac{\text{Fixed Costs}}{\text{Price} - \text{Variable Cost}}")
    st.write(
        """
        The break-even quantity tells you the number of units you need to sell at a given price
        to cover all fixed and variable costs.
        
        - **Fixed Costs**: Costs that do not change with the number of units produced or sold (e.g., rent, salaries).
        - **Price**: The selling price per unit.
        - **Variable Cost**: The cost associated with producing one additional unit.
        
        The formula divides the total fixed costs by the contribution margin (Price - Variable Cost).
        """
    )

# SECTION 6: Calculate and Visualize Demand and Profit Curves with PMC, PME, and Competitors
st.header("6. Demand and Profit Curves with PMC, PME, and Competitors")

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
ax1.plot(prices, profit, label=f"Profit for {segment_name}", linestyle='-')
ax1.axvline(x=optimal_price, color='red', linestyle='-', linewidth=1.5, label=f"Optimal Price: €{optimal_price:.2f}")

# Highlight PMC and PME on the plot
ax1.axvline(x=pmc, color='orange', linestyle='--', label=f"PMC: €{pmc}")
ax1.axvline(x=pme, color='purple', linestyle='--', label=f"PME: €{pme}")

# Draw shaded areas for the confidence intervals of PMC and PME, extending vertically across the entire plot
ax1.fill_betweenx([0, max(sales_quantity) * 2], confidence_interval_pmc[0], confidence_interval_pmc[1], color='orange', alpha=0.2, label='Confidence Interval for PMC')
ax1.fill_betweenx([0, max(sales_quantity) * 2], confidence_interval_pme[0], confidence_interval_pme[1], color='purple', alpha=0.2, label='Confidence Interval for PME')

# Plot competitor prices as points
for idx, competitor in enumerate(competitors):
    y_offset = -50 * (idx + 1)  # Adjust y position to avoid overlap
    ax1.scatter(competitor['price'], y_offset, color='green', label=f"{competitor['brand']} ({competitor['spec']}): €{competitor['price']}", zorder=5)
    ax1.annotate(f"{competitor['brand']}\n{competitor['price']}€",
                 xy=(competitor['price'], y_offset), 
                 xytext=(competitor['price'], y_offset - 30),
                 textcoords='data',
                 arrowprops=dict(arrowstyle="->", color='green'),
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightyellow'))

# Highlight user-determined price and display break-even information
if user_price > variable_cost:
    ax1.axvline(x=user_price, color='blue', linestyle='--', linewidth=1.5, label=f"Your Price: €{user_price:.2f}")
    ax1.scatter(user_price, break_even_quantity, color='blue', zorder=5)
    ax1.annotate(f"Break-Even Qty:\n{break_even_quantity:.2f} units",
                 xy=(user_price, break_even_quantity), 
                 xytext=(user_price + 5, break_even_quantity + max(sales_quantity) * 0.1),
                 textcoords='data',
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor='blue', facecolor='lightyellow'),
                 arrowprops=dict(arrowstyle="->", color='blue'))

# Formatting the plot
ax1.set_xlabel('Price (€)')
ax1.set_ylabel('Quantity / Profit (€)')
ax1.set_title(f'Demand and Profit Curves for {segment_name} with PMC, PME, and Competitors')
ax1.grid(True)
ax1.legend(loc='upper right')

# Show the plot in Streamlit
st.pyplot(fig)

# Display additional questions for user reflection
st.header("Reflection on Your Price Setting")
if np.max(profit) < 0:
    st.error("### It is not possible to break even with the current pricing and cost structure.")
if user_price > variable_cost:
    st.write(f"Based on the chosen price point (€{user_price:.2f}), the required break-even quantity is {break_even_quantity:.2f} units.")
    
    # Display the strategic tip if break-even quantity is high compared to the population size
    if break_even_quantity > 0.2 * population_size:
        with st.expander("Tip: Strategies for Reaching Break-Even Point"):
            st.write(
                """
                If your break-even quantity is high compared to your target market size, achieving profitability 
                may be challenging. Consider the following strategies to improve your situation:
                
                1. **Expand Your Market**: Look for ways to reach a larger audience. This could involve 
                   exploring new geographical markets, diversifying your product range, or increasing marketing efforts.
                
                2. **Reduce Fixed Costs**: Reevaluate your operational expenses and explore opportunities to 
                   cut down costs. This could include negotiating with suppliers, reducing rent, or outsourcing non-core functions.
                
                3. **Combine Strategies**: A balanced approach, where you both expand your market reach and 
                   optimize your fixed costs, can often yield the best results.
                
                These adjustments can help make your pricing strategy more sustainable and achieve the break-even point faster.
                """
            )
    st.write("**1. Based on the defined price point, can you develop pricing bundles or tier pricing that can facilitate better value capturing?**")
    st.write("**2. What is your promotion/communication and place/channel strategy that can fulfill this minimum sales target?**")