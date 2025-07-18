# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_lottie import st_lottie
import altair as alt
import geopandas as gpd
from PIL import Image
import base64
from random import randrange
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# 
# import os
# current_dir = os.path.dirname(__file__)

# Page configuration
st.set_page_config(
    page_title="Indian EV Market",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")

# Setting Title
st.title(':car: India Ev Market Analysis')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Reading DataSet
df= pd.read_csv('ev_sales_by_makers_and_cat_15-24.csv')
df1=pd.read_csv('ev_cat_01-24.csv')
df3= pd.read_csv('OperationalPC.csv')
df4=pd.read_csv('EV Maker by Place.csv')

df3['State'] = df3['State'].replace("Odisha", "Orissa")
# Creating minidf
yearly_sales = df.iloc[:, 2:-1].sum()
minidf = pd.DataFrame(yearly_sales).reset_index()
minidf.columns = ['Year', 'Total Sales']

### Converting columns type 
df1['Date'] = df1['Date'].astype(str)
df1['Date'] = df1['Date'].replace('0', pd.NaT) 
df1['Date'] = pd.to_datetime(df1['Date'], format='%m/%d/%y', errors='coerce')

# Setting Page Logo
st.sidebar.image("voltvision.png")
# image_path = os.path.join(current_dir, "CarbonCoders.png")
# st.sidebar.image(image_path)
#Creating Side Bar
st.sidebar.header("Choose your filter: ")
# Create for State
State = st.sidebar.multiselect("Pick your State", df4["State"].unique())
if not State:
    df44=df4.copy()  
else:
    df44=df3[df3['State'].isin(State)]
# Create for Year 
Year = st.sidebar.multiselect("Pick your Year", minidf["Year"].unique())

# Creating Filter Logic
if not Year:
    minidf1=minidf.copy()  
else:
    minidf1=minidf[minidf['Year'].isin(Year)]
    
if not State:
    filter_data=df4
else:
    filter_data=df4[df4['State'].isin(State)]
    
if not Year:
    filter_Year=minidf
else:
    filter_Year=minidf[minidf['Year'].isin(Year)]

fd1=filter_data['State'].value_counts().reset_index()
fd1.columns = ['State', 'Number of company'] 
# Some Vizualisation 
col1, col2 = st.columns((2))    
with col1:
    st.subheader("Total Ev Sales By Year")
    fig = px.bar(filter_Year, x = 'Year', y = 'Total Sales', 
                  template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)
with col2:
    st.subheader("EV Plant State Wise")
    fig = px.pie(fd1, values = "Number of company", names = "State", hole = 0.5)
    fig.update_traces(text = fd1["State"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
 
with col1:
     with st.expander("Download Bar Charts Data"):
         st.write(filter_Year.style.background_gradient(cmap="Blues"))
         csv = filter_Year.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with col2:
     with st.expander("Download Pie Charts Data"):
         st.write(fd1.style.background_gradient(cmap="Oranges"))
         csv = fd1.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data", data = csv, file_name = "state.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file') 
         
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

# Some visualization         
df['Growth '] = ((df['2024'] - df['2015']) / df['2015']).replace([float('inf'), -float('inf')], 0) * 100
top_manufacturers_growth = df[['Maker', 'Growth ']].sort_values(by='Growth ', ascending=False).head(10)          
category_sales = df.groupby('Cat').sum()[['2015', '2016', '2017', '2018', '2019', '2020', '2021','2022', '2023', '2024']].reset_index()
category_sales = df.groupby('Cat').sum().loc[:, '2015':'2024']
category_sales_long = category_sales.reset_index().melt(id_vars='Cat', var_name='Year', value_name='Total Sales')
cat=category_sales_long.groupby('Cat')['Total Sales'].sum().reset_index() 
cat.columns=['Car Category','Total Sales']
chart1, chart2 = st.columns((2))

with chart1:
    st.subheader('Top 10 EV Manufacturers by Growth ')
    fig = px.bar(top_manufacturers_growth, x = 'Growth ', y = 'Maker', 
                 color_discrete_sequence=['#f4a24b'])
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.bar(cat, x = 'Car Category', y = 'Total Sales', 
                 color_discrete_sequence=['#4bf465'])
    st.plotly_chart(fig,use_container_width=True)

cl3, cl4 = st.columns((2))
with cl3:
    with st.expander("Download Bar Charts Data"):
        st.write(top_manufacturers_growth.style.background_gradient(cmap="Blues"))
        csv1 = top_manufacturers_growth.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv1, file_name="Category1.csv", mime="text/csv", key="unique_key_1")



with cl4:
    with st.expander("Download Bar Charts Data"):
        st.write(cat.style.background_gradient(cmap="Oranges"))
        csv2 = cat.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_2")
        
        
recent_sales = df[['Maker', '2021', '2022', '2023', '2024']]
recent_sales['Total Recent Sales'] = recent_sales[['2021', '2022', '2023', '2024']].sum(axis=1)
emerging_companies = recent_sales[recent_sales['Total Recent Sales'] > 1000]
emerging_companies_sorted = emerging_companies[['Maker', 'Total Recent Sales']].sort_values(by='Total Recent Sales', ascending=False).head(10)
# OLA Sales History
ola_history=df[df['Maker']=='OLA ELECTRIC TECHNOLOGIES PVT LTD']
ola_history.drop(columns=['Cat','Growth '],inplace=True)
ola_history_SUM= ola_history.iloc[:, 2:-1].sum()
minidf_OLA = pd.DataFrame(ola_history_SUM).reset_index()
minidf_OLA.columns = ['Years', 'Total Sales']

st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

cl5, cl6 = st.columns((2))
with cl5:
    st.subheader('Top 10 EV Manufacturers by Sales')
    fig = px.bar(emerging_companies_sorted , x = 'Total Recent Sales', y = 'Maker', 
                 color_discrete_sequence=['#ec4f37'])
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)
with cl6:
    st.subheader("OLA'S Exponential Growth History")
    fig = px.line(minidf_OLA, x = 'Years', y = 'Total Sales')
 #   fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)
       
with cl5:
    with st.expander("Download Bar Charts Data"):
        st.write(emerging_companies_sorted.style.background_gradient(cmap="Blues"))
        csv1 = emerging_companies_sorted.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv1, file_name="Category1.csv", mime="text/csv", key="unique_key_4")

with cl6:
    with st.expander("Download Line Plot Data"):
        st.write(minidf_OLA.style.background_gradient(cmap="Oranges"))
        csv2 = minidf_OLA.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_6")
        

# Vehicle Data Heatmap
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

st.markdown("<h3 style='text-align: center;'>Vehicle Data Heatmap</h3>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

coll1, coll2 = st.columns((2))
# Getting the min and max date 
startDate = pd.to_datetime(df1["Date"]).min()
endDate = pd.to_datetime(df1["Date"]).max()

# Making StartDate and end date columns
with coll1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with coll2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df1= df1[(df1['Date'] >= date1) & (df1['Date'] <= date2)].copy()      
# Heat Map
df_melted = df1.melt(id_vars=["Date"], var_name="Vehicle Type", value_name="Count")

# Create Plotly Heatmap
fig = px.imshow(
    df1.set_index("Date").T,
    labels=dict(x="Date", y="Vehicle Type", color="Count"),
    aspect="auto",
    color_continuous_scale="Cividis"
)

# Update layout
fig.update_layout(
 #   title="Vehicle Data Heatmap",
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Vehicle Type",
    coloraxis_colorbar=dict(title="Count")
)
fig.update_xaxes(showgrid=True, gridcolor='white', gridwidth=2)
fig.update_yaxes(showgrid=True, gridcolor='white', gridwidth=2)

st.plotly_chart(fig)

with st.expander("Download Hitmap Plot Data"):
        st.write(df1.style.background_gradient(cmap="Oranges"))
        csv2 = df1.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_8")

# get some geojson for India.  Reduce somplexity of geomtry to make it more efficient
url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
gdf = gpd.read_file(url)
gdf["geometry"] = gdf.to_crs(gdf.estimate_utm_crs()).simplify(1000).to_crs(gdf.crs)
india_states = gdf.rename(columns={"NAME_1": "ST_NM"}).__geo_interface__


# create base map of all India states
fig_choropleth = px.choropleth(
    pd.json_normalize(india_states["features"])["properties.ST_NM"],
    locations="properties.ST_NM",
    geojson=india_states,
    featureidkey="properties.ST_NM",
    color_discrete_sequence=["lightgrey"],
)

# Create the base map for all India states
fig = px.choropleth(
    df3,
    locations='State', 
    geojson=india_states,  
    featureidkey="properties.ST_NM",  
    color='No. of Operational PCS',  
    color_continuous_scale="Viridis", 
    hover_name="State",  
 #   title="No. of Operational PCS by State in India",
)

fig.update_layout(
    template="plotly_dark",
)

fig.update_geos(fitbounds="locations", visible=False)
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

st.markdown("<h3 style='text-align: center;'>Operational PCS in India by State</h3>", unsafe_allow_html=True)
st.plotly_chart(fig)  

cl7, cl8 = st.columns((2))

with cl7:
    with st.expander("Download Map Plot Data"):
        st.write(df3.style.background_gradient(cmap="Oranges"))
        csv2 = minidf_OLA.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_11")


# ev_makers
# Load Data from CSV
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('EV_Maker_with_Location.csv')
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()  # Returning empty DataFrame if error occurs
    
    # Necessary columns
    required_columns = ['EV Maker', 'Place', 'State', 'Latitude', 'Longitude']
    if not all(col in data.columns for col in required_columns):
        st.error("CSV file must contain columns: EV Maker, Place, State, Latitude, Longitude")
        return pd.DataFrame()  # Returning empty DataFrame if columns are missing
    
    # Converting Latitude and Longitude to numeric
    data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
    data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')

    # Dropping rows with missing values in Latitude or Longitude
    data = data.dropna(subset=['Latitude', 'Longitude'])
    
    return data

# Main Streamlit App
def main():
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
    st.markdown("<h3 style='text-align: center;'>Explore the Electric Vehicle Makers Location in India</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

    data = load_data()
    if data.empty:
        return  # Exit if data is not valid

    # Filter valid latitude and longitude ranges
    data = data[(data['Latitude'].between(-90, 90)) & (data['Longitude'].between(-180, 180))]

    # columns for filter options and map
    col1, col2 = st.columns([1, 2])  # Adjustment of proportions as needed

    with col1:
        # horizontal layout for the logo and header
        st.markdown("<h3 style='margin: 0;'>Filter Options</h3>", unsafe_allow_html=True)
        selected_maker = st.multiselect("Select EV Maker", options=data['EV Maker'].unique())
        selected_place = st.multiselect("Select Place", options=data['Place'].unique())
        selected_state = st.multiselect("Select State", options=data['State'].unique())

    # Filter data based on selections
    if selected_maker:
        data = data[data['EV Maker'].isin(selected_maker)]
    if selected_place:
        data = data[data['Place'].isin(selected_place)]
    if selected_state:
        data = data[data['State'].isin(selected_state)]

    # Create a Folium map centered around India
    india_map = folium.Map(location=[23.0, 82.0], zoom_start=4, tiles="CartoDB Positron")

    # Optional: Add custom boundaries (GeoJSON overlay)
    geojson_file = 'india_with_disputed_boundaries.geojson.geojson'  # Replace with the correct file path
    try:
        folium.GeoJson(
            geojson_file,
            name="Disputed Boundaries",
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'red',
                'weight': 2
            }
        ).add_to(india_map)
    except FileNotFoundError:
        st.warning("GeoJSON file for India's boundaries not found. Proceeding without it.")

    # Add data points to the map
    marker_cluster = MarkerCluster().add_to(india_map)

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['EV Maker']} at {row['Place']} ({row['State']})",
            tooltip=f"{row['EV Maker']} at {row['Place']}",
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)

    # Render the map in the second column
    with col2:
        st_folium(india_map, width=700, height=500)


# feedback form 
st.header(":mailbox: Get In Touch With EV News!")
contact_form = """

<form action="https://formsubmit.co/deekshith.mamidi19@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""
st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("./style.css")

# End 