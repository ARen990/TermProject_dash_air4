from pycaret.classification import *
import requests
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd

# Fetch data from Air4Thai API
station_id = "44t"
param = "PM25,PM10,O3,CO,NO2,SO2,WS,TEMP,RH,WD,BP,RAIN"
data_type = "hr"
start_date = "2023-12-01"
end_date = "2024-02-20"
start_time = "00"
end_time = "23"

url = f"http://air4thai.com/forweb/getHistoryData.php?stationID={station_id}&param={param}&type={data_type}&sdate={start_date}&edate={end_date}&stime={start_time}&etime={end_time}"
response = requests.get(url)
response_json = response.json()
data = pd.DataFrame.from_dict(response_json["stations"][0]["data"])

# Load your dataset containing PM25, PM10, O3, CO, NO2, SO2, WS, TEMP, RH, WD
data = pd.read_csv("air4thai_data.csv")

# Convert "DATETIMEDATA" to datetime format
data["DATETIMEDATA"] = pd.to_datetime(data["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
data.sort_values("DATETIMEDATA", inplace=True)

# Set the threshold for non-null values
threshold_percentage = 50
threshold = len(data) * (1 - threshold_percentage / 100)

# Drop columns with more than 50% NaN values
data.dropna(axis=1, thresh=threshold, inplace=True)

# Fill null values with the mean of each column
data.fillna(data.mean(), inplace=True)

# Handle zeros separately
columns_to_handle_zeros = ["Temperature", "Relative Humidity", "Atmospheric Pressure", "Wind Direction"]

for column in columns_to_handle_zeros:
    data.dropna(subset=columns_to_handle_zeros, inplace=True)
    data[column].replace(0, data[column].mean(), inplace=True)

# Create Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Air Quality Analytics: Understand Your Air"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🍃😎🍃", className="header-emoji"),
                html.H1(
                    children="Air Quality Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze air quality parameters"
                    " including ,DATETIMEDATA,PM25,PM10,O3,CO,NO2,SO2,Wind Speed,Temperature,Relative Humidity,Wind Direction,Atmospheric Pressure,RAIN",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Parameter", className="menu-title"),
                        dcc.Dropdown(
                            id="parameter-filter",
                            options=[
                                {"label": param, "value": param}
                                for param in data.columns[2:]  # Skip the 'DATETIMEDATA' column
                            ],
                            value="PM25",  # Set default parameter
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Date Range", className="menu-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["DATETIMEDATA"].min().date(),
                            max_date_allowed=data["DATETIMEDATA"].max().date(),
                            start_date=data["DATETIMEDATA"].min().date(),
                            end_date=data["DATETIMEDATA"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(
                            id="parameter-chart", config={"displayModeBar": False},
                        ),
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        dcc.Graph(
                            id="histogram-chart", config={"displayModeBar": False},
                        ),
                    ],
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

@app.callback(
    Output("parameter-chart", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_chart(parameter, start_date, end_date):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask, :]
    chart_figure = {
        "data": [
            {
                "x": filtered_data["DATETIMEDATA"],
                "y": filtered_data[parameter],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": f"{parameter} Levels", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#1F77B4"],
        },
    }
    return chart_figure

@app.callback(
    Output("histogram-chart", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_histogram(parameter, start_date, end_date):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask, :]
    histogram_figure = {
        "data": [
            {
                "x": filtered_data[parameter],
                "type": "histogram",
                "marker": {"color": "#1F77B4"},
            },
        ],
        "layout": {
            "title": {"text": f"{parameter} Histogram", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#1F77B4"],
        },
    }
    return histogram_figure

if __name__ == "__main__":
    app.run_server(debug=True)
