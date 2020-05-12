#!/usr/bin/env python
# coding: utf-8

# In[14]:


import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#%matplotlib inline
#import folium
#from IPython.display import IFrame
#import base64

import geopandas as gpd
import json
from bokeh.io import show, output_notebook
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter, 
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, FactorRange, Legend)
from bokeh.layouts import column, row, widgetbox
from bokeh.palettes import brewer
from bokeh.palettes import viridis
from bokeh.plotting import figure

from bokeh.plotting import ColumnDataSource, figure, output_notebook, show


# In[15]:


df3 = pd.read_csv("data_population.csv") #Trond fyrer den
df4 = pd.read_csv("Demographic_Data.csv") #https://www.kaggle.com/muonneutrino/us-census-demographic-data#acs2017_census_tract_data.csv


# In[16]:


#Finding the population for each state
State_pop = df4.groupby('State')['TotalPop'].sum()


# In[17]:


#Merging the population to df4
df4 = df4.merge(State_pop, on=['State'], how='left')


# In[18]:


#Finding the population ratio for each county
df4['Pop_ratio']=df4['TotalPop_x']/df4['TotalPop_y']


# In[19]:


#Removing the total state population
df4 = df4.drop(['TotalPop_y'], axis=1)


# In[20]:


#Defining the columns that needs to be normalized with state ratio
ratio_columns = ['Hispanic','White', 'Black', 'Native', 'Asian', 'Pacific',
       'Income', 'Poverty', 'ChildPoverty', 'Professional', 'Service', 'Office', 'Construction',
       'Production', 'Drive', 'Carpool', 'Transit', 'Walk', 'OtherTransp',
       'WorkAtHome', 'MeanCommute', 'Employed', 'PrivateWork', 'PublicWork',
       'SelfEmployed', 'FamilyWork', 'Unemployment']


# In[21]:


#Normalizing the columns
df5=pd.DataFrame(df4['State'])
for column in df4[ratio_columns]:
    df5[column] = df4[column]*df4['Pop_ratio']


# In[22]:


#merging the normalized columns with df4
df4 = df4[['TotalPop_x','Men','Women']]
df4 = pd.concat([df4, df5], axis=1)


# In[23]:


#finding all info for each state
df4 = df4.groupby('State').sum()


# In[24]:


#merging dataset 4 and 3
df3 = df3.set_index('State')
df4 = df4.merge(df3,on=['State'], how='left')
df_state = df4
df_state = df_state.reset_index()
df_state = df_state.loc[~df_state.State.isin(['Alaska', 'Hawaii', 'Puerto Rico'])]
df_state = df_state.reset_index(drop=True)


# In[25]:


#safe plots
#for i in range(len(df_state.index)):
#    fig = plt.figure(figsize=(9, 3))
#    plt.bar(df_state.iloc[i,4:10].sort_values(ascending=False).index, df_state.iloc[i,4:10].sort_values(ascending=False))
#    plt.savefig("Pics/hist" + str(i) + ".png")
#    plt.close(fig)


# In[26]:


# Read in shapefile
contiguous_usa = gpd.read_file('cb_2018_us_state_20m/cb_2018_us_state_20m.shp')
contiguous_usa = contiguous_usa.sort_values(by=['NAME'])


# In[27]:


contiguous_usa.rename(columns = {'NAME':'State'}, inplace = True)                                 
pop_states = contiguous_usa.merge(df_state, on=['State'], how='left')
pop_states = pop_states.loc[~pop_states['State'].isin(['Alaska', 'Hawaii','Puerto Rico'])]


# In[28]:


imgshist=[]
for i in range(len(df_state.index)):
    imgshist = np.append(imgshist,"Pics/hist" + str(i) + ".png")

pop_states['imgshist'] = imgshist


# In[29]:


# set up output file as first thing
#output_notebook()

def get_geodatasource(pop_states):    
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(pop_states.to_json()))
    return GeoJSONDataSource(geojson = json_data)


# In[30]:


geosource = get_geodatasource(pop_states)


# In[31]:


TOOLTIPS = """
    <div>
        <div>
            <img
                src="@imgshist" height="500" alt="@imgshist" width="500"
                border="1"
            ></img>
        </div>
    </div>
"""


# In[32]:


# Create figure object.
palette = brewer['OrRd'][8]
palette = palette[::-1]
vals = pop_states['Density']
color_mapper = LinearColorMapper(palette = palette, low = vals.min(), high = vals.max())

p = figure(title = 'State Data', 
           plot_height = 600 ,
           plot_width = 950, 
           toolbar_location = 'below',
           tools = "pan, wheel_zoom, box_zoom, reset")
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
# Add patch renderer to figure.
states = p.patches('xs','ys', source = geosource,
                   fill_color={'field': 'Density', 'transform': color_mapper},
                   line_color = "black", 
                   line_width = 0.5, 
                   fill_alpha = 1)
# Create hover tool
p.add_tools(HoverTool(renderers = [states],
                      tooltips = [('State','@State'),
                                  ('Income','@Income{int}'),
                                  ('Density','@Density{int}'),
                                  ('',TOOLTIPS)]))
#show(p)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




