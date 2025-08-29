import dash
import more_itertools  # kept to match the provided base
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv'
)

# Initialize the Dash app
app = dash.Dash(__name__)

# ---------------------------------------------------------------------------------
# Dropdown options & years (per note: 1980–2013)
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]
year_list = [i for i in range(1980, 2014, 1)]

# ---------------------------------------------------------------------------------
# Layout
app.layout = html.Div([
    # TASK 2.1: Title
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}
    ),

    # TASK 2.2: Report-type dropdown
    html.Div([
        html.Label("Select Report Type:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            placeholder='Select a report type',
            value='Yearly Statistics',
            style={'width': '80%', 'padding': '3px', 'fontSize': 20, 'textAlignLast': 'center'}
        )
    ], style={"marginBottom": "12px"}),

    # TASK 2.2: Year dropdown
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select year',
            value=2010,
            style={'width': '80%', 'padding': '3px', 'fontSize': 20, 'textAlignLast': 'center'}
        )
    ], style={"marginBottom": "12px"}),

    # TASK 2.3: Output division
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
    ])
])

# ---------------------------------------------------------------------------------
# TASK 2.4 — Callback 1: Enable/disable year dropdown based on report type
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False  # enabled
    else:
        return True   # disabled

# ---------------------------------------------------------------------------------
# TASK 2.4/2.5/2.6 — Callback 2: Update output container (return four plots per report)
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):

    # ---------------- TASK 2.5: Recession Period Statistics ----------------
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Plot 1 — Line: Average Automobile Sales fluctuation over Recession Period (year-wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x='Year',
                y='Automobile_Sales',
                labels={'Year': 'Year', 'Automobile_Sales': 'Average Automobile Sales'},
                title="Average Automobile Sales Fluctuation over Recession Period (Year-wise)"
            )
        )

        # Plot 2 — Bar: Average number of vehicles sold by vehicle type
        average_sales = (recession_data
                         .groupby('Vehicle_Type')['Automobile_Sales']
                         .mean()
                         .reset_index())
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                labels={'Vehicle_Type': 'Vehicle Type', 'Automobile_Sales': 'Average Automobile Sales'},
                title="Average Vehicles Sold by Vehicle Type (Recessions)"
            )
        )

        # Plot 3 — Pie: Total expenditure share by vehicle type during recessions
        exp_rec = (recession_data
                   .groupby('Vehicle_Type')['Advertising_Expenditure']
                   .sum()
                   .reset_index())
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title="Total Advertisement Expenditure Share by Vehicle Type (Recessions)"
            )
        )

        # Plot 4 — Bar: Effect of unemployment rate on vehicle type and sales
        unemp_data = (recession_data
                      .groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales']
                      .mean()
                      .reset_index())
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                title='Effect of Unemployment Rate on Vehicle Type and Sales (Recessions)'
            )
        )

        # Return 2x2 grid (two flex rows)
        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart1, style={'width': '50%'}),
                               html.Div(children=R_chart2, style={'width': '50%'})],
                     style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart3, style={'width': '50%'}),
                               html.Div(children=R_chart4, style={'width': '50%'})],
                     style={'display': 'flex', 'width': '100%'})
        ]

    # ---------------- TASK 2.6: Yearly Statistics ----------------
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        yearly_data = data[data['Year'] == input_year]

        # Plot 1 — Line: Yearly Automobile sales for the whole period (average per year)
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x='Year',
                y='Automobile_Sales',
                labels={'Year': 'Year', 'Automobile_Sales': 'Average Automobile Sales'},
                title='Yearly Average Automobile Sales (Entire Period)'
            )
        )

        # Plot 2 — Line: Total Monthly Automobile sales for selected year
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas,
                x='Month',
                y='Automobile_Sales',
                labels={'Month': 'Month', 'Automobile_Sales': 'Total Automobile Sales'},
                title=f'Total Monthly Automobile Sales — {input_year}'
            )
        )

        # Plot 3 — Bar: Average Vehicles Sold by Vehicle Type for selected year
        avr_vdata = (yearly_data
                     .groupby('Vehicle_Type')['Automobile_Sales']
                     .mean()
                     .reset_index())
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x='Vehicle_Type',
                y='Automobile_Sales',
                labels={'Vehicle_Type': 'Vehicle Type', 'Automobile_Sales': 'Average Automobile Sales'},
                title=f'Average Vehicles Sold by Vehicle Type — {input_year}'
            )
        )

        # Plot 4 — Pie: Total Advertisement Expenditure by Vehicle Type for selected year
        exp_data = (yearly_data
                    .groupby('Vehicle_Type')['Advertising_Expenditure']
                    .sum()
                    .reset_index())
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title='Total Advertisement Expenditure by Vehicle Type'
            )
        )

        # Return 2x2 grid (two flex rows)
        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart1, style={'width': '50%'}),
                               html.Div(children=Y_chart2, style={'width': '50%'})],
                     style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart3, style={'width': '50%'}),
                               html.Div(children=Y_chart4, style={'width': '50%'})],
                     style={'display': 'flex', 'width': '100%'})
        ]

    else:
        return None

# ---------------------------------------------------------------------------------
# Run the Dash app (Dash v3+)
if __name__ == '__main__':
    app.run(debug=True)