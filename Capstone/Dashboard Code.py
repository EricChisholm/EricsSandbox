# Import required libraries
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create the Dash app
app = Dash(__name__)

# ---------------------------
# Layout (TASKS 1–3 + chart placeholders)
# ---------------------------
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Success pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    # TASK 3: Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ---------------------------
# Callbacks
# ---------------------------

# TASK 2: Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Success counts by site (class == 1)
        df_success = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df_success,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Success vs Failure for selected site
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        fig = px.pie(
            outcome_counts,
            values='count',
            names='class',
            title=f'Total Launch Outcomes for {entered_site} (Success vs Failure)'
        )
        return fig

# TASK 4: Scatter chart callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df = spacex_df[mask].copy()

    title = 'Correlation between Payload and Success for all Sites'
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for {selected_site}'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=title
    )
    return fig

# ---------------------------
# Run the app
# ---------------------------
if __name__ == '__main__':
    app.run()

