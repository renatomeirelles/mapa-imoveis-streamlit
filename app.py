import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

st.set_page_config(page_title="Mapa de Calor", layout="wide")

st.title("📍 Mapa de Calor de Imóveis")

# Simulação de dados (substitua pelo seu DataFrame real)
data = pd.DataFrame({
    'latitude': [-23.4205, -23.4210, -23.4195],
    'longitude': [-51.9331, -51.9340, -51.9320],
    'preco': [300000, 450000, 500000]
})

# Criar mapa base
mapa = folium.Map(
    location=[-23.4205, -51.9331],
    zoom_start=13,
    tiles='https://tile.jawg.io/jawg-matrix/{z}/{x}/{y}{r}.png?access-token=ZK6EgfhFT6px8F8MsRfOp2S5aUMPOvNr5CEEtLmjOYjHDC2MzgI0ZJ1cJjj0C98Y',
    attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
)

# Adicionar camada de calor
pontos = data[['latitude', 'longitude', 'preco']].values.tolist()
HeatMap(pontos, radius=15).add_to(mapa)

# Mostrar mapa no Streamlit
folium_static(mapa)
