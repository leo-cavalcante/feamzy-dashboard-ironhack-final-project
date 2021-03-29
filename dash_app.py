import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

classes = pd.read_csv("data_clean/ClassStats.csv")
users = pd.read_csv("data_clean/User.csv")
homeworks = pd.read_csv("data_clean/HomeworkRequest.csv")
documents = pd.read_csv("data_clean/Document.csv")
notifications = pd.read_csv("data_clean/Notification.csv")
events = pd.read_csv("data_clean/Event.csv")

card_users_1 = dbc.Card([
     dbc.CardBody(
         [
             html.Div(children=[users.id.count()], style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'}),
             html.H4(['Total Users'], style={'color': '#696969','textAlign': 'center'}),
         ]
     )
 ])

card_users_2 = dbc.Card([
     dbc.CardBody(
         [
             dcc.Graph(id='users-evolution'),
             dcc.DatePickerRange(id="selected-dates-users", calendar_orientation='horizontal', day_size=20,
                                         end_date_placeholder_text="End date", with_portal=False,
                                         first_day_of_week=0, reopen_calendar_on_clear=True, is_RTL=False,
                                         clearable=True, number_of_months_shown=3, min_date_allowed=dt(2020, 1, 1),
                                         max_date_allowed=pd.to_datetime("today").date(),
                                         initial_visible_month=dt(2021, 1, 1),
                                         start_date=dt(2021, 1, 1).date(), end_date=pd.to_datetime("today").date(),
                                         display_format="DD-MMMM-YYYY", minimum_nights=6,
                                         persistence=True, persisted_props=["start_date"], persistence_type="session",
                                         updatemode="singledate"
                                         )
         ]
     )
 ])

card_classes_key_metrics = dbc.Card([
     dbc.CardBody(
         [
             html.Div(children=[users.id.count()], style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'}),
             html.H4(['Total Users'], style={'color': '#696969','textAlign': 'center'}),
         ]
     )
 ])


region_options = []
for region in sorted(list(classes.libelle_region.unique())):
    region_options.append({'label': str(region),'value': region})

app.layout = html.Div(children=[
    html.Div(html.Img(src="https://www.relations-publiques.pro/wp-content/uploads/2021/01/20210112103656-p1-document-bpmt.png", alt="Feamzy logo",
            style={'maxWidth': '15%', 'maxHeight': '15%', 'marginLeft': 20, 'marginTop': 20}), style={'textAlign': 'center'}),
    html.H1(['Dashboard'], style={'color': '#4e98f5','textAlign': 'center'}),
    html.Br(),
    html.H2('Users', style={'marginLeft': 10}),
    # dbc.Row([dbc.Col(html.Div(children=[users.id.count()], style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'}),width=3),
    #     dcc.Graph(id='users-evolution')
    #     ], style={'height': 250, 'marginLeft': 10}, align="end"),
    # dbc.Row(
    #     [dbc.Col(html.Div(children=["Users"], style={'marginBottom': 25,'textAlign': 'center'}),width=3),
    #      dbc.Col(dcc.DatePickerRange(id="selected-dates-users",calendar_orientation='horizontal',day_size=20,end_date_placeholder_text="End date",with_portal=False,
    #                          first_day_of_week=0,reopen_calendar_on_clear=True,is_RTL=False,clearable=True,number_of_months_shown=3,min_date_allowed=dt(2020,1,1),
    #                          max_date_allowed=pd.to_datetime("today").date(),initial_visible_month=dt(2021,1,1),
    #                          start_date=dt(2021,1,1).date(), end_date=pd.to_datetime("today").date(),display_format="DD-MMMM-YYYY",minimum_nights=6,
    #                          persistence=True,persisted_props=["start_date"],persistence_type="session",updatemode="singledate"
    #                          ))
    #      ]),
    #dbc.CardGroup([card_users_1, card_users_2]),
    dbc.Row([dbc.Col(card_users_1,width=5), dbc.Col(card_users_2, width=7)]),
    html.Br(),
    html.H2('Classes',style={'marginLeft': 10}),
    dbc.Row(
        [dbc.Col(html.Div(children=["Number of Schools"], style={'marginBottom': 25, 'textAlign': 'center'}),width=3),
         dbc.Col(html.Div(children=["Average Children per Class"], style={'marginBottom': 25, 'textAlign': 'center'}),width=3),
         ], style={'height': 10, 'marginLeft': 10}, align="end"),
    dbc.Row(
        [dbc.Col(html.Div(children=[classes.id.nunique()],
                 style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'}),width=3),
        dbc.Col(html.Div(children=[(classes["nbChild"].sum()/classes.shape[0]).round(2)],
                 style={'marginTop': 25, 'fontSize': 50, 'color': '#4e98f5','textAlign': 'center'}),width=3),
        dcc.Graph(id='public-prive')
        ],style={'height': 250,'marginLeft': 10},align="start"),
    dcc.Dropdown(id='regions_picker', options=region_options, value=sorted(list(classes.libelle_region.unique())), multi=True, style={'marginLeft': 20,'marginRight': 50}),
    dcc.Graph(id="classes_map"),
    html.Br(),
    html.H2('Documents', style={'marginLeft': 10}),
    dbc.Row(
        [dbc.Col(html.Div(children=["Number of Documents"], style={'marginBottom': 25, 'textAlign': 'center'}), width=3),
         dbc.Col(html.Div(),width=6),
         ], style={'height': 10, 'marginLeft': 10}, align="end"),
    dbc.Row(
        [dbc.Col(html.Div(children=[documents.id.nunique()], style={'marginTop': 25, 'fontSize': 50,'color': '#4e98f5','textAlign': 'center'}),width=3),
         dbc.Col(html.Div(dcc.Graph(id='documents_type')),width=6),
         ], style={'height': 250, 'marginLeft': 10}, align="start"),
    html.Br(),
    html.H2('Events', style={'marginLeft': 10}),
    html.Br(),
    dbc.Row([dbc.Col(html.H6('Global Filter', style={'marginLeft': 10, 'marginRight': 0, 'textAlign': 'right'}),width=2),
                dbc.Col(dcc.DatePickerRange(id="selected-dates-events",calendar_orientation='horizontal',day_size=20,end_date_placeholder_text="End date",with_portal=False,
                             first_day_of_week=0,reopen_calendar_on_clear=True,is_RTL=False,clearable=True,number_of_months_shown=3,min_date_allowed=dt(2020,1,1),
                             max_date_allowed=dt(2022,12,31),initial_visible_month=dt(2021,1,1),
                             start_date=dt(2020,8,1).date(), end_date=pd.to_datetime("today").date(),display_format="DD-MMMM-YYYY",minimum_nights=6,
                             persistence=True,persisted_props=["start_date"],persistence_type="session",updatemode="singledate"
                             ))],align="center"),
    html.Br(),
    html.Br(),
    html.Div(dcc.Graph(id='events-dayofweek')),
    dbc.Row([dbc.Col(html.Div(dcc.Graph(id='events-wordcloud')),width=8),
    dbc.Col(dash_table.DataTable(
        id='events-authors',
        style_cell={"TextAlign" : "left",},
        style_header={'backgroundColor':'#4e98f5', 'color': 'white', 'fontWeight': 'bold', 'border':'1px solid black'},
        style_data_conditional=[{'if':{'row_index':'odd'},  'backgroundColor':'rgb(248,248,248)'}],
        page_size=15,
        style_table={'width':'400px','height':'500px',},
        style_as_list_view=True,),width=4)]),
    html.Div(),
    html.Br(),
    html.H2('Notifications',style={'marginLeft': 10}),
    html.Div(dcc.Graph(id='notifications-wordcloud')),
    html.Div(dcc.DatePickerRange(id="selected-dates-notifications",calendar_orientation='horizontal',day_size=20,end_date_placeholder_text="End date",with_portal=False,
                             first_day_of_week=0,reopen_calendar_on_clear=True,is_RTL=False,clearable=True,number_of_months_shown=3,min_date_allowed=dt(2020,1,1),
                             max_date_allowed=pd.to_datetime("today").date(),initial_visible_month=dt(2021,1,1),
                             start_date=dt(2020,8,1).date(), end_date=pd.to_datetime("today").date(),display_format="DD-MMMM-YYYY",minimum_nights=6,
                             persistence=True,persisted_props=["start_date"],persistence_type="session",updatemode="singledate",style={'width':'400px','height':'100px',}
                             )),
    html.Br(),
    html.Div(),
])

@app.callback(Output('users-evolution', 'figure'),[Input('selected-dates-users', 'start_date'),Input('selected-dates-users', 'end_date')])
def users_evolution(start_date,  end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    df = users[["id", "creationDate"]].copy()
    df["creationDate"] = pd.to_datetime(df["creationDate"]).dt.date
    df["Count"] = 1
    dff = df.groupby("creationDate").sum()
    dff["Evolution"] = dff.sort_values(by="creationDate").Count.cumsum()
    dff = dff.loc[start_date:end_date]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=dff.index, y=dff['Evolution'], name="Cumulated Users"), secondary_y=True)
    fig.add_bar(x=dff.index, y=dff.Count, name="# New users", secondary_y=False)

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Users evolution',
        width=800, height=250
        )

    return fig

@app.callback(Output('public-prive', 'figure'),[Input('regions_picker', 'value')])
def pie_public_prive(selected_regions):
    classes_filtered = classes[classes.libelle_region.isin(selected_regions)]

    fig = go.Figure(data=[go.Pie(labels=classes_filtered.secteur_public_prive_libe.value_counts().index,
                           values=classes_filtered.secteur_public_prive_libe.value_counts().values)])

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Public & Private Schools', title_x=0.5, #title_y=0.9,
        width=400, height=250
        )

    return fig


@app.callback(Output('classes_map', 'figure'),
                 [Input('regions_picker', 'value')])
def update_map(selected_regions):
    #if selected_regions ==[]:
    #    raise PreventUpdate

    with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
        france = json.load(response)

    classes_filtered = classes[classes.libelle_region.isin(selected_regions)]

    fig = go.Figure(px.scatter_mapbox(classes_filtered, lat="coordinatesLat", lon="coordinatesLong", text="appellation_officielle", color='secteur_public_prive_libe',
                    size="nbChild", color_continuous_scale="Viridis", range_color=(0, 12)))

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

@app.callback(Output('events-dayofweek', 'figure'),[Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def events_dayofweek(start_date, end_date):
    df = dataset_with_correct_dates(events[["id","firstPeriods-startDate"]].copy(), "firstPeriods-startDate", start_date, end_date)

    df = df['firstPeriods-startDate'].dropna().copy()
    df = pd.to_datetime(df).dt.dayofweek
    days_dict = {0: "MONDAY", 1: "TUESDAY", 2: "WEDNESDAY", 3: "THURSDAY", 4: "FRIDAY", 5: "SATURDAY", 6: "SUNDAY"}
    df = df.apply(lambda x: days_dict[x])

    df = pd.DataFrame(df.value_counts()).reset_index()
    df.rename(columns={'index': 'Day of the Week', 'firstPeriods-startDate': 'Number of Events'}, inplace=True)

    days_dict = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
    df["day_number"] = df['Day of the Week'].apply(lambda x: days_dict[x])
    df = df.set_index('day_number').sort_index()
    fig = px.bar(df, x='Day of the Week', y='Number of Events')

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Events per Day of the Week', title_x=0.5, #title_y=0.9,
        width=800, height=250
        )

    return fig

@app.callback(Output('events-wordcloud', 'figure'),
                 [Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def wordcloud_events(start_date,end_date):
    df = dataset_with_correct_dates(events[["firstPeriods-startDate", "label"]].copy(), "firstPeriods-startDate", start_date, end_date)
    # start_date = pd.to_datetime(start_date).date()
    # end_date = pd.to_datetime(end_date).date()
    #
    # source = events[["firstPeriods-startDate", "label"]].copy()
    # source.dropna(axis=0, inplace=True)
    # source["firstPeriods-startDate"] = pd.to_datetime(source["firstPeriods-startDate"]).dt.date
    #
    # source = source.sort_values("firstPeriods-startDate", ignore_index=True)
    # source2 = source.set_index("firstPeriods-startDate")
    # source2 = source2[~source2.index.duplicated(keep='first')]
    #
    # start_index = source2.index.get_loc(start_date, method='bfill')
    # start_date = source2.reset_index().iloc[start_index]["firstPeriods-startDate"]
    #
    # end_index = source2.index.get_loc(end_date, method='ffill')
    # end_date = source2.reset_index().iloc[end_index]["firstPeriods-startDate"]
    #
    # source = source.loc[(source["firstPeriods-startDate"]>=start_date)&(source["firstPeriods-startDate"]<=end_date)]
    df.reset_index(inplace=True, drop=True)

    text = " ".join([df.label[i] for i in range(0, df.shape[0]) if pd.notna(df.label[i])])

    stopwords = ["a", "abord", "absolument", "afin", "ah", "ai", "aie", "aient", "aies", "ailleurs", "ainsi", "ait","allaient", "allo", "allons", "allô", "alors", "anterieur", "anterieure", "anterieures", "apres",
                 "après", "as", "assez", "attendu", "au", "aucun", "aucune", "aucuns", "aujourd", "aujourd'hui","aupres", "auquel", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez",
                 "aurions", "aurons", "auront", "aussi", "autant", "autre", "autrefois", "autrement", "autres","autrui", "aux", "auxquelles", "auxquels", "avaient", "avais", "avait", "avant", "avec", "avez",
                 "aviez", "avions", "avoir", "avons", "ayant", "ayez", "ayons", "b", "bah", "bas", "basee", "bat","beau", "beaucoup", "bien", "bigre", "bon", "boum", "bravo", "brrr", "c", "car", "ce", "ceci", "cela",
                 "celle", "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui", "celui-ci", "celui-là","celà", "cent", "cependant", "certain", "certaine", "certaines", "certains", "certes", "ces", "cet",
                 "cette", "ceux", "ceux-ci", "ceux-là", "chacun", "chacune", "chaque", "cher", "chers", "chez", "chiche", "chut", "chère", "chères", "ci", "cinq", "cinquantaine", "cinquante", "cinquantième",
                 "cinquième", "clac", "clic", "combien", "comme", "comment", "comparable", "comparables", "compris", "concernant", "contre", "couic", "crac", "d", "da", "dans", "de", "debout", "dedans", "dehors", "deja",
                 "delà", "depuis", "dernier", "derniere", "derriere", "derrière", "des", "desormais", "desquelles","desquels", "dessous", "dessus", "deux", "deuxième", "deuxièmement", "devant", "devers", "devra",
                 "devrait", "different", "differentes", "differents", "différent", "différente", "différentes", "différents", "dire", "directe", "directement", "dit", "dite", "dits", "divers", "diverse", "diverses",
                 "dix", "dix-huit", "dix-neuf", "dix-sept", "dixième", "doit", "doivent", "donc", "dont", "dos","douze", "douzième", "dring", "droite", "du", "duquel", "durant", "dès", "début", "désormais", "e",
                 "effet", "egale", "egalement", "egales", "eh", "elle", "elle-même", "elles", "elles-mêmes", "en","encore", "enfin", "entre", "envers", "environ", "es", "essai", "est", "et", "etant", "etc", "etre",
                 "eu", "eue", "eues", "euh", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions","eut", "eux", "eux-mêmes", "exactement", "excepté", "extenso", "exterieur", "eûmes", "eût", "eûtes",
                 "f", "fais", "faisaient", "faisant", "fait", "faites", "façon", "feront", "fi", "flac", "floc", "fois","font", "force", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "fûmes",
                 "fût", "fûtes", "g", "gens", "h", "ha", "haut", "hein", "hem", "hep", "hi", "ho", "holà", "hop","hormis", "hors", "hou", "houp", "hue", "hui", "huit", "huitième", "hum", "hurrah", "hé", "hélas", "i",
                 "ici", "il", "ils", "importe", "j", "je", "jusqu", "jusque", "juste", "k", "l", "la", "laisser","laquelle", "las", "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "longtemps",
                 "lors", "lorsque", "lui", "lui-meme", "lui-même", "là", "lès", "m", "ma", "maint", "maintenant","mais", "malgre", "malgré", "maximale", "me", "meme", "memes", "merci", "mes", "mien", "mienne",
                 "miennes", "miens", "mille", "mince", "mine", "minimale", "moi", "moi-meme", "moi-même", "moindres","moins", "mon", "mot", "moyennant", "multiple", "multiples", "même", "mêmes", "n", "na", "naturel",
                 "naturelle", "naturelles", "ne", "neanmoins", "necessaire", "necessairement", "neuf", "neuvième", "ni","nombreuses", "nombreux", "nommés", "non", "nos", "notamment", "notre", "nous", "nous-mêmes",
                 "nouveau", "nouveaux", "nul", "néanmoins", "nôtre", "nôtres", "o", "oh", "ohé", "ollé", "olé", "on","ont", "onze", "onzième", "ore", "ou", "ouf", "ouias", "oust", "ouste", "outre", "ouvert", "ouverte",
                 "ouverts", "o|", "où", "p", "paf", "pan", "par", "parce", "parfois", "parle", "parlent", "parler","parmi", "parole", "parseme", "partant", "particulier", "particulière", "particulièrement", "pas",
                 "passé", "pendant", "pense", "permet", "personne", "personnes", "peu", "peut", "peuvent", "peux","pff", "pfft", "pfut", "pif", "pire", "pièce", "plein", "plouf", "plupart", "plus", "plusieurs",
                 "plutôt", "possessif", "possessifs", "possible", "possibles", "pouah", "pour", "pourquoi", "pourrais","pourrait", "pouvait", "prealable", "precisement", "premier", "première", "premièrement", "pres",
                 "probable", "probante", "procedant", "proche", "près", "psitt", "pu", "puis", "puisque", "pur", "pure","q", "qu", "quand", "quant", "quant-à-soi", "quanta", "quarante", "quatorze", "quatre", "quatre-vingt",
                 "quatrième", "quatrièmement", "que", "quel", "quelconque", "quelle", "quelles", "quelqu'un", "quelque","quelques", "quels", "qui", "quiconque", "quinze", "quoi", "quoique", "r", "rare", "rarement", "rares",
                 "relative", "relativement", "remarquable", "rend", "rendre", "restant", "reste", "restent","restrictif", "retour", "revoici", "revoilà", "rien", "s", "sa", "sacrebleu", "sait", "sans",
                 "sapristi", "sauf", "se", "sein", "seize", "selon", "semblable", "semblaient", "semble", "semblent","sent", "sept", "septième", "sera", "serai", "seraient", "serais", "serait", "seras", "serez",
                 "seriez", "serions", "serons", "seront", "ses", "seul", "seule", "seulement", "si", "sien", "sienne","siennes", "siens", "sinon", "six", "sixième", "soi", "soi-même", "soient", "sois", "soit", "soixante",
                 "sommes", "son", "sont", "sous", "souvent", "soyez", "soyons", "specifique", "specifiques","speculatif", "stop", "strictement", "subtiles", "suffisant", "suffisante", "suffit", "suis", "suit",
                 "suivant", "suivante", "suivantes", "suivants", "suivre", "sujet", "superpose", "sur", "surtout", "t","ta", "tac", "tandis", "tant", "tardive", "te", "tel", "telle", "tellement", "telles", "tels",
                 "tenant", "tend", "tenir", "tente", "tes", "tic", "tien", "tienne", "tiennes", "tiens", "toc", "toi","toi-même", "ton", "touchant", "toujours", "tous", "tout", "toute", "toutefois", "toutes", "treize",
                 "trente", "tres", "trois", "troisième", "troisièmement", "trop", "très", "tsoin", "tsouin", "tu", "té","u", "un", "une", "unes", "uniformement", "unique", "uniques", "uns", "v", "va", "vais", "valeur",
                 "vas", "vers", "via", "vif", "vifs", "vingt", "vivat", "vive", "vives", "vlan", "voici", "voie","voient", "voilà", "voire", "vont", "vos", "votre", "vous", "vous-mêmes", "vu", "vé", "vôtre",
                 "vôtres", "w", "x", "y", "z", "zut", "à", "â", "ça", "ès", "étaient", "étais", "était", "étant","état", "étiez", "étions", "été", "étée", "étées", "étés", "êtes", "être", "ô", "the", "-", ".", "!",
                 "'", 'in', 'B', "+","1","2","3","4","5","6","7","8","9","10","cc","Cc","CC","Faire","faire","dr","M.","m","m.","Mme","mme","mme.","pute","putain","salope","con","conasse"]

    counts = Counter(text.split(" "))
    counts = sorted(counts.items(), key=lambda x: -x[1])

    text_list = set()
    i = 0
    while len(text_list) < 40 or i < len(counts):
        if counts[i][0] not in stopwords:
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

@app.callback([Output('events-authors', 'data'),Output('events-authors', 'columns')],[Input('selected-dates-events', 'start_date'),Input('selected-dates-events', 'end_date')])
def events_authors(start_date, end_date):

    df = dataset_with_correct_dates(events[["id","author","firstPeriods-startDate"]].copy(), "firstPeriods-startDate", start_date, end_date)

    events_authors = df.groupby("author").count()["id"].sort_values(ascending=False).reset_index().rename(columns={"author": "Author", "id": "Events Created"})
    events_authors["Rank"] = events_authors["Events Created"].rank(ascending=False)
    events_authors["Rank"] = events_authors["Rank"].apply(int)
    events_authors = events_authors[["Rank", "Author", "Events Created"]]

    data_columns = [{"name": i, "id": i} for i in events_authors.columns]
    data = events_authors.to_dict('records')

    return data, data_columns

@app.callback(Output('documents_type', 'figure'),[Input('regions_picker', 'value')])
def doc_type(selected_regions):
    df = pd.DataFrame(documents.type.value_counts()).reset_index()
    df.rename(columns={'index': "Type", "type": "Number"}, inplace=True)
    fig = px.bar(df, x=df.Number, y=df.Type)

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text='Documents Type', title_x=0.5, #title_y=0.9,
        width=400, height=200
        )

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

    stopwords = ["a", "abord", "absolument", "afin", "ah", "ai", "aie", "aient", "aies", "ailleurs", "ainsi", "ait","allaient", "allo", "allons", "allô", "alors", "anterieur", "anterieure", "anterieures", "apres",
                 "après", "as", "assez", "attendu", "au", "aucun", "aucune", "aucuns", "aujourd", "aujourd'hui","aupres", "auquel", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez",
                 "aurions", "aurons", "auront", "aussi", "autant", "autre", "autrefois", "autrement", "autres","autrui", "aux", "auxquelles", "auxquels", "avaient", "avais", "avait", "avant", "avec", "avez",
                 "aviez", "avions", "avoir", "avons", "ayant", "ayez", "ayons", "b", "bah", "bas", "basee", "bat","beau", "beaucoup", "bien", "bigre", "bon", "boum", "bravo", "brrr", "c", "car", "ce", "ceci", "cela",
                 "celle", "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui", "celui-ci", "celui-là","celà", "cent", "cependant", "certain", "certaine", "certaines", "certains", "certes", "ces", "cet",
                 "cette", "ceux", "ceux-ci", "ceux-là", "chacun", "chacune", "chaque", "cher", "chers", "chez", "chiche", "chut", "chère", "chères", "ci", "cinq", "cinquantaine", "cinquante", "cinquantième",
                 "cinquième", "clac", "clic", "combien", "comme", "comment", "comparable", "comparables", "compris", "concernant", "contre", "couic", "crac", "d", "da", "dans", "de", "debout", "dedans", "dehors", "deja",
                 "delà", "depuis", "dernier", "derniere", "derriere", "derrière", "des", "desormais", "desquelles","desquels", "dessous", "dessus", "deux", "deuxième", "deuxièmement", "devant", "devers", "devra",
                 "devrait", "different", "differentes", "differents", "différent", "différente", "différentes", "différents", "dire", "directe", "directement", "dit", "dite", "dits", "divers", "diverse", "diverses",
                 "dix", "dix-huit", "dix-neuf", "dix-sept", "dixième", "doit", "doivent", "donc", "dont", "dos","douze", "douzième", "dring", "droite", "du", "duquel", "durant", "dès", "début", "désormais", "e",
                 "effet", "egale", "egalement", "egales", "eh", "elle", "elle-même", "elles", "elles-mêmes", "en","encore", "enfin", "entre", "envers", "environ", "es", "essai", "est", "et", "etant", "etc", "etre",
                 "eu", "eue", "eues", "euh", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions","eut", "eux", "eux-mêmes", "exactement", "excepté", "extenso", "exterieur", "eûmes", "eût", "eûtes",
                 "f", "fais", "faisaient", "faisant", "fait", "faites", "façon", "feront", "fi", "flac", "floc", "fois","font", "force", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "fûmes",
                 "fût", "fûtes", "g", "gens", "h", "ha", "haut", "hein", "hem", "hep", "hi", "ho", "holà", "hop","hormis", "hors", "hou", "houp", "hue", "hui", "huit", "huitième", "hum", "hurrah", "hé", "hélas", "i",
                 "ici", "il", "ils", "importe", "j", "je", "jusqu", "jusque", "juste", "k", "l", "la", "laisser","laquelle", "las", "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "longtemps",
                 "lors", "lorsque", "lui", "lui-meme", "lui-même", "là", "lès", "m", "ma", "maint", "maintenant","mais", "malgre", "malgré", "maximale", "me", "meme", "memes", "merci", "mes", "mien", "mienne",
                 "miennes", "miens", "mille", "mince", "mine", "minimale", "moi", "moi-meme", "moi-même", "moindres","moins", "mon", "mot", "moyennant", "multiple", "multiples", "même", "mêmes", "n", "na", "naturel",
                 "naturelle", "naturelles", "ne", "neanmoins", "necessaire", "necessairement", "neuf", "neuvième", "ni","nombreuses", "nombreux", "nommés", "non", "nos", "notamment", "notre", "nous", "nous-mêmes",
                 "nouveau", "nouveaux", "nul", "néanmoins", "nôtre", "nôtres", "o", "oh", "ohé", "ollé", "olé", "on","ont", "onze", "onzième", "ore", "ou", "ouf", "ouias", "oust", "ouste", "outre", "ouvert", "ouverte",
                 "ouverts", "o|", "où", "p", "paf", "pan", "par", "parce", "parfois", "parle", "parlent", "parler","parmi", "parole", "parseme", "partant", "particulier", "particulière", "particulièrement", "pas",
                 "passé", "pendant", "pense", "permet", "personne", "personnes", "peu", "peut", "peuvent", "peux","pff", "pfft", "pfut", "pif", "pire", "pièce", "plein", "plouf", "plupart", "plus", "plusieurs",
                 "plutôt", "possessif", "possessifs", "possible", "possibles", "pouah", "pour", "pourquoi", "pourrais","pourrait", "pouvait", "prealable", "precisement", "premier", "première", "premièrement", "pres",
                 "probable", "probante", "procedant", "proche", "près", "psitt", "pu", "puis", "puisque", "pur", "pure","q", "qu", "quand", "quant", "quant-à-soi", "quanta", "quarante", "quatorze", "quatre", "quatre-vingt",
                 "quatrième", "quatrièmement", "que", "quel", "quelconque", "quelle", "quelles", "quelqu'un", "quelque","quelques", "quels", "qui", "quiconque", "quinze", "quoi", "quoique", "r", "rare", "rarement", "rares",
                 "relative", "relativement", "remarquable", "rend", "rendre", "restant", "reste", "restent","restrictif", "retour", "revoici", "revoilà", "rien", "s", "sa", "sacrebleu", "sait", "sans",
                 "sapristi", "sauf", "se", "sein", "seize", "selon", "semblable", "semblaient", "semble", "semblent","sent", "sept", "septième", "sera", "serai", "seraient", "serais", "serait", "seras", "serez",
                 "seriez", "serions", "serons", "seront", "ses", "seul", "seule", "seulement", "si", "sien", "sienne","siennes", "siens", "sinon", "six", "sixième", "soi", "soi-même", "soient", "sois", "soit", "soixante",
                 "sommes", "son", "sont", "sous", "souvent", "soyez", "soyons", "specifique", "specifiques","speculatif", "stop", "strictement", "subtiles", "suffisant", "suffisante", "suffit", "suis", "suit",
                 "suivant", "suivante", "suivantes", "suivants", "suivre", "sujet", "superpose", "sur", "surtout", "t","ta", "tac", "tandis", "tant", "tardive", "te", "tel", "telle", "tellement", "telles", "tels",
                 "tenant", "tend", "tenir", "tente", "tes", "tic", "tien", "tienne", "tiennes", "tiens", "toc", "toi","toi-même", "ton", "touchant", "toujours", "tous", "tout", "toute", "toutefois", "toutes", "treize",
                 "trente", "tres", "trois", "troisième", "troisièmement", "trop", "très", "tsoin", "tsouin", "tu", "té","u", "un", "une", "unes", "uniformement", "unique", "uniques", "uns", "v", "va", "vais", "valeur",
                 "vas", "vers", "via", "vif", "vifs", "vingt", "vivat", "vive", "vives", "vlan", "voici", "voie","voient", "voilà", "voire", "vont", "vos", "votre", "vous", "vous-mêmes", "vu", "vé", "vôtre",
                 "vôtres", "w", "x", "y", "z", "zut", "à", "â", "ça", "ès", "étaient", "étais", "était", "étant","état", "étiez", "étions", "été", "étée", "étées", "étés", "êtes", "être", "ô", "the", "-", ".", "!",
                 "'", 'in', 'B',"+","1","2","3","4","5","6","7","8","9","10","cc","Cc","CC","Faire","faire","dr","M.","m","m.","Mme","mme","mme.","28","12","pute","putain","salope","con","conasse"]

    counts = Counter(text.split(" "))
    counts = sorted(counts.items(), key=lambda x: -x[1])

    text_list = set()
    i = 0
    while len(text_list) < 40 or i < len(counts):
        if counts[i][0] not in stopwords:
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


if __name__ == '__main__':
    app.run_server(debug=True)