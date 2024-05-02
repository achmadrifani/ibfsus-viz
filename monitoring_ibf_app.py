import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
import pandas as pd
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container

#Test
st.set_page_config(layout="wide", page_title="SUS - IBF Visualization Platform", page_icon="🌧️")
DATA_DIR = "data"
FILE_NAME_LATEST = "SUS_IBF_latest.json"

def load_latest_data():
    data = gpd.read_file(f"{DATA_DIR}/{FILE_NAME_LATEST}")
    data.loc[:, "effective"] = pd.to_datetime(data["effective"], unit="ms")
    data.loc[:, "sent"] = pd.to_datetime(data["sent"], unit="ms")
    data = data.loc[data["layer"] == "rainfall_risk"]
    return data


def make_popup(row):
    popup_content = f'''
    <div style="background-color:{row['fill']}; padding:10px; border-radius:5px;">
<h3>Rainfall Risk Level {row['value']}</h3>
<b>Effective at</b> {row['effective']}<br>
<b>Impacted Area</b>: {row['area_desc']}
</div>'''
    return folium.Popup(popup_content,max_width=300,max_height=200)


def make_map(data):
    poly = folium.FeatureGroup(name='Rainfall Risk')
    for i, row in data.iterrows():
        coords = [(lat, lon) for lon, lat in row.geometry.exterior.coords]
        polygon = folium.Polygon(coords,
                                 fill_color=row['fill'],
                                 fill_opacity=0.7,
                                 color=None,
                                 weight=0).add_to(poly)
        popup_content = make_popup(row)
        polygon.add_child(popup_content)
    return poly


def nextf():
    if st.session_state["slider"] < timelist[-1]:
        st.session_state.slider += (timelist[1] - timelist[0])
    else:
        pass
    return


def prevf():
    if st.session_state["slider"] > timelist[0]:
        st.session_state.slider -= (timelist[1] - timelist[0])
    else:
        pass
    return


# def main():
st.title("SUS - IBF Visualization Platform")
data = load_latest_data()
with stylable_container(
    key="data-update",
    css_styles=["""
    {position: absolute;
    top: 680px;
    left: 30px;
    z-index: 5;}""",]):
    st.write(f"Latest data update: {data['sent'].max().strftime('%d %b %Y %H:%M') } UTC")
timelist = sorted(data["effective"].unique())

with stylable_container(
    key="select-time",
    css_styles=["""
    {background-color: #f4f4f4;
    padding: 10px;
    position: absolute;
    top:710px;
    width: 100%;
    z-index:5;
    box-sizing:none;}""",]):
    valid_date = st.select_slider("Select Time", options=timelist, key="slider", format_func=lambda x: x.strftime("%d %b"))

cols = st.columns([.1,.1,.8],gap='small')
with stylable_container(
    key="button-prev",
    css_styles=["""
    button {
        background-color: #f4f4f4;
        color: #333;
        border: 1px solid #333;
        padding: 5px;
        margin: 5px;
        position: absolute;
        left: 20px;
        top: 490px;
        z-index: 5;}""",
        """
    button:hover {
        background-color: #ff8300;
        color: #f4f4f4;
        border: 1px solid #333;
        border-radius: 50px;
        padding: 5px;
        margin: 5px;}"""]):
    st.button("Previous", on_click=prevf, key="prev")

with stylable_container(
        key="button-next",
        css_styles=["""
    button {
        background-color: #f4f4f4;
        color: #333;
        border: 1px solid #333;
        padding: 5px;
        margin: 5px;
        position: absolute;
        left: 100px;
        top: 475px;
        z-index: 5;}""",
        """
    button:hover {
        background-color: #ff8300;
        color: #f4f4f4;
        border: 1px solid #333;
        border-radius: 50px;
        padding: 5px;
        margin: 5px;}"""]):
    st.button("Next", on_click=nextf, key="next")

with stylable_container(
        key="button-refresh",
        css_styles=["""
    button {
        background-color: #f4f4f4;
        color: #333;
        border: 1px solid #333;
        padding: 5px;
        margin: 5px;
        position: absolute;
        left: 20px;
        top: 410px;
        z-index: 5;}""",
        """
    button:hover {
        background-color: #ff8300;
        color: #f4f4f4;
        border: 1px solid #333;
        border-radius: 50px;
        padding: 5px;
        margin: 5px;}"""]):
    st.button("Refresh Data", on_click=load_latest_data, key="refresh")

if valid_date.day not in st.session_state:
    st.session_state[f"data_{valid_date.day}"] = data.loc[data["effective"].dt.day == valid_date.day]

if f"map_{valid_date.day}" not in st.session_state:
    st.session_state[f"map_{valid_date.day}"] = make_map(st.session_state[f"data_{valid_date.day}"])

m = folium.Map(location=[-2.5, 120], zoom_start=5, zoom_on_click=True)
folium.plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)
with stylable_container(
    key="map_container",
    css_styles=["""
    {position: absolute;
    top:100px;
    z-index:1;}""",]
):
    st_folium(m,feature_group_to_add=[st.session_state[f"map_{valid_date.day}"]],use_container_width=True, key="map_container")


# if __name__ == "__main__":
#     main()
