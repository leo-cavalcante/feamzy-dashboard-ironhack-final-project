import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# card_main = dbc.Card([
#     dbc.CardImg(src="images/feamzy-logo.png", top=True, bottom=False, alt="Feamzy Logo")
# ])

classes = pd.read_csv("data_clean/ClassStats.csv")

region_options = []
for region in sorted(list(classes.libelle_region.unique())):
    region_options.append({'label': str(region),'value': region})


app.layout = html.Div(children=[
    dbc.CardImg(src="/images/feamzy-log.png", top=True),
    html.H1(['Feamzy Dashboard'], style={'textAlign': 'center'}),
    html.Br(),
    html.H2('Users KPIs',style={'marginLeft': 10}),
    html.Br(),
    html.H2('Classes KPIs',style={'marginLeft': 10}),
    dbc.Row(
        [dbc.Col(html.Div(children=[classes.id.nunique()],
                 style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'})),
        dbc.Col(html.Div(children=[(classes["nbChild"].sum()/classes.shape[0]).round(2)],
                 style={'marginTop': 25, 'fontSize': 50, 'color': '#4e98f5','textAlign': 'center'}))
        ]),
    dbc.Row(
        [dbc.Col(html.Div(children=["Schools"], style={'marginBottom': 25,'textAlign': 'center'})),
         dbc.Col(html.Div(children=["Average Children per Class"], style={'marginBottom': 25,'textAlign': 'center'}))
         ]),
    dcc.Dropdown(id='regions_picker', options=region_options, value=sorted(list(classes.libelle_region.unique())), multi=True,style={'marginLeft': 20,'marginRight': 20}),
    dcc.Graph(id="classes_map"),
    html.Br(),
    html.H2('Notifications KPIs',style={'marginLeft': 10}),
    html.Br(),
    html.Div(),
])

@app.callback(Output('classes_map', 'figure'),
                 [Input('regions_picker', 'value')])
def update_map(selected_regions):
    with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
        france = json.load(response)

    classes_filtered = classes[classes.libelle_region.isin(selected_regions)]


    fig = go.Figure(px.scatter_mapbox(classes_filtered, lat="coordinatesLat", lon="coordinatesLong", text="appellation_officielle",
                    size="nbChild", color_continuous_scale="Viridis", range_color=(0, 12)))

    #fig.update_layout(title_text="Classes per Region")

    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_text = 'Classes per Region',
        mapbox=go.layout.Mapbox(style="carto-positron",
                               zoom=4.5, center_lat=47, center_lon=3,
                               layers=[{
                                   'sourcetype': 'geojson',
                                   'source': france,
                                   'type': 'line',
                                   'color': '#A9A9A9',
                                   'below': "True",
                               }]
                               ))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)