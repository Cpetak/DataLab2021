import plotly.express as px
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np

import pandas as pd
from urllib.request import urlopen
import json
from collections import defaultdict

url = "https://github.com/Cpetak/DataLab2021/blob/main/TaskForce1/CountyData.tsv" # Make sure the url is the raw version of the file on GitHub
df = pd.read_html(url)
df=df[0]
data = df.replace('No Data', None)
data = data.replace('#N/A', None)
data.head()

url="https://raw.githubusercontent.com/Cpetak/DataLab2021/main/county_network.csv"
net = pd.read_csv(url, error_bad_lines=False)

net_map=defaultdict(list)

for indx, row in net.iterrows():
    net_map[row.County_A].append(row.County_B)

data['net']= data['County'].map(net_map)

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

data['id'] = data['id'].map(lambda x: f'{x:0>5}')

import dash

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("US map"),
    dcc.Graph(id='graph'),
    html.Label([
        "Look at migration FROM",
        dcc.Dropdown(
            id='colorscale-dropdown', clearable=False,
            value='None', options=[
                {'label': c, 'value': c}
                for c in list(data.County.unique()) + ["None"]
            ]),
        "income",
        dcc.Slider(
            id='income-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            ),
        "education",
        dcc.Slider(
            id='education-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            ),
        "unemployment",
        dcc.Slider(
            id='unemployment-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            ),
        "life",
        dcc.Slider(
            id='life-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            ),
        "disability",
        dcc.Slider(
            id='disability-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            ),
        "obesity",
        dcc.Slider(
            id='obesity-slider',
            min=0,
            max=1,
            value=0.5,
            step=0.1
            )
    ])
])# Define callback to update graph

@app.callback(
    Output('graph', 'figure' ),
    [Input("colorscale-dropdown", "value"), Input('income-slider', 'value'),Input('education-slider', 'value'),Input('unemployment-slider', 'value'),Input('life-slider', 'value'),Input('disability-slider', 'value'),Input('obesity-slider', 'value')]
)
def update_figure(colorscale, income_slider, education_slider, unemployment_slider, life_slider, disability_slider, obesity_slider):
    weight_income = income_slider
    weight_education = education_slider
    weight_unemployment = unemployment_slider
    weight_life  = life_slider
    weight_disability = disability_slider
    weight_obesity = obesity_slider
    

    weighted_data = (1/6)*(weight_income*((data['income'].map(float)).rank(ascending=False)) \
                  + weight_education*((data['education'].map(float)).rank(ascending=False)) \
                  + weight_unemployment*((data['unemployment'].map(float)).rank(ascending=True)) \
                  + weight_life*((data['life'].map(float)).rank(ascending=False)) \
                  + weight_disability*((data['disability'].map(float)).rank(ascending=True)) \
                  + weight_obesity*((data['obesity'].map(float)).rank(ascending=True)))


    data["wrank"]=weighted_data
    data["col"]=0
    
    
    if colorscale != "None":
        
        conn=data[data["County"]==colorscale].net.to_numpy()

        for c in conn[0]:
            data.loc[(data.County == c),'col']=1
        
        return px.choropleth(data,geojson=counties,locations='id',color='col', 
                             scope='usa',
                             color_continuous_scale="Viridis",
                             hover_data=["wrank","County"],
                             labels={'wrank':'weighted rank'})
    
    return px.choropleth(data,geojson=counties,locations='id',color='wrank', 
                         scope='usa',
                         color_continuous_scale="Viridis",
                         hover_data=["wrank","County"],
                         labels={'wrank':'weighted rank'})

if __name__ == "__main__":
    app.run_server(debug=True)
