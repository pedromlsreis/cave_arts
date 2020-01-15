##################################################Imports###########################################################
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import datetime as dt

##################################### App setup for Heruko############################################################
app = dash.Dash(__name__)
server = app.server

######################################################Data##############################################################
#reading data
input_folder = "./input/"

data = pd.read_csv(input_folder+'africa-economic-banking-and-systemic-crisis-data.zip', compression='zip')

df = data.copy()



#data selections and data transformations
#selecting data since 1910.
df = df[df['year']>=1910].reset_index(drop=True)

#coverting string categoical values in banking_crisis to numerics
replace_values = {'no_crisis' : 0, 'crisis' : 1}
df = df.replace({"banking_crisis": replace_values}) 


#creating additional variables
df['text'] = '<b>' + df['country'] + '</b>' + '<br>' + \
    'Systemic Crisis ' + df['systemic_crisis'].astype(str) +'<br>' + \
    'Currency Crises ' + df['currency_crises'].astype(str) + '<br>' + \
    'Banking Crises ' + df['banking_crisis'].astype(str) + '<br>' + \
    'Inflation Crises ' + df['inflation_crises'].astype(str)

#just adding this     
df['total_crises'] = df[['systemic_crisis', 'currency_crises', 'inflation_crises', 'banking_crisis']].sum(axis=1)

#covert year to datetime 
#df['year'] = pd.to_datetime(df['year'])

crises = ['systemic_crisis', 'currency_crises', 'inflation_crises', 'banking_crisis']

indicators= ['exch_usd', 'gdp_weighted_default',
       'inflation_annual_cpi']

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['country'].unique()]

crises_options = [dict(label=crisis.replace('_', ' '), value=crisis) for crisis in crises]

indicators_options = [dict(label=indicator.replace('_', ' '), value=indicator) for indicator in indicators]

##################################################APP###############################################################

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.H1('African Financial Crisis Over the Years')
    ], className='Title'),

    html.Div([

        html.Div([
            html.Label('Country Choice'),
            dcc.Dropdown(
                id='country_drop',
                options=country_options,
                value=['Egypt'],
                multi=True
            ),

            html.Br(),

            html.Label('Crises'),
            dcc.Dropdown(
                id='crises_options',
                options=crises_options,
                value='systemic_crisis',
            ),

            html.Br(),

            html.Label('Indicator Choice'),
            dcc.Dropdown(
                id='indicators_options',
                options=indicators_options,
                value=['gdp_weighted_default', 'inflation_annual_cpi'],
                multi=True
            ),

            html.Br(),

            html.Label('Scroll to select a Year'),
            dcc.Slider(
                id='year',
                min= df['year'].min(),
                max= df['year'].max(),
                marks={str(i): '{}'.format(str(i)) for i in [1910, 1930, 1950, 1970, 
                                                               1990, 2014]},
                value=1955,
                step=1
            ),

            html.Br(),

            html.Label('Linear Log'),
            dcc.RadioItems(
                id='lin_log',
                options=[dict(label='Linear', value=0), dict(label='log', value=1)],
                value=0
            )

        ], className='column1 pretty'),

        html.Div([
            html.Div([
                    html.Label('Crises in the selected Country(s)')
                    ], className='h2'),

            html.Div([

                html.Div([html.Label(id='crisis_1')], className='mini pretty'),
                html.Div([html.Label(id='crisis_2')], className='mini pretty'),
                html.Div([html.Label(id='crisis_3')], className='mini pretty'),
                html.Div([html.Label(id='crisis_4')], className='mini pretty')

            ], className='4 containers row'),
            

            html.Div([dcc.Graph(id='bar_graph')], className='bar_plot pretty')

        ], className='column2')

    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='choropleth')], className='column3 pretty'),

        html.Div([dcc.Graph(id='aggregate_graph')], className='column3 pretty')

    ], className='row')

])

######################################################Callbacks#########################################################



@app.callback(
    [
         Output("choropleth", "figure"),   
         Output("bar_graph", "figure"),
         Output("aggregate_graph", "figure"),
    ],
    [
        Input("year", "value"),
        Input("country_drop", "value"),
        Input("crises_options", "value"),
        Input("lin_log", "value"),
        #Input("projection", "value"),

        Input("indicators_options", "value")
    ]
)
def plots(year, countries, crisis, scale, indicator):
        #############################################First Choropleth######################################################
    projection = 0 #equirectangular is preferred
    dff = df.loc[df['year'] == year]
    
    z = dff['total_crises']
    #z=''


    data_choropleth = dict(type='choropleth',
                           locations=dff['country'],
                           # There are three ways to 'merge' your data with the data pre embedded in the map
                           locationmode='country names',
                           z=z,
                           text=dff['text'],
                           colorscale='Reds',
                           colorbar=dict(title='# of Crises',
                                         tickmode = 'array',
                                         tickvals = [0, 1, 2, 3, 4, 5]),
                           hovertemplate='Country: %{text} <br>' + 'Total Crises' ': %{z}',
                           #hovertemplate='Country: %{text} <br>' + str(crisis.replace('_', ' ')) + ': %{z}',

                           )

    layout_choropleth = dict(geo=dict(scope='africa',  # default
                                      projection=dict(type=['equirectangular', 'orthographic'][projection]),
                                      landcolor='white',
                                      lakecolor='#1f77b4',
                                      showocean=True,  # default = False
                                      oceancolor='azure',
                                      bgcolor='#f9f9f9'
                                      ),

                             title=dict(text='Choropleth Map of Financial Crises by African countries on <b>' + str(year) +'</b>',
                                        x=.5  # Title relative position according to the xaxis, range (0,1)

                                        ),
                             paper_bgcolor='#f9f9f9'
                             )
                             

    ############################################second Bar Plot##########################################################
    data_bar = []
    for country in countries:
        df_bar = df.loc[(df['country'] == country)]

        x_bar = df_bar['year']
        y_bar = df_bar[crisis]

        data_bar.append(dict(type='bar', x=x_bar, y=y_bar, name=country))

    layout_bar = dict(title=dict(text='Historical Financial Crisis'),
                  yaxis=dict(title='Crises', type=['linear', 'log'][scale]),
                  paper_bgcolor='#f9f9f9'
                  )



    ############################################Third Scatter Plot######################################################

    df_loc = df.loc[df['country'].isin(countries)].groupby('year').mean().reset_index()

    data_agg = []

    
    for place in indicator:
        data_agg.append(dict(type='scatter',
                         x=df_loc['year'].unique(),
                         y=df_loc[place],
                         name=place.replace('_', ' ')
                         )
                    )

    layout_agg = dict(title=dict(text='Indicators'),
                     yaxis=dict(title=['S crisis', 'S crisis (log scaled)'][scale],
                                type=['linear', 'log'][scale]),
                     xaxis=dict(title='Year', rangeslider=dict(visible=True)),
                     paper_bgcolor='#f9f9f9'
                     )

    return go.Figure(data=data_bar, layout=layout_bar), \
           go.Figure(data=data_choropleth, layout=layout_choropleth),\
           go.Figure(data=data_agg, layout=layout_agg)


@app.callback(
    [
        Output("crisis_1", "children"),
        Output("crisis_2", "children"),
        Output("crisis_3", "children"),
        Output("crisis_4", "children"),
    ],
    [
        Input("country_drop", "value"),
        Input("year", "value"),
    ]
)
def indicator(countries, year):
    df_loc = df.loc[df['country'].isin(countries)].groupby('year').sum().reset_index()
    
    #years = list(range(year_slider[0], year_slider[1]+1))
    
    #for year in years:

        
    value_1 = round(df_loc.loc[df_loc['year'] == year][crises[0]].values[0], 2)
    value_2 = round(df_loc.loc[df_loc['year'] == year][crises[1]].values[0], 2)
    value_3 = round(df_loc.loc[df_loc['year'] == year][crises[2]].values[0], 2)
    value_4 = round(df_loc.loc[df_loc['year'] == year][crises[3]].values[0], 2)

    return str(crises[0]).replace('_', ' ') + ': ' + str(value_1),\
           str(crises[1]).replace('_', ' ') + ': ' + str(value_2), \
           str(crises[2]).replace('_', ' ') + ': ' + str(value_3), \
           str(crises[3]).replace('_', ' ') + ': ' + str(value_4)

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)