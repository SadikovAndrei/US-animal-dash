#!/usr/bin/env python
# coding: utf-8




#!pip install  pandas geopandas requests 

import pandas as pd
import geopandas as gpd
import requests
import re

#source - from here you should extract the shp file:
#source= 'https://ecos.fws.gov/ecp/report/table/critical-habitat.html#:~:text=A-,zip%20file,-containing%20two%20shapefiles' 
shape_file = '/Users/andrei/Downloads/crithab_all_layers/crithab_poly.shp' #This is the link to the chape file

gdf = gpd.read_file(shape_file)

gdf.drop(columns=['unit', 'subunit', 'unitname', 'subunitnam','coopoffice', 'coopofmore', 'fedreg', 'effectdate',
       'vacatedate', 'accuracy','spcode', 'vipcode','leadoffice','source_id','objectid'],inplace = True)
#Excluding some values that either don't have picture or don't have a correct habitat
values_to_exclude = ['Chelonia mydas', 'Etheostoma phytophilum', 'Corvus kubaryi', 'Lepidomeda vittata', 'Catostomus warnerensis', 'Charadrius nivosus nivosus', 'Rana muscosa','Zosterops rotensis']

gdf = gdf[~gdf['sciname'].isin(values_to_exclude)]
#dropping  duplicate values
gdf.drop_duplicates(subset=None, keep='first', inplace=True)

list_names = gdf['sciname'].to_list()
# Using wikipedia API retrieving image links
url_img_list = []
for i,row in enumerate(list_names):
    page_title = list_names[i]

    url = 'https://en.wikipedia.org/w/api.php'
    params = {
    'action': 'query',
    'format': 'json',
    'redirects': '1',
    'titles': page_title
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Check if there are redirects
    if 'redirects' in data['query']:
        page_title = redirected_title = data['query']['redirects'][0]['to']

        url = 'https://en.wikipedia.org/w/api.php'
        params = {
        'action': 'query',
        'format': 'json',
        'prop': 'pageimages',
        'piprop': 'original',
        'titles': page_title
        }
        response = requests.get(url, params=params)
        data = response.json()

        page_id = list(data['query']['pages'].keys())[0]
        image_url = data['query']['pages'][page_id].get('original', {}).get('source', None)

        url_img_list.append(image_url)
    elif 'redirects' not in data['query']:
        page_id = list(data['query']['pages'].keys())[0]
        image_url = data['query']['pages'][page_id].get('original', {}).get('source', None)
        url_img_list.append(image_url)

gdf['url_img'] = url_img_list

gdf = gdf[gdf['url_img'].notnull()]

#Creating an intersection table with states
#set here the path to geojson with states file
states_file = '/Users/andrei/Desktop/DATA ANALISYS/us animals/us_states.json'
states_gdf = gpd.read_file(states_file)
df1 = gdf[['entity_id','sciname','geometry',]]
intersection_gdf = gpd.sjoin(df1, states_gdf, how="inner", predicate='intersects')
#intersection_gdf = intersection_gdf[['sciname','NAME','SHORT','CENSUSAREA']]
#intersection_gdf.rename(columns={'name':'State'},inplace=True)

intersection_gdf.reset_index(inplace=True)
intersection_gdf.drop(columns=['index','geometry','GEO_ID','index_right','LSAD'], inplace=True)
intersection_gdf.drop_duplicates(subset=None, keep='first', inplace=True)

gdf.drop(columns=['singlmulti','status'], inplace=True)

output_geojson_filepath = '/Users/andrei/Desktop/DATA ANALISYS/us animals/shape/main.shp'

gdf.to_file(output_geojson_filepath, driver='ESRI Shapefile')


output_file_path = '/Users/andrei/Desktop/DATA ANALISYS/us animals/intersection.csv'

# Save the DataFrame to a csv file
intersection_gdf.to_csv(output_file_path)

descr_list = []

for i, page_title in enumerate(list_names):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'redirects': '1',
        'titles': page_title,
        'prop': 'extracts',
        'explaintext': True,
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Check if there are redirects
    if 'redirects' in data['query']:
        page_title = data['query']['redirects'][0]['to']
        params['titles'] = page_title
        response = requests.get(url, params=params)
        data = response.json()

    page_id = list(data['query']['pages'].keys())[0]
    extract = data['query']['pages'][page_id].get('extract', None)

    if extract:
        descr_list.append(extract)
    else:
        descr_list.append("Description not found")

descr_list


species_info = []
for i, el in enumerate(descr_list):
    input_text = descr_list[i]
    description_text = re.search(r'\n== Description ==\n(.*?)\n', input_text, re.DOTALL)
    if description_text:
        description_text = description_text.group(1)
        species_info.append(description_text)
    else:
        description_text = None
        species_info.append(description_text)
species_info



gdf_desc = gdf[['sciname']]
gdf_desc['description'] = species_info
gdf_desc


output_file_path = '/Users/andrei/Desktop/DATA ANALISYS/us animals/species_info.csv'

# Save the DataFrame to a csv file
gdf_desc.to_csv(output_file_path)

