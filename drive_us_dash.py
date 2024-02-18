#!/usr/bin/env python
# coding: utf-8

# In[8]:


from shapely.geometry import Polygon
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import no_update
import pandas as pd
import geopandas as gpd
import gdown
import os
import random




font = 'Trebuchet MS, sans-serif'
bgcolor = '#F9F8F6'
import requests

file_ids = ['1_d1DzAb7Eg7utCI3rstFa4T-fKT3SQye', '18MTFH6VjoSlWlVXGXqflWH6nk_8dilCy', '1-0y68l604Vep1L8FFYU_fwCVjbOE_yU_']
urls = [f'https://drive.google.com/uc?id={file_id}&export=download' for file_id in file_ids]
output_files = ['file.shp', 'file.shx', 'file.dbf']

for url, output_file in zip(urls, output_files):
    response = requests.get(url)
    if response.status_code == 200:
        # If the request is successful, write the content to a file
        with open(output_file, 'wb') as f:
            f.write(response.content)

gdf = gpd.read_file('file.shp')


file_id = '118Y2JXdJECplLMH82lLNFoG-N0WW_HBw'
url = f'https://drive.google.com/uc?id={file_id}'
output_file = 'data.csv'
gdown.download(url, output_file, quiet=False)
intersection_gdf = pd.read_csv(output_file)


file_id = '1ULYmNUEBTTM8-2OYIDqQvvkX5FnazDE-'
url = f'https://drive.google.com/uc?id={file_id}'
output_file = 'info.csv'
gdown.download(url, output_file, quiet=False)
info_df = pd.read_csv(output_file)





list_names = sorted(list(gdf.sciname.unique()))
value = list_names[0]

random_value = random.choice(list_names)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor': bgcolor},children=[html.H1('Some endangered species of USA',
                                        style={'textAlign': 'center',
                                               'color': '#503D36',
                                               'font-size': 40,
                                              'font-family': font}),
                                html.P(),
                                
                                dcc.Dropdown(list_names,
                                             value=random_value,
                                             id='dropdown-statistics',
                                             placeholder='Select an endangeremnt grade',
                                             style={'width': '100%', 'padding': '3px',
                                                    'font-size': '20px', 'text-align': 'center',
                                                    'font-family': font,
                                                   'borderRadius': '10px'}
                                            ),

                                #html.Div(id='output-container', className='chart-grid', style={'display': 'flex'}),
                                html.Div(id='output-container'),
                            
                                
                                html.Div(children=[
                                html.Div(id='image-container', style={'flex': '1','textAlign': 'center'}),
                                html.Div(children =[
                                        html.Div(id='name-container',style={'marginLeft': '10px', 'textAlign': 'center',
                                               'color': '#503D36',
                                               'font-size': 50,
                                              'font-family': font}),
                                        html.Div(id='status-container'),
                                        html.Div(id='info-container',style={'marginLeft': '10px', 'textAlign': 'center',
                                               'color': '#503D36',
                                               'font-size': 20,
                                              'font-family': font})],style={#'backgroundColor': 'white','borderRadius': '20px',
                                                                            'flex': '1'})
                                        ],style={'display': 'flex','alignItems': 'center', 'justifyContent': 'center'})
                                
                                               
                    ])

@app.callback(
    Output(component_id='output-container', component_property='children'),
    Output(component_id='image-container', component_property='children'),
    Output(component_id='status-container', component_property='children'),
    Output(component_id='name-container', component_property='children'),
    Output(component_id='info-container', component_property='children'),
    
    Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(value):
    
    
    
    df1 = gdf[gdf['sciname'] == value]
    
    poly = df1['geometry']
    poly = poly.iloc[0]  # Access the first polygon
    centroid = poly.centroid
    centroid_x, centroid_y = centroid.y, centroid.x  # Reversed for correct lat-lon assignment
    center = {"lat": centroid_x, "lon": centroid_y}
    if poly.area >= 500:
        zoom = 0
    elif poly.area >= 50 and poly.area < 500:
        zoom = 1
    elif poly.area >= 5 and poly.area < 50:
        zoom = 3
    elif poly.area >= 0.5 and poly.area < 5:
        zoom = 4
    elif poly.area >= 0.05 and poly.area < 0.5:
        zoom = 6
    elif poly.area >= 0.005 and poly.area < 0.05:
        zoom = 7
    elif poly.area >= 0.001 and poly.area < 0.005:
        zoom = 8
    elif poly.area >= 0.0005 and poly.area < 0.001:
        zoom = 9
    elif poly.area >= 0.0001 and poly.area < 0.0005:
        zoom = 10
    elif poly.area >= 0.00005 and poly.area < 0.0001:
        zoom = 11
    elif poly.area >= 0.00001 and poly.area < 0.00005:
        zoom = 12
    elif poly.area >= 0.000005 and poly.area < 0.00001:
        zoom = 13
    elif poly.area >= 0.000001 and poly.area < 0.000005:
        zoom = 14
    elif poly.area >= 0.0000005 and poly.area < 0.000001:
        zoom = 15
    elif poly.area < 0.0000005:
        zoom = 16


    fig1 = px.choropleth_mapbox(df1,
                            geojson=df1.geometry,
                            locations=df1.index,  # Assuming the index contains location identifiers
                            color=df1.comname,  # Replace 'your_column' with the column name containing the color data
                            color_continuous_scale='RdBu',
                            mapbox_style="carto-positron",
                            zoom=zoom,
                            center=center,
                            opacity=0.5)
    fig1.update_layout(plot_bgcolor=bgcolor,paper_bgcolor=bgcolor)
    fig1.update_traces(hovertemplate=df1.comname)

    fig1.update_layout(#title_text='Species Areal',
                       #legend_title_text="Species name",
                      showlegend=False,
                      plot_bgcolor='#F7C50C')
    fig1.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),)
    df2 = intersection_gdf[intersection_gdf['sciname']==value]
    states_list = df2['SHORT'].to_list()
    if 'PR' in states_list:
        fig2 = px.choropleth(
        locationmode="country names",  
        locations=["Puerto Rico"],
        color=[1],
        scope="world",
        #title="Choropleth Map of Puerto Rico",
        )
        fig2.update_geos(projection_scale=6,center=center)
        fig2.update_layout(coloraxis_showscale=False,geo_bgcolor=bgcolor)
        fig2.update_layout(margin=dict(l=5, r=5, t=5, b=5),)
        fig2.update_layout(geo=dict(showframe=False))
        fig2.update_traces(marker_opacity=0.5)
        fig2.update_layout(plot_bgcolor=bgcolor,paper_bgcolor=bgcolor)
        fig2.update_layout(
            #autosize=False,
            #width=600,
            height=400)
        fig2.update_traces(hovertemplate=df2.NAME)
    else:
        fig2 = px.choropleth(df2,locations=df2['SHORT'], locationmode="USA-states", color=df2.SHORT, scope="usa")
        fig2.update_layout(
            #showlegend=False,
            geo_bgcolor=bgcolor)
        fig2.update_layout(margin=dict(l=5, r=5, t=5, b=5),)
        fig2.update_traces(marker_opacity=0.5)
        fig2.update_layout(plot_bgcolor=bgcolor,paper_bgcolor=bgcolor
                           #,height=400
                          )
        fig2.update_traces(hovertemplate=df2.NAME)
    
    div1 = html.Div(children = [html.Div(dcc.Graph(figure=fig1),style={'flex': '1'}),html.Div(dcc.Graph(figure=fig2),style={'flex': '1'})],style={'display': 'flex'})

    
    image_url = gdf.loc[gdf['sciname'] == value, 'url_img'].values[0]
    if image_url is not None:
        image1 = html.Div(children=[html.Img(style={'height':'400px','borderRadius': '20px','marginLeft': '20px'},alt=value,src=image_url)])
    else:
        image1 = html.Div(children=[html.Img(style={'width':'40%'},alt=value,src='https://upload.wikimedia.org/wikipedia/en/thumb/e/ec/IUCN_Red_List.svg/440px-IUCN_Red_List.svg.png')])
    st = list(df1['listing_st'])[0]
    status = html.Div(st,style={'textAlign': 'center',
                                               'color': '#7d192a',
                                               'font-size': 45,'font-family': font})
    name = gdf.loc[gdf['sciname'] == value, 'comname'].values[0]
    if name == 'No common name':
        name = gdf.loc[gdf['sciname'] == value, 'sciname'].values[0]
    else:
        name
    
    df3 = info_df[info_df['sciname'] == value]
    animal_info = list(df3['description'])[0]
    
    return div1,  image1,status,name, animal_info


    
    




# Run the application                   
if __name__ == '__main__':
    app.run_server(port=8001)


# In[ ]:




