# Import required libraries
import os
import copy
import pandas as pd
from flask import Flask
from flask_cors import CORS
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from controls import STATES, HEALTH_MEASURES


app = dash.Dash(__name__)

df = pd.read_csv('500_Cities.csv') 

# Filter data frame by row values
df = df[(df.StateAbbr != 'US') & (df.Data_Value_Type  \
         == 'Crude prevalence') & (df.GeographicLevel == 'City') \
        & (df.MeasureId != 'COREM') & (df.MeasureId != 'COREW')]

# Filter data frame by column names
df = df.filter(items = ['Year', 'StateAbbr', 'StateDesc', 'CityName', 
                        'Category', 'Data_Value', 'Low_Confidence_Limit', 
                        'High_Confidence_Limit', 'PopulationCount', 
                        'GeoLocation', 'CategoryID', 'MeasureId'])

df = df.dropna()

# Create a data frame that only contains one measure
single_measure = df[df.MeasureId == 'ARTHRITIS']
single_measure = single_measure.dropna()

# Extract longitute and latitute data from data frame
df['location'] = df['GeoLocation'].str.replace('(', '')
df['location'] = df['location'].str.replace(')', '')
df['location'] = df['location'].str.replace(' ', '')
df['lat'], df['lon'] = df['location'].str.split(',').str

health_measure_options = [{'label': str(HEALTH_MEASURES[health_measures]),
                          'value': str(health_measures)}
                          for health_measures in HEALTH_MEASURES]

states = [{'label': str(STATES[state]),
          'value': str(state)}
          for state in STATES]


# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    '500 Cities Project: Data for Better Health'
                ),
                html.Br([]),
                html.Br([]),
                html.H2(
                    'Health Measures from Individual Cities'
                )
            ],
            className='row'
        ),
        html.H3('Select a city:'),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id='state_selector1',
                            options=states,
                            multi=False,
                            value='AL',
                        )
                    ],
                    className='two columns',
                    ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id='city_selector',
                            multi=False,
                            value='Birmingham',
                        )
                    ],
                    className='two columns',
                    ),
            ],
            className='row'
        ),
        html.Div(
            [
               dcc.Graph(id='bar')
            ],
            className='row'
        ),
        html.Div(
            [
                html.Br([]),
                html.H2('Health Measures Across Cities')
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3('Filter by state:'),
                        dcc.Dropdown(
                            id='state_selector',
                            options=states,
                            multi=True,
                            value=list(STATES.keys()),
                        ),
                    ],
                    className='seven columns'
                ),
                html.Div(
                    [   
                        html.H3('Select a health status measure'),
                        dcc.Checklist(
                            id='measure_type_selector',
                            options=[
                                {'label': 'Prevention ', 
                                 'value': 'prevention'},
                                {'label': 'Health outcomes ', 
                                 'value': 'outcomes'},
                                {'label': 'Unhealthy Behaviors ', 
                                 'value': 'behaviors'}
                            ],
                            values=['prevention', 'outcomes', 'behaviors'], 
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.P('\n\n\n'),
                        dcc.Dropdown(
                            id='health_measure_selector',
                            multi=False,
                            value='ACCESS2'
                        )

                    ],
                    className='five columns'
                ),
            ],
            className='row'
        ),
        html.Div(
            [   
                html.Div(
                    [   
                        html.H3('Select value range:'),
                        dcc.RangeSlider(
                            id='slider',
                            max=100,
                            min=0,
                            step=0.1,
                            value=[0, 100]
                        ),
                        html.P(
                            '',
                            id='range_text',
                        ),
                        html.Br([]),
                        html.H3('Sort:'),
                        dcc.RadioItems(
                            id = 'sorting',
                            options=[
                                     {'label': 'low to high', 'value': 'asc'},
                                     {'label': 'high to low', 'value': 'des'}],
                                     value='asc',
                            labelStyle={'display': 'inline-block'}
                        ),
                        
                    ],
                    className='two columns',
                    style={'margin-top': '40'}
                ),
                html.Div(
                    [dcc.Graph(id='table')],
                    className='five columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='hist')
                    ],
                    className='five columns',
                    style={'margin-top': '10'}
                )
                
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='map')
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        html.Br([]),
                        html.H4(
                            '',
                            id='population_text',
                        ),
                        html.Br([]),
                        dcc.Graph(id='pie_chart')
                    ],
                    className='four columns',
                    style={'margin-top': '20'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Br([]),
                html.H2('Correlations Between Health Measures')
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3('Select a health status measure'),
                        dcc.Checklist(
                            id='measure_type_selector2',
                            options=[
                                {'label': 'Prevention ', 
                                 'value': 'prevention'},
                                {'label': 'Health outcomes ', 
                                 'value': 'outcomes'},
                                {'label': 'Unhealthy Behaviors ', 
                                 'value': 'behaviors'}
                            ],
                            values=['prevention', 'outcomes', 'behaviors'], 
                            labelStyle={'display': 'inline-block'}
                        ),
                        dcc.Dropdown(
                            id='health_measure_selector2',
                            multi=False,
                            value='ACCESS2'
                            )
                        ],
                    className='five columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        html.H3('Select a health status measure'),
                        dcc.Checklist(
                            id='measure_type_selector3',
                            options=[
                                {'label': 'Prevention ', 
                                 'value': 'prevention'},
                                {'label': 'Health outcomes ', 
                                 'value': 'outcomes'},
                                {'label': 'Unhealthy Behaviors ', 
                                 'value': 'behaviors'}
                            ],
                            values=['prevention', 'outcomes', 'behaviors'], 
                            labelStyle={'display': 'inline-block'}
                        ),
                        dcc.Dropdown(
                            id='health_measure_selector3',
                            multi=False,
                            value='COPD'
                            )
                    ],
                    className='five columns',
                    style={'margin-top': '10'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                dcc.Graph(id='scatter_plot')
            ],
            className='row',

        ),
# new code on single year data
        html.Div(
            [
                html.Br([]),
                html.H2('Single Year Data')
            ],
            className='row'
        ),
        html.Div(
            [
            html.Div(
                [
                html.Div(
                    [
                        html.H3('Select a year:'),
                        dcc.Slider(
                            id="year-slider",
                            min=df.Year.min(),
                            max=df.Year.max(),
                            value=df.Year.min(), 
                            marks={int(df.Year.min()):str(df.Year.min()), int(df.Year.max()):str(df.Year.max())}
                        )
                    ],
                    className='seven columns'
                ),
                html.Div(
                    [
                        html.H3('Select an health measure:'),
                        dcc.Dropdown(
                            id="health_measure_options_single_year",
                        )
                    ],
                    className='five columns'
                )
                ],
                className='row'
            ),
            html.Div(
                [
                   dcc.Graph(id='single-year-hist')
                ],
                className='row'
            ),
        ]
        ),

# end new code

        html.Br([]),
        html.Br([]),
        html.A('Source: Centers for Disease Control and Prevention', href='https://www.cdc.gov/500cities/index.htm'),
        html.Br([]),
        html.Br([]),
    ],
    className='ten columns offset-by-one'
)


# Helper function to filter the dataframe
def filter_dataframe(df, health_measure, states):
    dff = df[(df['MeasureId'] == str(health_measure)) & (df['StateAbbr'].isin(states))]
    return dff


# state dropdown menu -> city dropdown menu
@app.callback(Output('city_selector', 'options'),
              [Input('state_selector1', 'value')])
def update_city(selector):
    try:
        dff = single_measure[single_measure.StateAbbr==selector]
    except ValueError:
        pass

    cities = sorted(dff['CityName'].tolist())
    city_options = [{'label': str(city),
          'value': str(city)}
          for city in cities]
    return city_options


# city dropdown menu -> bar chart
@app.callback(Output('bar', 'figure'),
              [Input('city_selector', 'value')])
def make_bar(selector):
    dff = df[df.CityName==selector]
    trace = go.Bar(
        x=[HEALTH_MEASURES[measure] for measure in dff['MeasureId'].tolist()],
        y=dff['Data_Value'].tolist(),
        marker=dict(
        color='#33115E'
        )
    )
    layout_bar = go.Layout(
        autosize=True,
        height=600,
        xaxis=dict(tickangle=-45, automargin=True),
        title='All Health Measures of '+ selector + \
               ', ' + dff['StateDesc'].tolist()[0] + ' (% of population)')

    fig = go.Figure(data=[trace], layout=layout_bar)
    return fig

# first checkbox -> measure dropdown menu
@app.callback(Output('health_measure_selector', 'options'),
              [Input('measure_type_selector', 'values')])
def update_measure_options1(selector):
    ls = []
    # If the checkbox for each one category is checked, dropdown menu 
    # should includes all measure of the type
    if 'prevention' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ACCESS2', 'BPMED', \
                                            'CHECKUP', 'CHOLSCREEN', \
                                            'COLON_SCREEN', 'DENTAL', \
                                            'MAMMOUSE', 'PAPTEST']])
    if 'outcomes' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ARTHRITIS', 'BPHIGH', 'CANCER', 
                    'CASTHMA', 'CHD', 'COPD', 'DIABETES', 'HIGHCHOL', 
                    'KIDNEY', 'MHLTH', 'PHLTH', 'STROKE', 'TEETHLOST']])
    
    if 'behaviors' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['BINGE', 'CSMOKING', \
                    'LPA', 'OBESITY', 'SLEEP']])

    return ls

# multiple state dropdown menu and measure dropdown menu -> histogram
@app.callback(Output('hist', 'figure'),
              [Input('health_measure_selector', 'value'),
               Input('state_selector', 'value')])
def make_hist(health_measure, states):
    dff = filter_dataframe(df, health_measure, states)
    trace = go.Histogram(
        x = dff.Data_Value,
        histnorm='percent',
        marker=dict(
            color='#7B62AB',
            ))
    layout = go.Layout(
        autosize=True,
        height=400,
        margin=dict(
            l=30,
            r=0,
        ),
        title=('Distribution of Percentages of Population with<br>' + 
            HEALTH_MEASURES[health_measure]),
        xaxis=dict(
            title='Value'
        ),
        yaxis=dict(
            title='Count'
        )
    )
    fig = go.Figure(data=[trace], layout=layout)
    return fig

# range slider -> range text
@app.callback(Output('range_text', 'children'),
              [Input('slider', 'value')])
def update_slider_text(slider):
    return 'You selected ' + str(slider[0]) + '% - ' + str(slider[1]) + '%' 

# range slider + sorting radio items -> table
@app.callback(Output('table', 'figure'),
              [Input('health_measure_selector', 'value'),
               Input('state_selector', 'value'),
               Input('slider', 'value'),
               Input('sorting', 'value')])
def make_table(health_measure, states, data_range, sorting):
    # Filter data frame by health measure, states, and value range
    dff = filter_dataframe(df, health_measure, states)
    dff = dff[(dff['Data_Value']>=data_range[0]) & (dff['Data_Value']<=data_range[1])]
    
    if (sorting == 'asc'):
        dff = dff.sort_values(by=['Data_Value'])
    else:
        dff = dff.sort_values(by=['Data_Value'], ascending=False)

    trace = go.Table(
        # Set different column widths
        columnorder = [1, 2, 3, 4, 5, 6],
        columnwidth = [50, 130, 55, 85, 90, 90],
        header = dict(values=['Rank', 'City', 'State', 'Value', \
                              'High Confidence Limit', 'Low Confidence Limit'],
                      align=['left'] * 5),
        cells = dict(values=[[i for i in range(1, dff.shape[0]+1)],  
                             dff.CityName, dff.StateAbbr, \
                             dff.Data_Value.map('{:,.1f}'.format), \
                             dff.High_Confidence_Limit.map('{:,.1f}'.format), \
                             dff.Low_Confidence_Limit.map('{:,.1f}'.format)],
                     align=['left'] * 5))
    layout = dict(
        title='Cities Ranked by Percentage of Population with<br>'+ HEALTH_MEASURES[health_measure],
        autosize=True,
        height=350,
        margin=dict(
        l=10,
        r=35,
        b=35,
        )
    )
    data = [trace]
    fig = dict(data=data, layout=layout)
    return fig


# Selectors -> map
@app.callback(Output('map', 'figure'),
              [Input('health_measure_selector', 'value'),
               Input('state_selector', 'value')],
              [State('map', 'relayoutData')])
def make_map(health_measure, states, map_layout):
    
    dff = filter_dataframe(df, health_measure, states)
    quintile = dff.Data_Value.quantile([0.2, 0.4, 0.6, 0.8])
    
    # Get quintile thresholds of the selected cities
    data_quintile = [(dff.Data_Value.min(), quintile.iloc[0]), 
                     (quintile.iloc[0], quintile.iloc[1]), 
                     (quintile.iloc[1], quintile.iloc[2]), 
                     (quintile.iloc[2], quintile.iloc[3]), 
                     (quintile.iloc[3], dff.Data_Value.max()+0.1)]

    cities = []
    scale = 5000
    colors = ["rgb(190,168,224)","rgb(128,96,171)","rgb(88,54,133)",
              "rgb(54,23,94)","rgb(30,0,66)"]
    
    for i in range(len(data_quintile)):
        data = data_quintile[i]
        df_sub = dff[(dff['Data_Value'] >= data[0]) & (dff['Data_Value'] < data[1])]
        city = dict(
            type='scattergeo',
            locationmode='USA-states',
            lon=df_sub['lon'],
            lat=df_sub['lat'],
            customdata=df_sub['CityName'],
            text=df_sub['CityName'] + ' ,' + df_sub['StateAbbr'] + '<br>',
            hoverinfo='text+name',
            hoverlabel=dict(namelength=-1),
            marker = dict(
                          size = df_sub['PopulationCount']/scale,
                          color = colors[i],
                          sizemode = 'area'
                          ),
            name = str(i*20) + ' - ' + str((i+1)*20) + ' percentile'
        )
        cities.append(city)

    map_layout = dict(
        autosize=True,
        height=550,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=35,
            pad=10
        ),
        title = ('Distribution of Population with ' + \
                 HEALTH_MEASURES[health_measure] + 
                 '<br>(colored by percentile rank, sized by population count)'),
        showlegend = True,
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = 'rgb(217, 217, 217)',
            subunitwidth=1,
            countrywidth=1,
            subunitcolor="rgb(255, 255, 255)",
            countrycolor="rgb(255, 255, 255)"
        ),
        legend=dict(
            font=dict(size=10), 
            orientation='h',
            x=0.5,
            xanchor='center',
        )
    )

    figure = dict(data=cities, layout=map_layout)
    return figure

# map -> text
@app.callback(Output('population_text', 'children'),
              [Input('health_measure_selector', 'value'),
               Input('state_selector', 'value'),
               Input('map', 'hoverData')])
def make_text(health_measure, states, map_hover):
    dff = filter_dataframe(df, health_measure, states)
    # When user has not hovered on any point, show the overall numbers
    if map_hover is not None:
        city = map_hover['points'][0]['customdata']
        dff = dff[dff['CityName']==city]
        try:
            state = dff.StateDesc.tolist()[0]
            pop = int(dff.PopulationCount.tolist()[0])
            total = int(dff.Data_Value.tolist()[0] * pop / 100)
            return ('In ' + city + ', ' + state + ', ' + '{:,d}'.format(total) + 
                    ' thousand of ' + '{:,d}'.format(pop) + 
                    ' thousand people have or experience ' + 
                    HEALTH_MEASURES[health_measure].lower())
        # In case all states are filtered out
        except IndexError:
            return ''
    else:
        total = int((dff.PopulationCount * dff.Data_Value).sum()/100)
        pop = int(dff.PopulationCount.sum())
        return ('Of all cities selected, ' + '{:,d}'.format(total) + \
                ' thousand of ' + '{:,d}'.format(pop) + \
                ' thousand people have or experience ' + \
                HEALTH_MEASURES[health_measure].lower())

# map -> pie
@app.callback(Output('pie_chart', 'figure'),
              [Input('health_measure_selector', 'value'),
               Input('state_selector', 'value'),
               Input('map', 'hoverData')])
def make_pie(health_measure, states, map_hover):
    dff = filter_dataframe(df, health_measure, states)
    # When user has not hovered on any poinnt, show the overall average
    if map_hover is not None:
        city = map_hover['points'][0]['customdata']
        dff = dff[dff['CityName']==city]
        # In case user filters out all the states
        try:
            state = dff.StateDesc.tolist()[0]
            percentage = dff.Data_Value.tolist()[0]
            values = [percentage/100, 1-(percentage/100)]
        except IndexError:
            values = [0, 1]
    else:
        # To prevent divide by 0 error
        if not dff.PopulationCount.sum() == 0:
            average = (dff.PopulationCount * dff.Data_Value).sum() / dff.PopulationCount.sum()
            values = [average/100, 1-(average/100)]
        else: 
            values = [0, 1]
    
    data = go.Pie(
        values=values,
        labels=[HEALTH_MEASURES[health_measure], ''],
        marker=dict(colors=['#25064C', '#CCCCCC']),
        hoverinfo='label',
        hole=0.5
    )
    layout_pie = go.Layout(
        autosize=True,
        height=300,
        showlegend=False,
        margin=dict(
            l=20,
            r=10,
            t=50)
    )
    figure = dict(data=[data], layout=layout_pie)
    return figure

#Checkbox 2 -> drop down menu 2
@app.callback(Output('health_measure_selector2', 'options'),
              [Input('measure_type_selector2', 'values'),
               Input('health_measure_selector3', 'value')])
def update_measure_options2(selector, yaxis):
    ls = []
    # If the checkbox for each one category is checked, dropdown menu 
    # should includes all measure of the type
    if 'prevention' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ACCESS2', 'BPMED', \
                                            'CHECKUP', 'CHOLSCREEN', \
                                            'COLON_SCREEN', 'DENTAL', \
                                            'MAMMOUSE', 'PAPTEST']])
    if 'outcomes' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ARTHRITIS', 'BPHIGH', 'CANCER', 
                    'CASTHMA', 'CHD', 'COPD', 'DIABETES', 'HIGHCHOL', 
                    'KIDNEY', 'MHLTH', 'PHLTH', 'STROKE', 'TEETHLOST']])
    
    if 'behaviors' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['BINGE', 'CSMOKING', \
                    'LPA', 'OBESITY', 'SLEEP']])
    
    # if one measure is selected for the other axis, it cannot be selected
    # for this axis
    for i in ls:
        if i['value'] == yaxis:
            i['disabled'] = True
    return ls


# checkbox3 + measure selector2 -> measure selector3
@app.callback(Output('health_measure_selector3', 'options'),
              [Input('measure_type_selector3', 'values'),
               Input('health_measure_selector2', 'value')])
def update_measure_options3(selector, xaxis):
    ls = []
    # If the checkbox for each one category is checked, dropdown menu 
    # should includes all measure of the type
    if 'prevention' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ACCESS2', 'BPMED', \
                                            'CHECKUP', 'CHOLSCREEN', \
                                            'COLON_SCREEN', 'DENTAL', \
                                            'MAMMOUSE', 'PAPTEST']])
    if 'outcomes' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['ARTHRITIS', 'BPHIGH', 'CANCER', 
                    'CASTHMA', 'CHD', 'COPD', 'DIABETES', 'HIGHCHOL', 
                    'KIDNEY', 'MHLTH', 'PHLTH', 'STROKE', 'TEETHLOST']])
   
    if 'behaviors' in selector:
        ls.extend([{'label': str(HEALTH_MEASURES[health_measures]),
                    'value': str(health_measures)}
                    for health_measures in ['BINGE', 'CSMOKING', \
                    'LPA', 'OBESITY', 'SLEEP']])
    
    # if one measure is selected for the other axis, it cannot be selected
    # for this axis
    for i in ls:
        if i['value'] == str(xaxis):
            i['disabled'] = True
    return ls

# measure selector 2 + 3 -> scatter plot
@app.callback(Output('scatter_plot', 'figure'),
              [Input('health_measure_selector2', 'value'),
               Input('health_measure_selector3', 'value')])
def make_scatter(xaxis, yaxis):
    dff = df.filter(items = ['CityName', 'StateAbbr', 'Data_Value', 'MeasureId'])
    # Concatinate city and state strings
    dff['CitySt'] =  dff['CityName']+ ', ' + dff['StateAbbr'].map(str)
    # Reshape table into wide format
    dff = dff.pivot_table(index = 'CitySt', columns='MeasureId', values='Data_Value')
    trace = go.Scatter(
        x = dff[xaxis],
        y = dff[yaxis],
        mode = 'markers',
        marker = dict(
            size= 14,
            color='#35165E',
            line= dict(width=1,color='#25064C'),
            opacity= 0.3
        ),
        text = dff.index.values 
        ) 

    layout = go.Layout(
        height = 650,
        hovermode= 'closest',
        xaxis= dict(
            title= HEALTH_MEASURES[xaxis],
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= HEALTH_MEASURES[yaxis],
            ticklen= 5,
            gridwidth= 2,
        ),
        showlegend= False
    )

    fig = go.Figure(data=[trace], layout=layout)
    return fig

# filter health measures to just those from particular year
@app.callback(Output('health_measure_options_single_year', 'options'),
              [Input('year-slider', 'value')])
def update_measure_options_single_year(selector):
    try:
        dff = df[df.Year==selector]
        print(dff.columns)
    except ValueError:
        pass

    measures = sorted(dff['MeasureId'].unique().tolist())
    health_measure_options_single_year = [{'label': str(measure),
          'value': str(measure)}
          for measure in measures]
    return health_measure_options_single_year

# multiple state dropdown menu and measure dropdown menu -> histogram
@app.callback(Output('single-year-hist', 'figure'),
              [Input('health_measure_options_single_year', 'value')])
def make_hist(health_measure):
    dff = df[(df['MeasureId'] == str(health_measure))]
    trace = go.Histogram(
        x = dff.Data_Value,
        histnorm='percent',
        marker=dict(
            color='#7B62AB',
            ))
    layout = go.Layout(
        autosize=True,
        height=400,
        margin=dict(
            l=30,
            r=0,
        ),
        title=('Distribution of Percentages of Population with<br>' + 
            HEALTH_MEASURES[health_measure]),
        xaxis=dict(
            title='Value'
        ),
        yaxis=dict(
            title='Count'
        )
    )
    fig = go.Figure(data=[trace], layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)