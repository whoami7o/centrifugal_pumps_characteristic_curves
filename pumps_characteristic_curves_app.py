import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import plotly.graph_objects as go  # or plotly.express as px


with open('esp_db.json', encoding='utf8') as file:
    pumps_info = json.load(file)
    file.close()


def plot_graph(pump_id='58', freq=50):
    fig = go.Figure()
    # head line
    fig.add_trace(go.Scatter(
        x=pumps_info[pump_id]['rate_points'],
        y=pumps_info[pump_id]['head_points'],
        name="напор, ном част",
        line={'shape': 'spline', 'color': "#1f77b4", 'smoothing': 0.75}  # "dash": 'dot'
    ))
    fig.add_trace(go.Scatter(
        x=[i * (freq / pumps_info[pump_id]['freq_Hz']) for i in pumps_info[pump_id]['rate_points']],
        y=[i * (freq / pumps_info[pump_id]['freq_Hz']) ** 2 for i in pumps_info[pump_id]['head_points']],
        name="напор, заданая част",
        line={'shape': 'spline', 'color': "#1f77b4", 'smoothing': 0.75, "dash": 'longdash'},
        opacity=0.75
    ))

    # power line
    fig.add_trace(go.Scatter(
        x=pumps_info[pump_id]['rate_points'],
        y=pumps_info[pump_id]['power_points'],
        name="мощность, ном част",
        yaxis="y2",
        line={'shape': 'spline', 'color': "#ff7f0e", 'smoothing': 0.75}
    ))
    fig.add_trace(go.Scatter(
        x=[i * (freq / pumps_info[pump_id]['freq_Hz']) for i in pumps_info[pump_id]['rate_points']],
        y=[i * (freq / pumps_info[pump_id]['freq_Hz']) ** 3 for i in pumps_info[pump_id]['power_points']],
        name="мощность, заданая част",
        yaxis="y2",
        line={'shape': 'spline', 'color': "#ff7f0e", 'smoothing': 0.75, "dash": 'longdash'},
        opacity=0.75
    ))

    # eff line
    fig.add_trace(go.Scatter(
        x=pumps_info[pump_id]['rate_points'],
        y=pumps_info[pump_id]['eff_points'],
        name="кпд, ном частота",
        yaxis="y3",
        line={'shape': 'spline', 'color': "#d62728", 'smoothing': 0.75}
    ))
    fig.add_trace(go.Scatter(
        x=[i * (freq / pumps_info[pump_id]['freq_Hz']) for i in pumps_info[pump_id]['rate_points']],
        y=pumps_info[pump_id]['eff_points'],
        name="кпд, заданая част",
        yaxis="y3",
        line={'shape': 'spline', 'color': "#d62728", 'smoothing': 0.75, "dash": 'longdash'},
        opacity=0.75
    ))

    # nominal borders
    fig.add_trace(go.Scatter(
        x=[pumps_info[pump_id]['rate_nom_sm3day'], pumps_info[pump_id]['rate_nom_sm3day']],
        y=[0, 1000],
        name="ном расход",
        line={'shape': 'spline', 'color': "black", 'smoothing': 0.75, "dash": 'dot'},  # "dash": 'dot'
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=[pumps_info[pump_id]['rate_opt_min_sm3day'], pumps_info[pump_id]['rate_opt_min_sm3day']],
        y=[0, 1000],
        name="опт мин расход",
        line={'shape': 'spline', 'color': "green", 'smoothing': 0.75, "dash": 'dot'},  # "dash": 'dot'
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=[pumps_info[pump_id]['rate_opt_max_sm3day'], pumps_info[pump_id]['rate_opt_max_sm3day']],
        y=[0, 1000],
        name="опт макс расход",
        line={'shape': 'spline', 'color': "green", 'smoothing': 0.75, "dash": 'dot'},  # "dash": 'dot'
        opacity=0.5,
        fill='tonexty',
        fillcolor='rgba(0, 128, 0, 0.03)'
    ))

    # Create axis objects
    fig.update_layout(
        xaxis=dict(
            title='Подача, см3/сут',
            domain=[0, 0.85],
            range=[min(pumps_info[pump_id]['rate_points']), max(pumps_info[pump_id]['rate_points'])],
            rangemode='nonnegative',
            dtick=200
        ),
        yaxis=dict(
            title="Напор, м",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            ),
            range=[0, 1.01 * max(pumps_info[pump_id]['head_points'])],
            rangemode='nonnegative',
            dtick=1
        ),
        yaxis2=dict(
            title="Мощность, кВт",
            titlefont=dict(
                color="#ff7f0e"
            ),
            tickfont=dict(
                color="#ff7f0e"
            ),
            range=[0, 4 * max(pumps_info[pump_id]['power_points'])],
            rangemode='nonnegative',
            anchor="x",
            overlaying="y",
            side="right",
            showgrid=False,
            dtick=1
        ),
        yaxis3=dict(
            title="КПД, %",
            titlefont=dict(
                color="#d62728"
            ),
            tickfont=dict(
                color="#d62728"
            ),
            range=[0, 1],
            rangemode='nonnegative',
            anchor="free",
            overlaying="y",
            side="right",
            position=0.9,
            showgrid=False,
            dtick=0.1
        )
    )
    title_msg = f"Марка насоса : {pumps_info[pump_id]['name']} | " \
                f"Производитель : {pumps_info[pump_id]['manufacturer']} | " \
                f"Ном. частота : {pumps_info[pump_id]['freq_Hz']}, Гц"

    # Update layout properties
    fig.update_layout(
        title_text=title_msg,
        width=1400,
        height=700
    )
    return fig

# dropdown


app = dash.Dash(__name__)

app.layout = html.Div(
    id='parent',
    children=[
        html.H1(
            id='H1',
            children="Напорно-расходная характеристика УЭЦН",
            style={'textAlign': 'center'},
        ),
        html.Label('Выбор насоса'),
        html.Div([
            dcc.Dropdown(
                id='dropdown',
                options=[{'label': pumps_info[i]['name'], 'value' : i} for i in pumps_info],
                value='58'
            ),
        ],
            style={"width": "20%"}
        ),
        html.Label('Выбор частоты'),
        html.Div([
            dcc.Slider(
                id='freq_slider',
                min=0,
                max=100,
                step=0.1,
                marks={value : f'{value}, Гц' for value in range(0, 100, 10)},
                value=50,
                tooltip={"placement": "top", "always_visible": True}
            ),
        ],
            style={"width": "40%"}
        ),
        dcc.Graph(
            id='line_graph',
            figure=plot_graph()
        )
    ]
)


@app.callback(Output(component_id='line_graph', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value'),
               Input(component_id='freq_slider', component_property= 'value')])
def line_graph_update_pump(dropdown_value, freq_slide_value):
    return plot_graph(pump_id=dropdown_value, freq=freq_slide_value)


if __name__ == '__main__':
    app.run_server(debug=True)  # , use_reloader=False # Turn off reloader if inside Jupyter
