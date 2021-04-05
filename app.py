import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
import dash_auth
#from time import sleep

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np

from urllib.request import urlopen
import json
from datetime import datetime as dt
import random
from collections import Counter

#from cleaning_functions import *

# Function to detect the most closest dates chosen from the filter.
# Sometimes there's no activity in the date chosen by the user, therefore this function will be able to bypass that
# by returning the closest precise date within the period given by the user
def dataset_with_correct_dates(df, column, start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    df.dropna(axis=0, inplace=True)
    df[column] = pd.to_datetime(df[column]).dt.date

    df = df.sort_values(column, ignore_index=True)
    dff = df.set_index(column)
    dff = dff[~dff.index.duplicated(keep='first')]

    start_index = dff.index.get_loc(start_date, method='bfill')
    start_date = dff.reset_index().iloc[start_index][column]

    end_index = dff.index.get_loc(end_date, method='ffill')
    end_date = dff.reset_index().iloc[end_index][column]

    df = df.loc[(df[column] >= start_date) & (df[column] <= end_date)]

    return df

# Cleaning the databases present in the folder "data"
# run_once = 0
# while 1:
#     if run_once == 0:
#         clean_all_databases()
#         run_once = 1

# Sleeping to have sometime to charge the clean databases
# sleep(2)

# Charging all databases
classes = pd.read_csv("data_clean/ClassStats.csv")
users = pd.read_csv("data_clean/User.csv")
homeworks = pd.read_csv("data_clean/HomeworkRequest.csv")
documents = pd.read_csv("data_clean/Document.csv")
notifications = pd.read_csv("data_clean/Notification.csv")
events = pd.read_csv("data_clean/Event.csv")

# Saving the words that should not appear in the wordclouds
stopwords = []
with open('stopwords.txt', 'r') as file:
    # reading each line
    for line in file:
        # reading each word
        for word in line.split():
            # displaying the words
            stopwords.append(word)


# Creating variables necessary for filters
region_options = []
for region in sorted(list(classes.libelle_region.unique())):
    region_options.append({'label': str(region),'value': region})

events_types = []
for event_type in sorted(list(events.eventType.fillna("NOT ASSIGNED").unique())):
    events_types.append({'label': str(event_type),'value': event_type})

notifications_group = []
for notif in sorted(list(notifications.Group.fillna("NOT ASSIGNED").unique())):
    notifications_group.append({'label': str(notif),'value': notif})

# Determining the recency of the databases
last_update = max(users.creationDate.max(), classes.creationDate.max(), homeworks.creationDate.max(),
                  documents.creationDate.max(), notifications.creationDate.max(), events.creationDate.max())

# Creating the application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# Setting up the authentification
auth = dash_auth.BasicAuth(app, [['Username','Password'],['feamzy_adm', 'ironhack']])

# Creating cards that will compose grids in the layout of the application
card_users_key_metrics = dbc.Card([
     dbc.CardBody(
         [
             html.H3('Key Metrics',style={'marginLeft': 4,'color': '#f8e71c', 'textShadow': '2px 2px black'}),
             html.Div(children=[users.id.count()], style={'fontSize': 50,'color': 'white','textAlign': 'center'}), #'marginTop': 25,
             html.H4(['Total Users'], style={'color': 'white','textAlign': 'center'}),
             html.Br(),
             html.Div(children=[users.groupChildSize.sum()], style={'fontSize': 50,'color': 'white','textAlign': 'center'}), #'marginTop': 25,
             html.H4(['Children Profiles Created'], style={'color': 'white','textAlign': 'center'}),
             html.Br(),
             html.Br(),
             dcc.Graph(id="children_number"),
             html.Br(),
             html.P(children=["PS.: the 'y' axis is in logarithm scale"], style={'fontSize': 10,'color': 'white','textAlign': 'right','font-style': 'italic',})
         ]
     )
 ],color='#4e99f6',inverse=True,style={"border": "none"})

card_users_evolution = dbc.Card([
     dbc.CardBody(
         [
             dcc.Graph(id='users-evolution'),
             html.Br(),
             dcc.DatePickerRange(id="selected-dates-users", calendar_orientation='horizontal', day_size=20,
                                         end_date_placeholder_text="End date", with_portal=False, first_day_of_week=0, reopen_calendar_on_clear=True, is_RTL=False,
                                         clearable=True, number_of_months_shown=3, min_date_allowed=dt(2020, 1, 1),max_date_allowed=pd.to_datetime("today").date(),
                                         initial_visible_month=dt(2021, 1, 1), start_date=dt(2020, 8, 1).date(), end_date=pd.to_datetime("today").date(),
                                         display_format="DD-MMMM-YYYY", minimum_nights=6,
                                         persistence=True, persisted_props=["start_date"], persistence_type="session",
                                         updatemode="singledate"
                                         )
         ]
     )
 ],color='#4e99f6',inverse=True,style={"border": "none"})

card_users_inactive = dbc.Card([
     dbc.CardBody(
         [
             dash_table.DataTable(id='inactive-users',
                                  style_cell={"TextAlign": "left", },
                                  style_header={'backgroundColor': '#4e99f6', 'color': 'white', 'fontWeight': 'bold',
                                                'border': '1px solid black'},
                                  style_data_conditional=[
                                      {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248,248,248)'}], page_size=5,
                                  style_table={'width': '100px', 'height': '200px', },
                                  style_as_list_view=True,
                                  export_format="csv",
                                  )
         ]
     )
 ],color='#4e99f6',inverse=True,style={"border": "none"})

card_classes_key_metrics_1 = dbc.Card([
     dbc.CardBody([
            dbc.Row([dbc.CardImg(src="https://img.icons8.com/bubbles/2x/classroom.png", alt="Classroom icon",
                                        style={'maxWidth': '25%', 'maxHeight': '25%', 'textAlign': 'center','width': 200}),
                     dbc.Col([html.H4(id='unique-classes', style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Classes", html.Br(),"Created"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})], align="end"
                              ),
                     dbc.Col([html.H4(id='classes-without-children', children=[],style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Classes without Children assigned"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})],align="end")
                    ], align="center"),
         ])
 ],inverse=True, outline=False,style={'boxShadow':'4px 4px lightgrey'})

card_classes_key_metrics_2 = dbc.Card([
     dbc.CardBody([
         dbc.Row([dbc.CardImg(
                 src="data:image/png;base64,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",
                 alt="School icon", style={'maxWidth': '25%', 'maxHeight': '25%', 'textAlign': 'center'}),

                      dbc.Col([html.H4(id='unique-schools', style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Unique", html.Br(),"Schools"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})], align="end"
                              ),
                      dbc.Col([html.H4(id='schools-without-children', children=[],style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Schools without Children assigned"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})],
                              align="end")
                      ], align="center"),
         ])
 ],inverse=True, outline=False,style={'boxShadow':'4px 4px lightgrey'})

card_classes_key_metrics_3 = dbc.Card([
     dbc.CardBody(
         [
             dbc.Row([dbc.CardImg(src="https://img.icons8.com/clouds/2x/child-safe-zone.png", alt="Kids icon", className='align-self-center', style={'maxWidth': '25%', 'maxHeight': '25%'}),
                      dbc.Col([html.H4(children=[(classes["nbChild"].sum())], style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                                html.H6(children=["Children assigned to Classes"], style={'marginBottom': 25, 'color': 'grey', 'textAlign': 'center'})]),
                      dbc.Col([html.H4(children=[classes["nbArchivedChildren"].sum()], style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Archived", html.Br(),"Children"], style={'marginBottom': 25, 'color': 'grey', 'textAlign': 'center'})]),
                      ], align="center"),
         ]
     )
 ],inverse=True,outline=False,style={'boxShadow':'4px 4px lightgrey'})

card_classes_map = dbc.Card([dbc.CardBody([dcc.Graph(id="classes_map")])],inverse=True, outline=False,style={"border": "none"})

card_classes_pie_chart = dbc.Card([dbc.CardBody([dcc.Graph(id='public-prive')])],inverse=True,style={"border": "none"})

card_homeworks_key_metrics_1 = dbc.Card([
    dbc.CardBody([
    dbc.Row([dbc.Col(html.Div(children=[homeworks.id.nunique()], style={'fontSize': 50,'color': '#4e99f6','textAlign': 'center'})),], style={'height': 60}, align="end"),
    dbc.Row([dbc.Col(html.Div(children=["Homeworks Created"], style={'marginBottom': 25, 'textAlign': 'center'})),], style={'height': 20}, align="start"),
    ])
],color='#F8F4F4',style={"border": "none"})

card_homeworks_key_metrics_2 = dbc.Card([
    dbc.CardBody([
    dbc.Row([dbc.Col(html.Div(children=[homeworks.classId.nunique()], style={'fontSize': 50,'color': '#4e99f6','textAlign': 'center'})),], style={'height': 60}, align="end"),
    dbc.Row([dbc.Col(html.Div(children=["Classes having Homeworks assigned"], style={'marginBottom': 25, 'textAlign': 'center'})),], style={'height': 20}, align="start"),
    ])
],color='#F8F4F4',style={"border": "none"})

card_homeworks_key_metrics_3 = dbc.Card([
    dbc.CardBody([
    dbc.Row([dbc.Col(html.Div(children=[homeworks.userId.nunique()], style={'fontSize': 50,'color': '#4e99f6','textAlign': 'center'})),], style={'height': 60}, align="end"),
    dbc.Row([dbc.Col(html.Div(children=["Unique Authors having created Homeworks"], style={'marginBottom': 25, 'textAlign': 'center'})),], style={'height': 20}, align="start"),
    ])
],color='#F8F4F4',style={"border": "none"})

card_homeworks_visualisations_1 = dbc.Card([dbc.CardBody([dcc.Graph(id="homeworks-type")])],color='#F8F4F4',style={"border": "none"})

card_homeworks_visualisations_2 = dbc.Card([dbc.CardBody([
    dash_table.DataTable(id='homeworks-authors',
                         style_cell={"TextAlign" : "left",},
                         style_header={'backgroundColor':'#4e99f6', 'color': 'white', 'fontWeight': 'bold', 'border':'1px solid black'},
                         style_data_conditional=[{'if':{'row_index':'odd'},  'backgroundColor':'rgb(248,248,248)'}], page_size=5,
                         style_table={'width':'600px','height':'200px',},
                         style_as_list_view=True,
                         export_format="csv",
                         )
            ]
    )],color='#F8F4F4',style={"border": "none"})

card_events_key_metrics_1 = dbc.Card([
     dbc.CardBody([
            dbc.Row([
                     dbc.Col([html.H4(id='events-past',style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Events Passed"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})],align="end")
                    ], align="center"),
         ])
 ],inverse=True, outline=False, style={'boxShadow':'-4px -4px lightgrey'})

card_events_key_metrics_2 = dbc.Card([
     dbc.CardBody([
            dbc.Row([
                     dbc.Col([html.H4(id='events-future', style={'marginTop': 25, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Upcoming Events"],style={'marginBottom': 25, 'textAlign': 'center', 'color': 'grey'})],align="end")
                    ], align="center"),
         ])
 ],inverse=True, outline=False,style={'boxShadow':'4px 4px lightgrey'})

card_events_key_metrics_3 = dbc.Card([
     dbc.CardBody([
            dcc.Graph(id='events-slots'),
            html.P(children=["PS.: the 'y' axis is in logarithm scale"], style={'fontSize': 10,'color': 'grey','textAlign': 'right','font-style': 'italic',})
         ])
 ],inverse=True, outline=False,style={"border": "none"})

card_events_given_period_1 = dbc.Card([
     dbc.CardBody([
            dbc.Row([
                     dbc.Col([html.H4(id='events-in-this-period',style={'marginTop': 70, 'fontSize': 50, 'color': '#4e99f6','textAlign': 'center'}),
                               html.H6(children=["Events in this period (of selected types)"],style={'marginBottom': 70, 'textAlign': 'center', 'color': 'grey'})],align="end")
                    ], align="center"),
            ])
    ],inverse=True, outline=False,style={"border": "none"})

card_events_given_period_2 = dbc.Card([dbc.CardBody([dbc.Row([dcc.Graph(id='events-dayofweek')], align="center"),])
                                        ],inverse=True, outline=False,style={"border": "none", 'marginLeft': 50, "width": "50rem", 'textAlign':"center"})


card_events_key_metrics_filter = dbc.Card([
     dbc.CardBody([
            dbc.Row([
                     dcc.Dropdown(id='events-types-key-metrics', options=events_types, value=sorted(list(events.eventType.fillna("NOT ASSIGNED").unique())), multi=True)
                    ], align="center"),
         ])
 ],inverse=True, outline=False,style={'width':'50%'})#style={'boxShadow':'4px 4px lightgrey'})

# Creating layout for the app with content, format and style
app.layout = html.Div(children=[
    dbc.Row([dbc.Col(html.Img(src="/static/feamzy-logo-bluebcg.png", alt="Feamzy logo", style={'maxWidth': '50%', 'maxHeight': '50%'}),width=4,align="center"),
            dbc.Col(html.H1(['Dashboard'], style={'color': 'white', 'offset':3,'marginLeft': 150, 'textShadow': '2px 2px black'}),width=4),
            dbc.Col(html.H6(['Last update: ',last_update], style={'color': 'white', 'offset':4,'marginLeft': 150, 'textShadow': '2px 2px black'}),width=4,align="center"),
            ], style={'backgroundColor':'#4e99f6','position':'sticky', 'top':'0','zIndex': 10, 'border':'1px grey solid','height': '60px'}),
    html.Div([
        html.Br(),
        html.H2('USERS', style={'color':'white','marginLeft': 20, 'textShadow': '2px 2px black'}),#,'bgcolor':'#800000'style={'backgroundColor':'blue'}
        dbc.Row([dbc.Col(card_users_key_metrics,width=5), dbc.Col(card_users_evolution, width=7)]),
        #dbc.Row([dbc.Col(card_users_inactive)]),
        html.Br(),
        ],   style={'backgroundColor':'#4e99f6'}),
    html.Br(),
    html.Br(),
    html.Div([
        html.H2('CLASSES & SCHOOLS',style={'marginLeft': 10,'color': '#4e99f6', 'textShadow': '2px 2px black'}),
        html.Br(),
        html.H3('Key Metrics',style={'marginLeft': 10,'color': '#f8e71c', 'textShadow': '2px 2px black'}),
        dbc.CardColumns([card_classes_key_metrics_1, card_classes_key_metrics_2, card_classes_key_metrics_3]),
        html.Br(),
        dbc.Row([dbc.Col(card_classes_map, width=9),
                 dbc.Col(card_classes_pie_chart,width=3)],align='center'),
        ],   style={'marginLeft': 10,'marginRight': 10, 'backgroundColor':'white'}),
        dbc.Row([dcc.Dropdown(id='regions_picker', options=region_options, value=sorted(list(classes.libelle_region.unique())), multi=True,)# style={'marginLeft': 40,'marginRight': 40})
                ],align='center', style={'marginLeft': 40,'marginRight': 40}),
    html.Br(),
    html.Br(),
    html.Div([html.Br(),
            html.Br(),
            html.H2('HOMEWORKS', style={'marginLeft': 10, 'marginRight': 10,'color': '#4e99f6', 'textShadow': '2px 2px black'}),
            html.Br(),
            html.H3('Key Metrics',style={'marginLeft': 10,'color': '#f8e71c', 'textShadow': '2px 2px black'}),
            dbc.CardGroup([card_homeworks_key_metrics_1, card_homeworks_key_metrics_2, card_homeworks_key_metrics_3]),
            html.Br(),
            dbc.CardDeck([card_homeworks_visualisations_1, card_homeworks_visualisations_2]),
            html.Br(),
              ],   style={'backgroundColor':'#F8F4F4'}),
    html.Div([html.Br(),
        html.H2('DOCUMENTS', style={'marginLeft': 10, 'marginRight': 10,'color': '#4e99f6', 'textShadow': '2px 2px black'}),
        html.Br(),
        html.H3('Key Metrics',style={'marginLeft': 10,'color': '#f8e71c', 'textShadow': '2px 2px black'}),
        dbc.Row(
            [dbc.Col(html.Div(children=["Documents Created"], style={'marginBottom': 25, 'color': 'black','textAlign': 'center'}), width=3),
             dbc.Col(html.Div(), width=6),
             ], style={'height': 10, 'marginLeft': 10}, align="end"),
        dbc.Row(
            [dbc.Col(html.Div(children=[documents.id.nunique()], style={'marginTop': 25, 'fontSize': 50,'color': '#4e99f6','textAlign': 'center'}),width=3),
             dbc.Col(html.Div(dcc.Graph(id='documents_type')),width=6),
             ], style={'height': 350, 'marginLeft': 10}, align="start")
        ],   style={'backgroundColor':'lightgrey'}),
    html.Br(),
    html.Br(),
    html.H2('EVENTS', style={'marginLeft': 10,'color': '##4e99f6', 'border':'1px red', 'textShadow': '2px 2px black'}),
    html.Br(),
    html.Div([
            dbc.Row([html.H3('Key Metrics',style={'marginLeft': 50,'color': '#f8e71c', 'textShadow': '2px 2px black'})],align="center"),
            html.Br(),
            dbc.Row([dcc.Dropdown(id='events-types-key-metrics', options=events_types, value=sorted(list(events.eventType.fillna("NOT ASSIGNED").unique())), multi=True)
                    ],align="center",style={'marginLeft': 500,})
            ]),
    html.Br(),
    dbc.Row([dbc.Col(card_events_key_metrics_1, width=3),
             dbc.Col(card_events_key_metrics_2, width=3),
             dbc.Col(card_events_key_metrics_3, width=6)
             ], align='center', style={'marginLeft': 20}),
    html.Br(),
    html.Div(dbc.Row([
        html.H3('Given Period Analysis',style={'marginLeft': 50,'color': '#f8e71c', 'textShadow': '2px 2px black'}),
    ],align="center")),
    html.Br(),
    html.Div([dbc.Row(html.H5('Filter for all the Analysis below', style={'marginLeft': 500, 'marginRight': 0, 'textAlign': 'center'}), style={'textAlign': 'center'}),
              dbc.Row([dbc.Col(html.H6('Dates Filter'),width =6),
                       dbc.Col(html.H6('Events Type Filter'),width =6)
                       ], align="center",style={'marginLeft': 10, 'marginRight': 10, 'textAlign': 'center'}),
              dbc.Row([dbc.Col([
                    dcc.DatePickerRange(id="selected-dates-events", calendar_orientation='horizontal',
                                       day_size=20, end_date_placeholder_text="End date", with_portal=False,
                                       first_day_of_week=0, reopen_calendar_on_clear=True, is_RTL=False,
                                       clearable=False, number_of_months_shown=3,
                                       min_date_allowed=dt(2020, 1, 1),
                                       max_date_allowed=dt(2022, 12, 31),
                                       initial_visible_month=dt(2021, 1, 1),
                                       start_date=dt(2020, 8, 1).date(),
                                       end_date=pd.to_datetime("today").date(),
                                       display_format="DD-MMMM-YYYY", minimum_nights=6,
                                       persistence=True, persisted_props=["start_date"],
                                       persistence_type="session", updatemode="singledate")]),
                      dbc.Col(dcc.Dropdown(id='events-types', options=events_types, value=sorted(list(events.eventType.fillna("NOT ASSIGNED").unique())), multi=True))#,width=6,align="center")
                      ],style={'marginLeft': 10, 'marginRight': 10, 'textAlign': 'center'})
              ], style={'marginLeft': 100, 'marginRight': 100, 'border':'1px solid lightgrey','border-radius': 10}),
    html.Br(),
    dbc.CardColumns([card_events_given_period_1, card_events_given_period_2]),
    html.Br(),
    dbc.Row([dbc.Col(html.Div(dcc.Graph(id='events-wordcloud')),width=8),
            dbc.Col(dash_table.DataTable(
                id='events-authors',
                style_cell={"TextAlign" : "left",},
                style_header={'backgroundColor':'#4e99f6', 'color': 'white', 'fontWeight': 'bold', 'border':'1px solid black'},
                style_data_conditional=[{'if':{'row_index':'odd'},  'backgroundColor':'rgb(248,248,248)'}],
                page_size=15,
                style_table={'width':'400px','height':'500px',},
                style_as_list_view=True,
                export_format="csv",
            ),width=4)]),
    html.Div(),
    html.Br(),
    html.H2('NOTIFICATIONS',style={'marginLeft': 10,'color': '#4e99f6', 'textShadow': '2px 2px black'}),
    html.Br(),
    html.Div([dbc.Row(html.H5('Filter for all the Analysis below', style={'marginLeft': 500, 'marginRight': 0, 'textAlign': 'center'}), style={'textAlign': 'center'}),
              dbc.Row([dbc.Col(html.H6('Dates Filter'),width =6),
                       dbc.Col(html.H6('Notifications Type Filter'),width =6)
                       ], align="center",style={'marginLeft': 10, 'marginRight': 10, 'textAlign': 'center'}),
              dbc.Row([dbc.Col(dcc.DatePickerRange(id="selected-dates-notifications",calendar_orientation='horizontal',day_size=20,end_date_placeholder_text="End date",with_portal=False,
                             first_day_of_week=0,reopen_calendar_on_clear=True,is_RTL=False,clearable=False,number_of_months_shown=3,min_date_allowed=dt(2020,1,1),
                             max_date_allowed=pd.to_datetime("today").date(),initial_visible_month=dt(2021,1,1),
                             start_date=dt(2020, 8, 1).date(), end_date=pd.to_datetime("today").date(),display_format="DD-MMMM-YYYY",minimum_nights=6,
                             persistence=True,persisted_props=["start_date"],persistence_type="session",updatemode="singledate",style={'width':'500px','height':'100px',}
                             )),
                      dbc.Col(dcc.Dropdown(id='notifications-types', options=notifications_group, value=sorted(list(notifications.Group.fillna("NOT ASSIGNED").unique())), multi=True))
                      ],style={'marginLeft': 10, 'marginRight': 10, 'textAlign': 'center'})
              ], style={'marginLeft': 100, 'marginRight': 100, 'border':'1px solid lightgrey','border-radius': 10}),
    html.Div(dcc.Graph(id='notifications-treemap')),
    html.Div(dcc.Graph(id='notifications-wordcloud')),
    html.Br(),
    html.Div(),
])

# Creating the interactive parts of the app (graphs visualisations and filters mainly)

@app.callback(Output('users-evolution', 'figure'),[Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
def users_evolution(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    df = dataset_with_correct_dates(users[["id", "creationDate"]].copy(), "creationDate", start_date, end_date)

    df["creationDate"] = pd.to_datetime(df["creationDate"]).dt.date
    df["Count"] = 1
    dff = df.groupby("creationDate").sum()
    dff["Evolution"] = dff.sort_values(by="creationDate").Count.cumsum()
    dff = dff.loc[start_date:end_date]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_bar(x=dff.index, y=dff.Count, name="New daily users", secondary_y=False, marker=dict(color="#2dd36f"))
    fig.add_trace(go.Scatter(x=dff.index, y=dff['Evolution'], name="Cumulated New Users in chosen period", marker=dict(color="#7039bd")), secondary_y=True)

    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'

    fig.update_layout(
                        margin={"r": 0, "t": 40, "l": 0, "b": 0},
                        title_text='User Acquisition', title_font={'color': '#FFF'}, font_color='white',
                        width=800, height=550,
                        legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01, font=dict(color="black")),
                        xaxis={'showgrid': False},yaxis={'showgrid': False},yaxis2={'showgrid': False,"overlaying":"y","zeroline":False})

    return fig

@app.callback([Output('unique-schools', 'children'),Output('schools-without-children', 'children')],[Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
def school_number(start_date, end_date):
    df = classes.groupby("schoolid").sum()["nbChild"]

    return [classes.schoolid.nunique()], [df[df < 1].shape[0]]

@app.callback([Output('unique-classes', 'children'),Output('classes-without-children', 'children')],[Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
def classes_number(start_date, end_date):
    df = classes.groupby("id").sum()["nbChild"]

    return [classes.id.nunique()], [df[df < 1].shape[0]]

@app.callback(Output('children_number', 'figure'),[Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
def children_number(start_date, end_date):
    df = users.groupChildSize.value_counts().reset_index()
    df.rename(columns={'index': 'Number of Children', 'groupChildSize': "Number of Users"}, inplace=True)
    fig = px.bar(df, df["Number of Children"], df["Number of Users"], color_discrete_sequence=['#2dd36f','#4e99f6'], log_y=True, hover_name=df["Number of Users"])

    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Relationship between User and number of Children', title_font={'color': '#FFF'}, font_color='white',
        width=500, height=250, xaxis={'showgrid': False}, yaxis={'showgrid': False}
        )

    return fig


# Try out to identify users without any activity, but it didn't work very well:

# @app.callback([Output('inactive-users', 'data'),Output('inactive-users', 'columns')],
#               [Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
# def users_without_activities(start_date, end_date):
#
#     df = users.copy()
#     df = dataset_with_correct_dates(df, "creationDate", start_date, end_date)
#
#     df = df[['id', 'username', 'firstName', 'lastName', 'nbPhoneNumbers', 'nbEmails', 'city', 'groupChildSize',
#              'creationDate', 'lastModificationDate']]
#
#     df_homeworks = dataset_with_correct_dates(homeworks, "creationDate", dt(2020, 1, 1).date(), end_date)
#     df_events = dataset_with_correct_dates(events, "creationDate", start_date, end_date)
#     df_documents = dataset_with_correct_dates(documents, "creationDate", start_date, end_date)
#
#     #active_users = list(set(list(df_homeworks.userId.unique()) + list(df_events.author.unique())))
#     active_users = list(set(list(df_homeworks.userId.unique())+list(df_events.author.unique())+list(df_documents.userId.unique())))
#
#     df = df[~df.id.isin(active_users)]
#
#     data_columns = [{"name": i, "id": i} for i in df.columns]
#     data = df.to_dict('records')
#
#     return data, data_columns


@app.callback(Output('public-prive', 'figure'),[Input('regions_picker', 'value')])
def pie_public_prive(selected_regions):
    classes_filtered = classes[classes.libelle_region.isin(selected_regions)]
    df = pd.DataFrame(classes_filtered.groupby(["schoolid", "secteur_public_prive_libe"]).count()['id']).reset_index()
    df.secteur_public_prive_libe.value_counts()

    fig = go.Figure(data=[go.Pie(labels=df.secteur_public_prive_libe.value_counts().index,
                                 values=df.secteur_public_prive_libe.value_counts().values,
                                 #color_discrete_map={'Public': '#4e99f6', 'Privé': '#2dd36f'},
                                 insidetextfont={'color':'white'}, hole=.4,)])
                                 #textfont={'color':'#FFF'},outsidetextfont={'color':'#FFF'},insidetextfont={'color':'#FFF'})])
    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    #fig.layout.legend.font.color = 'white'

    colors = ['#4e99f6','#2dd36f']
    fig.update_traces(hoverinfo='label+percent', textinfo='value', marker=dict(colors=colors))

    fig.update_layout(showlegend=False,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Public & Private Schools', title_x=0.5, #title_y=0.9,
        width=250, height=250, title_font = {'color': 'black'},
        font_color='black',
        )

    return fig

@app.callback(Output('classes_map', 'figure'),
                 [Input('regions_picker', 'value')])
def update_map(selected_regions):
    if selected_regions ==[]:
        return dash.no_update

    with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
        france = json.load(response)

    classes_filtered = classes[classes.libelle_region.isin(selected_regions)]
    df1 = classes_filtered.groupby("schoolid").sum().drop(columns=["code_postal_uai","coordinatesLat","coordinatesLong"]) #"Unnamed: 0",
    df2 = classes[["schoolid","secteur_public_prive_libe","appellation_officielle","libelle_commune","localite_acheminement_uai","libelle_departement","libelle_region","code_postal_uai","geometry_type","coordinatesLat","coordinatesLong"]]

    classes_filtered = pd.merge(df1, df2, on="schoolid")
    classes_filtered.rename(columns={"appellation_officielle":"Nom de l'Ecole","secteur_public_prive_libe":"Secteur","nbChild":"Children assigned","nbArchivedChildren":"Children archived"}, inplace=True)

    fig = go.Figure(px.scatter_mapbox(classes_filtered, lat="coordinatesLat", lon="coordinatesLong", size="Children assigned", color='Secteur',
                                      color_discrete_map={'Public':'#4e99f6', 'Privé':'#2dd36f'},
                                      hover_name="Nom de l'Ecole", hover_data=["Children archived","Children assigned"]))
    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title_text = 'Schools per Region',
        mapbox=go.layout.Mapbox(style="carto-positron",
                               zoom=4.5, center_lat=47, center_lon=3,
                               layers=[{
                                   'sourcetype': 'geojson',
                                   'source': france,
                                   'type': 'line',
                                   'color': '#7039bd',
                                   'opacity':0.1,
                                   'below': "True",
                               }]
                               ))
    return fig

@app.callback([Output('homeworks-authors', 'data'),Output('homeworks-authors', 'columns')],[Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def homeworks_authors(start_date, end_date):
    df = homeworks[["id", "userId", "creationDate"]].copy()

    homeworks_authors = df.groupby("userId").count()["id"].sort_values(ascending=False).reset_index().rename(columns={"userId": "Author", "id": "Homeworks Created"})
    homeworks_authors["Rank"] = homeworks_authors["Homeworks Created"].rank(ascending=False)
    homeworks_authors["Rank"] = homeworks_authors["Rank"].apply(int)
    homeworks_authors = homeworks_authors[["Rank", "Author", "Homeworks Created"]]

    data_columns = [{"name": i, "id": i} for i in homeworks_authors.columns]
    data = homeworks_authors.to_dict('records')

    return data, data_columns

@app.callback(Output('homeworks-type', 'figure'),[Input('regions_picker', 'value')])
def homeworks_type(selected_regions):
    df = pd.DataFrame(homeworks.type.value_counts()).reset_index()
    df.rename(columns={'index': "Type", "type": "Number"}, inplace=True)

    fig = px.bar(df, x=df.Number, y=df.Type, color_discrete_sequence=["#2dd36f"])

    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Homeworks Type', title_x=0.5, xaxis={'showgrid': False},yaxis={'showgrid': False},
        width=400, height=200
        )

    return fig

@app.callback(Output('documents_type', 'figure'),[Input('regions_picker', 'value')])
def doc_type(selected_regions):
    df = pd.DataFrame(documents.type.value_counts()).reset_index()
    df.rename(columns={'index': "Type", "type": "Number"}, inplace=True)

    fig = go.Figure(data=[go.Pie(labels=df["Type"],
                                 values=df["Number"],
                                 insidetextfont={'color': 'white'},hole=.4)])
    # textfont={'color':'#FFF'},outsidetextfont={'color':'#FFF'},insidetextfont={'color':'#FFF'})])
    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    # fig.layout.legend.font.color = 'white'

    colors = ['#4e99f6', '#2dd36f']
    fig.update_traces(hoverinfo='label+percent', textinfo='value', marker=dict(colors=colors))

    fig.update_layout(showlegend=True,
                      margin={"r": 0, "t": 40, "l": 0, "b": 0},
                      title_text='Documents Types', title_x=0.5,  # title_y=0.9,
                      width=350, height=350, title_font={'color': 'black'},
                      font_color='black')

    return fig

@app.callback([Output(component_id='events-past', component_property='children'),Output(component_id='events-future', component_property='children')],
              [Input('events-types-key-metrics', 'value')])
def events_today(events_types):
    if events_types == []:
        return dash.no_update

    df = events[["id", "eventType", "firstPeriods-startDate"]].copy()
    df["eventType"].fillna('NOT ASSIGNED', inplace=True)
    df = df.loc[df["eventType"].isin(events_types)]

    dff = dataset_with_correct_dates(df, "firstPeriods-startDate", df["firstPeriods-startDate"].fillna("2020-01-01").min(), pd.to_datetime("today").date())
    dfff = dataset_with_correct_dates(df, "firstPeriods-startDate", pd.to_datetime("today").date(), df["firstPeriods-startDate"].fillna("2020-01-01").max())

    return [dff.id.nunique()], [dfff.id.nunique()]

@app.callback(Output('events-slots', 'figure'),[Input('events-types-key-metrics', 'value')])
def events_slots(events_types):
    if events_types == []:
        return dash.no_update

    df = events.loc[events["eventType"].isin(events_types)]

    df = df.nbPeriods.value_counts().reset_index()
    df.rename(columns={"index": "Number of Time Slots", "nbPeriods": "Number of Events Created"}, inplace=True)

    fig = px.bar(df, df["Number of Time Slots"], df["Number of Events Created"], color_discrete_sequence=['#2dd36f','#4e99f6'], log_y=True)

    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'

    fig.update_layout(showlegend=True,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Number of Slots chosen in all Events Created', title_font={'color': 'grey'}, font_color='grey',
        width=500, height=250, xaxis={'showgrid': False}, yaxis={'showgrid': False}
        )

    return fig

@app.callback([Output(component_id='events-in-this-period', component_property='children')],
              [Input('events-types', 'value'),Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def events_in_this_period(events_types, start_date, end_date):
    if events_types == []:
        return dash.no_update

    df = events[["id", "eventType", "firstPeriods-startDate"]].copy()
    df["eventType"].fillna('NOT ASSIGNED', inplace=True)
    df = df.loc[df["eventType"].isin(events_types)]

    df = dataset_with_correct_dates(df, "firstPeriods-startDate", start_date, end_date)

    return [df.id.nunique()]

@app.callback(Output('events-dayofweek', 'figure'),[Input('events-types', 'value'),Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def events_dayofweek(events_types, start_date, end_date):
    if events_types == []:
        return dash.no_update

    df = events[["id", "eventType", "firstPeriods-startDate"]].copy()
    df["eventType"].fillna('NOT ASSIGNED', inplace=True)

    df = df.loc[df["eventType"].isin(events_types)]

    df = dataset_with_correct_dates(df, "firstPeriods-startDate", start_date, end_date)

    df['firstPeriods-startDate'] = pd.to_datetime(df['firstPeriods-startDate']).dt.dayofweek
    days_dict = {0: "MONDAY", 1: "TUESDAY", 2: "WEDNESDAY", 3: "THURSDAY", 4: "FRIDAY", 5: "SATURDAY", 6: "SUNDAY"}
    df['firstPeriods-startDate'] = df['firstPeriods-startDate'].apply(lambda x: days_dict[x])

    df = df.groupby(by=["eventType", "firstPeriods-startDate"]).count()
    df.reset_index(inplace=True)
    days_dict = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
    df["day_number"] = df["firstPeriods-startDate"].apply(lambda x: days_dict[x])
    df.set_index("day_number", inplace=True)
    df.rename(columns={"eventType": "Event Type", "firstPeriods-startDate": "Day of the Week", "id": "Number of Events"},inplace=True)
    df = df.sort_values(by=["day_number","Number of Events"],ascending=[True, False])

    fig = px.bar(df, x='Day of the Week', y='Number of Events', color='Event Type',color_discrete_sequence=["#4e99f6","#2dd36f","#7039bd","#f8e71c"])#,barmode='group')

    fig.layout.paper_bgcolor = 'rgba(0,0,0,0)'
    fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Events per Day of the Week', title_x=0.5, xaxis={'showgrid': False},yaxis={'showgrid': False},
        width=850, height=250
        )

    return fig

@app.callback(Output('events-wordcloud', 'figure'),
                 [Input('events-types', 'value'), Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def wordcloud_events(events_types,start_date,end_date):
    if events_types == []:
        return dash.no_update

    df = events[["label", "eventType", "firstPeriods-startDate"]].copy()
    df["eventType"].fillna('NOT ASSIGNED', inplace=True)
    df = df.loc[df["eventType"].isin(events_types)]

    df = dataset_with_correct_dates(df, "firstPeriods-startDate", start_date, end_date)
    df.reset_index(inplace=True, drop=True)

    text = " ".join([df.label[i] for i in range(0, df.shape[0]) if pd.notna(df.label[i])])

    counts = Counter(text.split(" "))
    counts = sorted(counts.items(), key=lambda x: -x[1])

    text_list = set()
    i = 0
    while (len(text_list) < 40) and (i < len(counts)):
        if (counts[i][0] not in stopwords) and (len(counts[i][0])>2):
            text_list.add(counts[i][0])
        i += 1

    colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(40)]
    weights = [45 - i for i in range(40)]

    data = go.Scatter(x=[random.random() for i in range(40)],
                      y=[random.random() for i in range(40)],
                      # y=[random.choices(range(30), k=30) for i in range(40)],
                      mode='text',
                      text=list(text_list),
                      marker={'opacity': 0.3},
                      textfont={'size': weights,
                                'color': colors})
    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'margin': {"r": 0, "t": 30, "l": 0, "b": 0}})
    fig = go.Figure(data=[data], layout=layout)

    return fig

@app.callback([Output('events-authors', 'data'),Output('events-authors', 'columns')],
              [Input('events-types', 'value'), Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def events_authors(events_types, start_date, end_date):
    if events_types == []:
        return dash.no_update

    df = events[["id", "author", "eventType", "firstPeriods-startDate"]].copy()
    df["eventType"].fillna('NOT ASSIGNED', inplace=True)
    df = df.loc[df["eventType"].isin(events_types)]

    df = dataset_with_correct_dates(df, "firstPeriods-startDate", start_date, end_date)

    events_authors = df.groupby("author").count()["id"].sort_values(ascending=False).reset_index().rename(columns={"author": "Author", "id": "Events Created"})
    events_authors["Rank"] = events_authors["Events Created"].rank(ascending=False)
    events_authors["Rank"] = events_authors["Rank"].apply(int)
    events_authors = events_authors[["Rank", "Author", "Events Created"]]

    data_columns = [{"name": i, "id": i} for i in events_authors.columns]
    data = events_authors.to_dict('records')

    return data, data_columns

@app.callback(Output('notifications-treemap', 'figure'),
                 [Input('notifications-types', 'value'), Input('selected-dates-notifications', 'start_date'), Input('selected-dates-notifications', 'end_date')])
def treemap_notifications(notifications_group, start_date, end_date):
    if notifications_group == []:
        return dash.no_update

    df = notifications[["id", "creationDate", "notificationType", "Group"]].copy()
    df.fillna("NOT ASSIGNED",inplace=True)
    df = df.loc[df["Group"].isin(notifications_group)]
    df = dataset_with_correct_dates(df, "creationDate", start_date, end_date)

    df = df.groupby(["Group", "notificationType"]).count()
    df = df.reset_index().rename(columns={'id': 'Number'})
    df["Notifications"] = "NOTIFICATIONS"

    fig = px.treemap(df, path=['Notifications', 'Group', 'notificationType'], values=df["Number"], color=df["Group"],
                     color_discrete_map={"(?)":"#d3d3d3", "SETUP": "#4e99f6", "EVENT":"#2dd36f", "HOMEWORK" : "#7039bd", "CLASSES" : "#f8e71c"},
                     hover_name=df["Number"])

    fig.data[0].textinfo = 'label+text+value+percent parent+percent root'

    return fig

@app.callback(Output('notifications-wordcloud', 'figure'),
                 [Input('selected-dates-notifications', 'start_date'),Input('selected-dates-notifications', 'end_date')])
def wordcloud_notifications(start_date,end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    source = notifications[["creationDate", "message"]].copy()
    source.dropna(axis=0, inplace=True)
    source["creationDate"] = pd.to_datetime(source["creationDate"]).dt.date

    source["message"] = source["message"].str.strip(',.!?\n\t')
    source["message"] = source["message"].str.replace(",", "")
    source["message"] = source["message"].str.replace("l''agenda", "l'agenda")
    source["message"] = source["message"].str.replace(",", "")

    source = source.sort_values("creationDate", ignore_index=True)
    source2 = source.set_index("creationDate")
    source2 = source2[~source2.index.duplicated(keep='first')]

    start_index = source2.index.get_loc(start_date, method='bfill')
    start_date = source2.reset_index().iloc[start_index]["creationDate"]

    end_index = source2.index.get_loc(end_date, method='ffill')
    end_date = source2.reset_index().iloc[end_index]["creationDate"]

    source = source.loc[(source.creationDate>=start_date)&(source.creationDate<=end_date)]
    source.reset_index(inplace=True, drop=True)

    text = " ".join([source.message[i] for i in range(0, source.shape[0]) if pd.notna(source.message[i])])

    counts = Counter(text.split(" "))
    counts = sorted(counts.items(), key=lambda x: -x[1])

    text_list = set()
    i = 0
    while (len(text_list) < 40) and (i < len(counts)):
        if (counts[i][0] not in stopwords) and (len(counts[i][0])>2):
            text_list.add(counts[i][0])
        i += 1

    colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(40)]
    # weights = [random.randint(15, 35) for i in range(40)]
    weights = [45 - i for i in range(40)]

    data = go.Scatter(x=[random.random() for i in range(40)],
                      #y=[random.random() for i in range(40)],
                      y=[random.choices(range(40), k=40) for i in range(40)],
                      mode='text',
                      text=list(text_list),
                      marker={'opacity': 0.3},
                      textfont={'size': weights,
                                'color': colors})
    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'margin': {"r": 0, "t": 30, "l": 0, "b": 0}})
    fig = go.Figure(data=[data], layout=layout)

    return fig

# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)