
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# 📁 Carregar dados
df = pd.read_excel('/content/drive/MyDrive/dados/enderecos_geocodificados_final.xlsx')
df = df.dropna(subset=['latitude', 'longitude'])

gdf_combinado = gpd.read_file('/content/drive/MyDrive/dados/camada_bairro_subdistrito.shp')
centro = gdf_combinado.geometry.centroid.unary_union.centroid

# 🧭 Filtros
tipo = st.selectbox("Tipo", ["Todos"] + sorted(df['tipo'].dropna().unique()))
bairro = st.selectbox("Bairro", ["Todos"] + sorted(df['bairro'].dropna().unique()))

# 🧮 Filtrar dados
dados_filtrados = df.copy()
if tipo != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['tipo'] == tipo]
if bairro != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['bairro'] == bairro]

# 📊 Estatísticas
st.write("Estatísticas gerais", dados_filtrados.describe())

# 🗺️ Mapa
mapa = folium.Map(location=[centro.y, centro.x], zoom_start=13)
for _, row in dados_filtrados.iterrows():
    popup_text = (
        f"{row['nome']}<br>"
        f"R$ {row['preco']:.2f}<br>"
        f"{row['tipo']}, {row['quartos']} Q / {row['banheiros']} B"
    )
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color='#2E8B57',
        fill=True,
        fill_color='#2E8B57',
        fill_opacity=0.85,
        popup=popup_text
    ).add_to(mapa)

folium_static(mapa)
