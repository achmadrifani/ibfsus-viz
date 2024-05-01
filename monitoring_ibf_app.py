import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="SUS - IBF Visualization Platform", page_icon="🌧️")
DATA_DIR = "data"
FILE_NAME = "SUS_IBF_latest.json"

@st.cache_data
def load_data():
    data = gpd.read_file(f"{DATA_DIR}/{FILE_NAME}")
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
    return folium.Popup(popup_content,max_width=300)


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

def main():
    st.title("SUS - IBF Visualization Platform")
    data = load_data()
    st.write(f"### Latest data update: {data['sent'].max().strftime('%d %b %Y %H:%M') } UTC")
    timelist = sorted(data["effective"].unique())
    valid = st.select_slider("Select Time", options=[x.strftime("%d %b") for x in timelist])
    valid_date = datetime.strptime(valid, "%d %b").date()

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
    st_folium(m,feature_group_to_add=[st.session_state[f"map_{valid_date.day}"]],use_container_width=True)


if __name__ == "__main__":
    main()
