#!/usr/bin/env python
# coding: utf-8

# # BayWheel Bike Data Visualziation

# In[103]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import math
import datetime
import json
get_ipython().run_line_magic('matplotlib', 'inline')


# In[85]:


import os
import conda

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib


# In[86]:


import matplotlib.cm
 
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize


# In[2]:


# import all the csv files
files = ['201801-fordgobike-tripdata.csv', '201802-fordgobike-tripdata.csv',
        '201803-fordgobike-tripdata.csv','201804-fordgobike-tripdata.csv',
        '201805-fordgobike-tripdata.csv','201806-fordgobike-tripdata.csv',
        '201807-fordgobike-tripdata.csv','201808-fordgobike-tripdata.csv',
        '201809-fordgobike-tripdata.csv','201810-fordgobike-tripdata.csv',
        '201811-fordgobike-tripdata.csv','201812-fordgobike-tripdata.csv']


# In[3]:


# loop through the file directory, append each file to the dataframe then reset the index 
df = pd.DataFrame()
for file in files:
    if df.empty:
        df = pd.read_csv(file)
    else:
        new_df = pd.read_csv(file)
        df = pd.concat([df, new_df], ignore_index=True)
df.reset_index()


# In[4]:


df.shape


# In[5]:


df.columns


# In[6]:


df.bike_share_for_all_trip.value_counts()


# In[7]:


# derive the time duration in terms of minute and hour from duration_sec
df['duration_min'] = df['duration_sec'].apply(lambda d: d/60).astype(float)
df['duration_hr'] = df['duration_min'].apply(lambda d: d/60).astype(float)


# In[8]:


# round to 2 decimals 
df['duration_min'] = df['duration_min'].apply(lambda x: round(x, 2))
df['duration_hr'] = df['duration_hr'].apply(lambda x: round(x, 2))


# In[9]:


# derive the age from members' birth year
df['member_age'] = df['member_birth_year'].apply(lambda b:0 if pd.isnull(b) else 2019-b).astype(int)


# In[10]:


# make a copy of the data frame for further exploration
dfc = df.copy()


# In[11]:


# convert end_time column to datetime type
dfc['end_time'] = pd.to_datetime(dfc['end_time'])


# In[12]:


# extract month, date, day, and hour from the end_time column utilizing the datetime library
dfc['month'] = dfc['end_time'].apply(lambda time: time.strftime("%B"))
dfc['date'] = dfc['end_time'].apply(lambda time: time.strftime("%d"))
dfc['day'] = dfc['end_time'].apply(lambda time: time.strftime("%A"))
dfc['hour'] = dfc['end_time'].apply(lambda time: time.strftime("%H"))


# In[13]:


# assign a certain day to weekday/weekend
def assign_weektime(day):
    weekdays = ['Monday','Tuesday', 'Wednesday','Thursday','Friday']
    weekend = ['Saturday', 'Sunday']
    if day in weekdays:
        return "Weekday"
    else:
        return "Weekend"


# In[14]:


dfc['timeofweek'] = dfc['day'].apply(lambda day: assign_weektime(day))


# In[15]:


dfc.timeofweek.value_counts()


# In[16]:


dfc['hour'] = dfc['hour'].astype(int)


# In[17]:


# assign a specific time period of the day (morning, afternoon, evening)
def assign_dayperiod(hour):
    if (hour >= 4 and hour <= 12):
        return "Morning"
    elif (hour > 12 and hour <= 18):
        return "Afternoon"
    else:
        return "Evening"


# In[18]:


dfc['dayperiod'] = dfc['hour'].apply(lambda hour: assign_dayperiod(hour))


# In[19]:


dfc.sample(5)


# In[20]:


# assign age group to the users
def assign_agegroup(age):
    if (age >= 0 and age <=10):
        return "Children"
    elif (age > 10 and age <=20):
        return "Teen"
    elif (age > 20 and age <=35):
        return "Young Adult"
    elif (age > 35 and age <=55):
        return "Adult"
    else:
        return "Senior"


# In[21]:


dfc['member_age_group'] = dfc['member_age'].apply(lambda age: assign_agegroup(age))


# In[22]:


dfc.member_age_group.value_counts()


# ### Average Trip Duration by Age Group

# In[197]:


age_order = ['Children', 'Teen', 'Young Adult', 'Adult', 'Senior']
age_range = [0, 10, 20, 35, 55, 120]


# In[293]:


sb.boxplot(data=dfc, x="member_age_group", y="duration_min", color=base_color, order=age_order)
plt.ylim(0,100)


# In[294]:


dfc_byAge = dfc.loc[dfc.member_age != 0].reset_index()


# In[295]:


# bin_edges = np.arange(0, dfc['member_age'].max() + 10, 10)
# bin_idxs = pd.cut(dfc['member_age'], bin_edges, right=False, include_lowest=False).astype(int)
bin_idxs = pd.cut(dfc_byAge['member_age'], age_range, labels=age_order)


# In[296]:


dfc_byAge.head()


# Last but not least, since a lot of the plots will have number of data rows (i.e., count of trips) as the y axis, let's develop a mechanism to display the trip counts in thousands (K) so it looks cleaner.

# In[578]:


def format_ride_count(count):
    if (count == 0):
        return "0"
    elif (len(str(count)) <=3):
        return str(count)
    else:
        return "{:,}".format(int(count/1000)) + "K"


# In[582]:


# test format function 
format_ride_count(3334334)


# ### Q1: When does people usually like to bike?

# First of all, we'd like to figure out when people like to bike around in different metrics. That'd be useful to build a pattern that would help better distributing the bikes based on demand of different time periods.

# We'll start off by weekday/weekend.

# In[606]:


plt.figure(figsize=[8,8])
timeofweek_counts = dfc.timeofweek.value_counts()
plt.pie(timeofweek_counts, labels=timeofweek_counts.index, startangle=90, autopct=lambda val: val.round(2));
plt.axis('square');


# Apparently, the majority of the bikes ride on the weekday. Do they bike to commute or just for fun? Maybe taking a look at the day period (morning/afternoon/evening) distribution would help us determine.

# In[566]:


plt.figure(figsize = [12, 10])
dayperiod_order = ['Morning', 'Afternoon', 'Evening']
sb.countplot(data=dfc, x="dayperiod", color=base_color, order=dayperiod_order);
y_ticks_props = np.arange(0, dfc.groupby('dayperiod').bike_id.count().max()+1, 100000);
y_ticks_display = [ format_ride_count(numRide) for numRide in y_ticks_props]
plt.yticks(y_ticks_props, y_ticks_display);
plt.ylabel('Rides');
plt.title('Ride Distribution in Day Periods', pad=20);


# Maybe they do bike for commuting as the majority of rides takes place during morning and afternoon. To confirm, let's dive deep and take a look at the hourly distribution.

# In[585]:


plt.figure(figsize = [12, 10])
hour_order = np.arange(0, 24, 1)
sb.countplot(data=dfc, x="hour", color=base_color, order=hour_order);
y_ticks_props = np.arange(0, dfc.groupby('hour').bike_id.count().max()+1, 50000);
y_ticks_display = [ format_ride_count(numRide) for numRide in y_ticks_props]
plt.xticks(np.arange(0, 24+1, 3), np.arange(0, 24+1, 3));
plt.yticks(y_ticks_props, y_ticks_display);
plt.ylabel('Rides');
plt.title('Hourly Ride Distribution');


# It might actually be the case. As we can see from the bar chart, the peak traffic is around 7-9 (morning commute) and 16-18 (afternoon commute(). There's a consistent traffic in between the two peaks, and after 7pm traffic starts to go down.

# Now let's examine the data set from the month's perspective. In which month do people bike the most? Let's find out by building a barplot based on month.

# In[621]:


plt.figure(figsize = [10, 10])
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
sb.countplot(data=dfc, y="month", color=base_color, order=month_order);
plt.xlabel('Rides');
x_ticks_props = np.arange(0, dfc.month.value_counts().max()+1, 50000);
x_ticks_display = [ format_ride_count(numRide) for numRide in x_ticks_props]
plt.xticks(x_ticks_props, x_ticks_display);
plt.title('Monthly Ride Distribution');


# To better display the month labels, I've set the barplot to be horizontal. Here we could see that apparently people like to bike in summer and fall - especially in the months from May to October. It makes sense because the weather during that those seasons are more ideal for biking.

# Now that we've examined the data from a chronological standpoint, let's switch gears and try to play around with demographic attributes. Nos vamos!

# ### Q2: Who likes to ride a bike the most?

# We would like to start off with some usual univariate analysis. Let's take a look at the age group - do older people prefer to bike than the younger people? 

# In[622]:


plt.figure(figsize = [10, 10])
age_order = ['Children', 'Teen', 'Young Adult', 'Adult', 'Senior']
sb.countplot(data=dfc, y="member_age_group", color=base_color, order=age_order);
x_ticks_props_age = np.arange(0, dfc['member_age_group'].value_counts().max()+1, 250000);
x_ticks_display_age = [ format_ride_count(numRide) for numRide in x_ticks_props_age]
plt.xticks(x_ticks_props_age, x_ticks_display_age);
plt.xlabel('rides');
plt.ylabel('age group');
plt.title('Ride Distribution among Age Aroups');
x_ticks_display_age


# This categorization might be a bit general. What if we break down the age by range of 10?

# In[332]:


bin_edges = np.arange(0, dfc.member_age.max(), 10)
dfc['age_by_10'] = pd.cut(dfc.member_age, bin_edges, right=False)


# In[327]:


bin_edges.shape


# In[624]:


# todo: convert xtick label to "start_age - end_age", e.g., 10-20 instead of [10, 20]
plt.figure(figsize=[15,10])
sb.countplot(data=dfc, y="age_by_10", color=base_color);
x_ticks_props = np.arange(0, dfc['age_by_10'].value_counts().max()+1, 100000);
x_ticks_display = [ format_ride_count(numRide) for numRide in x_ticks_props]
plt.xticks(x_ticks_props, x_ticks_display);
plt.xlabel('rides');
plt.ylabel('age');
plt.title('Ride Distribution among Age Aroups, range of 10');


# As we could see from above, most riders fall into the range of 20-50, which makes sense. Let's now try a bivariate visualization. What's the relationship between trip duration and age group? For the sake of simplicity, we'll use the duration in minute as our metric.

# In[340]:


plt.figure(figsize = [20, 10])
plt.subplot(1, 2, 1)
ax1 = sb.violinplot(data=dfc, x="member_age_group", y="duration_min", color=base_color, order=age_order)
plt.ylim(0, 50);
plt.ylabel("Duration (min)")

plt.subplot(1, 2, 2)
ax2 = sb.boxplot(data=dfc, x="member_age_group", y="duration_min", color=base_color, order=age_order)
plt.ylabel("Duration (min)");
plt.ylim(0, 50);


# As we could see, surprisingly children seem to have the longest duration. However as we recall for a lot the records that don't have a birth year, we simply assign their age to be 0. Let's clean it up and run the plots again. 

# In[343]:


dfc.query('member_age == 0').count()['bike_id']


# In[344]:


dfc_by_age = dfc.loc[dfc.member_age != 0]


# In[347]:


dfc_by_age.member_age_group.value_counts()


# In[496]:


plt.figure(figsize = [20, 10])
plt.subplot(1, 2, 1)
ax1 = sb.violinplot(data=dfc_by_age, x="member_age_group", y="duration_min", color=base_color, order=age_order[1:])
plt.ylim(0, 50);
plt.xlabel("Age Group", fontsize='x-small');
plt.ylabel("Duration (min)")

plt.subplot(1, 2, 2)
ax2 = sb.boxplot(data=dfc_by_age, x="member_age_group", y="duration_min", color=base_color, order=age_order[1:])
plt.xlabel("Age Group", fontsize='x-small');
plt.ylabel("Duration (min)");
plt.ylim(0, 50);


# Hmm, that makes a difference. Now the children group is completely gone - and teens take the lead among all age groups. Surprisingly, the seniors come nextm trailing by a small margin.

# Next, let's examine the distribution between user types (subscriber/customer)

# In[625]:


g = sb.FacetGrid(data=dfc, col="user_type");
sb.set(font_scale = 3)
g.fig.set_size_inches(20,10)
g.map(plt.hist, "duration_min", range=[0,40]);
g.set_titles('{col_name}', pad=20);
for ax in g.axes.flatten():
    ax.set_xlabel('Duration (min)');
y_ticks_props = np.arange(0, dfc.user_type.value_counts().max()+1, 100000);
y_ticks_display = [ format_ride_count(numRide) for numRide in y_ticks_props]
plt.yticks(y_ticks_props, y_ticks_display);


# As we could see, the majority of users are subscribers while just a small portion of users are occasional customers. For both groups, most data points fall into the range of 0-20 minutes. Nevertheless, the spread of subscribers is much greater than the customers, which is comparatively more even-out. For subscribers, the bulk of the data points of subscribers fall in 5-15 minutes.

# ### Q3: How about taking both time and age into consideration in terms of the trip duration?

# Let's try to draw a clustered bar plot to illustrate the impacts of day period (morning/afternoon/evening) and age on average trip duration.

# In[492]:


plt.figure(figsize = [24, 10])
ax = sb.barplot(data=dfc_by_age, x="member_age_group", y="duration_min", hue="dayperiod", order=age_order, palette="BuGn_r");
ax.legend(loc=3, framealpha=0.8)
plt.title("Relationship between Trip Duration and Daytime, Age", pad=20);
plt.xlabel("Age Group");
plt.ylabel("Trip Duration");


# We could also examine the relationship from a hourly perspective. Here we will draw a line chart of different age group's ride count in 24 hours.

# In[642]:


plt.figure(figsize = [15, 20])
dfc_by_age_sample = dfc_by_age.groupby(['member_age_group', 'hour']).bike_id.count().reset_index()
sb.lineplot(data=dfc_by_age_sample, x="hour", y="bike_id", hue="member_age_group")
y_ticks_props = np.arange(0, dfc_by_age.groupby(['member_age_group', 'hour']).bike_id.count().max()+1, 20000);
y_ticks_display = [format_ride_count(numRide) for numRide in y_ticks_props]
plt.yticks(y_ticks_props, y_ticks_display);
plt.ylabel("Rides");
plt.legend(loc=2, fontsize='xx-small')


# In[645]:


#todo: change the y_tick_props so that it's not hard-coded 
g = sb.FacetGrid(data=dfc_by_age, hue="member_age_group", height=12);
g.map(plt.hist, "hour", histtype="step");
plt.legend(fontsize='xx-small', loc=2);
plt.xticks(np.arange(0, 24+1, 3));
plt.ylabel("Number of Rides");
y_ticks_props = np.arange(0, 250000, 50000);
y_ticks_display = [ format_ride_count(numRide) for numRide in y_ticks_props]
plt.yticks(y_ticks_props, y_ticks_display);


# Wonderful! So through the line plot as well as the pseudo-histogram we can see that almost all the age groups share the same pattern in terms of hourly rides, with two peaks in the morning and late afternoon/early evening. For teens, the pattern is not so obvious but that's also because the sample size is smaller compared to the other groups.

# ### Q4: In which area does people bike the most?

# Notice that this visualization is more like a proof-of-concept experimentation. We wanted to figure out where (here we're primarily curious about the zip) people like to bike. We'll use Google's Geocoding API for computing the zip based on the latitude and longtitude extracted from a small sample of the dataframe (it's not feasible to do all of them because the Geocoding API is costly beyond a certain threshold), then visualize it on a map illustrating the most popular areas where people like to bike. 

# In[72]:


dfc_geo = dfc.sample(1500).reset_index()


# In[60]:


from pygeocoder import Geocoder


# In[61]:


API_KEY = 'AIzaSyC7wl1k4rxE_8cw0cVElpn8o0zxODkSV_0'


# In[73]:


for index, row in dfc_geo.iterrows():
    try:
        lat, lon = dfc_geo.loc[index, ['start_station_latitude', 'start_station_longitude']]
        start_loc = Geocoder(API_KEY).reverse_geocode(lat, lon)
        start_loc_zip = start_loc.postal_code
        dfc_geo.loc[index, 'zip'] = start_loc_zip
    except Exception as e:
        print('failed: index ', index, ' message: ', str(e))
        continue


# In[74]:


dfc_geo.zip.value_counts()


# In[107]:


# get a list of unique zips from the data frame for querying in the geojson data later 
ziplist = dfc_geo.zip.unique()


# In[76]:


# save the dataframe to CSV just in case 
dfc_geo.to_csv('geo_results.csv', index=False)


# In[222]:


# group trips by zip
dfc_geo_zip = dfc_geo.groupby('zip').bike_id.count().reset_index()


# In[228]:


dfc_geo_zip.rename(columns={"bike_id": "count"}, inplace=True)


# westlimit=-122.531598; southlimit=37.712724; eastlimit=-122.2194; northlimit=37.880205
# center: -122.531598,37.712724,-122.2194,37.880205

# In[123]:


import folium
import re


# In[112]:


# load GeoJSON
with open('sf_zip_geojson.json', 'r') as jsonFile:
    geo_data = json.load(jsonFile)
    
tmp = geo_data


# In[207]:


def create_feature_template(zip):
    feature = {
        "type": "Feature",
        "id": zip,
        "properties": {
            "zip": zip
          },
        "geometry": {
            "type": "Polygon",
            "coordinates": ""
        }
    }
    return feature


# In[249]:


def wrangle_coordinates(polygon):
    polygon = polygon[2:-2]
    coordinates_container = []
    coordinates = []
    pre_coordinates = polygon.split(',')
    for pre_coordinate in pre_coordinates:
        coordinate = []
        cors = pre_coordinate.strip().split(' ')
        coordinate.append(float(cors[0]))
        coordinate.append(float(cors[1]))
        coordinates.append(coordinate)
    coordinates_container.append(coordinates)
    return coordinates_container


# In[250]:


def populate_feature(shape, zip):
    new_feature = create_feature_template(zip)
    res = re.findall(r'\(\([^()]*\)\)', shape)
    if (len(res) == 1):
        container = wrangle_coordinates(res[0])
        new_feature['geometry']['coordinates'] = container
    else:
        new_feature['type'] = 'MultiPolygon'
        coordinate_container_multipolygon = []
        for polygon in res:
            coordinate_container_multipolygon.append(polygon)
    return new_feature


# In[210]:


# def populate_feature(shape, zip):
# #     for shape in matched_shapes[8:9]:
#     new_feature = create_feature_template(zip)
#     res = re.findall(r'\(\([^()]*\)\)', shape)
#     if (len(res) == 1):
#         polygon = res[0][2:-2]
#         coordinates_container = []
#         coordinates = []
#         pre_coordinates = polygon.split(',')
#         for pre_coordinate in pre_coordinates:
#             coordinate = []
#             cors = pre_coordinate.strip().split(' ')
#             coordinate.append(float(cors[0]))
#             coordinate.append(float(cors[1]))
#             coordinates.append(coordinate)
#         coordinates_container.append(coordinates)
#         new_feature['geometry']['coordinates'] = coordinates_container
#         return new_feature
#     else:
#         new_feature['type'] = 'MultiPolygon'
#         coordinate_container_multipolygon = []
#         for polygon in res:
            
    


# In[211]:


# matched_shapes = []
features = []
for row in tmp['data'][:100]:
    zip = row[-4]
    if (zip in ziplist):
        features.append(populate_feature(row[-5][14:-1], zip))
#           matched_shapes.append(row[-5][14:-1])


# In[212]:


features


# In[213]:


# creating new JSON object
new_json = dict.fromkeys(['type','features'])
new_json['type'] = 'FeatureCollection'
new_json['features'] = features
# save uodated JSON object
open("sf_geojson_cleaned.json", "w").write(json.dumps(new_json, sort_keys=True, indent=4, separators=(',', ': ')))


# In[248]:


SF_COORDINATES = (37.80, -122.30)
map = folium.Map(location=SF_COORDINATES, zoom_start=12)

map.choropleth(
        geo_data="sf_geojson_cleaned.json",
        name='choropleth',
        data=dfc_geo_zip,
        columns=['zip', 'count'],
        key_on='feature.properties.zip',
        fill_color='YlGn',
        fill_opacity=0.6,
        line_opacity=0.2,
        legend_name='trip count'
    )

display(map)


# In[ ]:




