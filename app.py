import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Interactive Profit Calculator"),

    html.Label("Min Price (€):"),
    dcc.Slider(id='min-price-slider', min=1, max=500, step=1, value=80, marks={i: str(i) for i in range(0, 501, 100)}),

    html.Label("Max Price (€):"),
    dcc.Slider(id='max-price-slider', min=1, max=500, step=1, value=200, marks={i: str(i) for i in range(0, 501, 100)}),

    html.Label("Fixed Cost (€):"),
    dcc.Slider(id='fixed-cost-slider', min=0, max=50000, step=1000, value=10000, marks={i: str(i) for i in range(0, 50001, 10000)}),

    html.Label("Variable Cost (€):"),
    dcc.Slider(id='variable-cost-slider', min=1, max=200, step=1, value=50, marks={i: str(i) for i in range(0, 201, 50)}),

    html.Label("Price Elasticity:"),
    dcc.Slider(id='price-elasticity-slider', min=0.1, max=2.0, step=0.1, value=1.0, marks={i/10: str(i/10) for i in range(1, 21, 2)}),

    html.Label("Specified Price (€):"),
    dcc.Input(id='specified-price-input', type='number', value=150),

    html.Div(id='output-container'),

    dcc.Graph(id='profit-curve-graph')
])

# Define the callback to update the graph and the metrics
@app.callback(
    [Output('profit-curve-graph', 'figure'),
     Output('output-container', 'children')],
    [Input('min-price-slider', 'value'),
     Input('max-price-slider', 'value'),
     Input('fixed-cost-slider', 'value'),
     Input('variable-cost-slider', 'value'),
     Input('price-elasticity-slider', 'value'),
     Input('specified-price-input', 'value')]
)
def update_graph(min_price, max_price, fixed_cost, variable_cost, price_elasticity, specified_price):
    # Calculate the profit curve
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

    # Calculate the optimal price (price with max profit)
    optimal_price = prices[np.argmax(profit)]
    optimal_profit = np.max(profit)

    # Filter prices to the right of the specified price for shading
    right_prices = prices[prices >= specified_price]
    right_sales_quantity = sales_quantity[prices >= specified_price]

    # Calculate gross margin at the specified price
    if specified_price > variable_cost:
        gross_margin = (specified_price - variable_cost) / specified_price * 100
    else:
        gross_margin = 0

    # Determine deviation from price acceptance range
    if specified_price < min_price:
        price_deviation = "Price is below the minimum acceptable price."
    elif specified_price > max_price:
        price_deviation = "Price is above the maximum acceptable price."
    else:
        price_deviation = "Price is within the acceptable range."

    # Create the profit curve figure with shaded area
    fig = go.Figure()

    # Plot the profit curve
    fig.add_trace(go.Scatter(x=prices, y=profit, mode='lines', name='Profit Curve', line=dict(color='blue')))
    
    # Plot the demand curve
    fig.add_trace(go.Scatter(x=prices, y=sales_quantity, mode='lines', name='Demand Curve', line=dict(color='green'), yaxis='y2'))

    # Shade the triangle area to the right of the specified price under the demand curve
    fig.add_trace(go.Scatter(x=right_prices, y=right_sales_quantity, fill='tozeroy', mode='none', fillcolor='rgba(255, 165, 0, 0.3)', name='Shaded Triangle Area'))

    # Add vertical lines for optimal price and specified price
    fig.add_trace(go.Scatter(x=[optimal_price], y=[optimal_profit], mode='markers', marker=dict(color='red', size=10), name=f'Optimal Price: €{optimal_price:.2f}'))
    fig.add_trace(go.Scatter(x=[specified_price], y=[0], mode='markers', marker=dict(color='magenta', size=10), name=f'Specified Price: €{specified_price:.2f}'))
    
    # Add annotations
    fig.add_annotation(x=specified_price, y=0, text=f"Specified Price: €{specified_price}\nGross Margin: {gross_margin:.2f}%\n{price_deviation}",
                       showarrow=True, arrowhead=2, ax=-50, ay=-40, bordercolor="black", borderwidth=1, borderpad=4, bgcolor="lightyellow")

    # Update layout with two y-axes
    fig.update_layout(
        title='Profit Curve and Demand Curve vs. Price',
        xaxis_title='Price (€)',
        yaxis=dict(title='Profit (€)', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
        yaxis2=dict(title='Sales Quantity', titlefont=dict(color='green'), tickfont=dict(color='green'), overlaying='y', side='right'),
        showlegend=True,
        legend=dict(x=-0.3, y=1, traceorder="normal", bgcolor="rgba(0,0,0,0)", bordercolor="Black", borderwidth=1)
    )

    output_text = f"At the specified price (€{specified_price:.2f}):\n" \
                  f" - Gross Margin: {gross_margin:.2f}%\n" \
                  f" - {price_deviation}"

    return fig, output_text

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
