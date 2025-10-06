import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import geopandas as gpd
from shapely.geometry import Point
from esda.moran import Moran_Local
from libpysal.weights import KNN
import numpy as np

st.set_page_config(page_title="Mapa de Imóveis", layout="wide")
st.title("📍 Mapa Interativo de Imóveis")

# 📥 Carregar dados
df = pd.read_csv("dados_imoveis.csv")
df = df.dropna(subset=['latitude', 'longitude'])

# 🎛️ Filtros interativos
tipo = st.selectbox("Tipo", ["Todos"] + sorted(df['tipo'].dropna().unique().tolist()))
bairro = st.selectbox("Bairro", ["Todos"] + sorted(df['bairro'].dropna().unique().tolist()))
anunciante = st.selectbox("Anunciante", ["Todos"] + sorted(df['Anunciante'].dropna().unique().tolist()))
quartos = st.slider("Quartos mínimos", 0, int(df['quartos'].max()), 0)
banheiros = st.slider("Banheiros mínimos", 0, int(df['banheiros'].max()), 0)
preco = st.slider("Faixa de preço (R$)", int(df['preco'].min()), int(df['preco'].max()), (int(df['preco'].min()), int(df['preco'].max())))

# 🔍 Aplicar filtros
dados = df.copy()
if tipo != "Todos":
    dados = dados[dados['tipo'] == tipo]
if bairro != "Todos":
    dados = dados[dados['bairro'] == bairro]
if anunciante != "Todos":
    dados = dados[dados['Anunciante'] == anunciante]
dados = dados[
    (dados['quartos'] >= quartos) &
    (dados['banheiros'] >= banheiros) &
    (dados['preco'] >= preco[0]) &
    (dados['preco'] <= preco[1])
]

st.markdown(f"🔢 Total de imóveis exibidos: **{len(dados)}**")

# ✅ Token Jawg
access_token = "ZK6EgfhFT6px8F8MsRfOp2S5aUMPOvNr5CEEtLmjOYjHDC2MzgI0ZJ1cJjj0C98Y"

# 🔥 Mapa de Calor
mapa_calor = folium.Map(
    location=[-23.4205, -51.9331],
    zoom_start=13,
    tiles=f"https://tile.jawg.io/jawg-matrix/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}",
    attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
)

pontos_calor = dados[['latitude', 'longitude', 'preco']].values.tolist()
HeatMap(pontos_calor, radius=15, blur=10, max_zoom=1).add_to(mapa_calor)

st.subheader("🔥 Mapa de Calor")
folium_static(mapa_calor)

# 🧭 Mapa com Clusters Espaciais
gdf = gpd.GeoDataFrame(
    dados,
    geometry=gpd.points_from_xy(dados.longitude, dados.latitude),
    crs="EPSG:4326"
)

w = KNN.from_dataframe(gdf, k=10)
w.transform = 'R'
moran_local = Moran_Local(gdf['preco'], w)

gdf['I_local'] = moran_local.Is
gdf['p_local'] = moran_local.p_sim
labels = np.array(['NS', 'HH', 'LH', 'LL', 'HL'])
gdf['cluster'] = np.where(gdf['p_local'] < 0.05, labels[moran_local.q], 'NS')

cores = {
    'HH': '#006400',
    'LL': '#8B0000',
    'LH': '#1E90FF',
    'HL': '#FFD700',
    'NS': '#A9A9A9'
}

mapa_cluster = folium.Map(
    location=[-23.4205, -51.9331],
    zoom_start=13,
    tiles=f"https://tile.jawg.io/jawg-matrix/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={access_token}",
    attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
)

for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color=cores[row['cluster']],
        fill=True,
        fill_color=cores[row['cluster']],
        fill_opacity=0.85,
        popup=f"{row['nome']}<br>R$ {row['preco']:.2f}<br>{row['tipo']}, {row['quartos']} Q / {row['banheiros']} B<br>Cluster: {row['cluster']}"
    ).add_to(mapa_cluster)

st.subheader("🧭 Mapa com Clusters Espaciais")
folium_static(mapa_cluster)

# 📊 Estatísticas
st.subheader("📊 Estatísticas Gerais")
variaveis = ['preco', 'preco do m²']
estatisticas_gerais = df[variaveis].describe().T
estatisticas_gerais['coef_var'] = estatisticas_gerais['std'] / estatisticas_gerais['mean']
estatisticas_gerais['moda'] = df[variaveis].mode().iloc[0]
st.dataframe(estatisticas_gerais[['mean', '50%', 'min', 'max', 'std', 'coef_var', 'moda']])

st.subheader("🏠 Estatísticas por Tipo")
tipos = df['tipo'].dropna().unique()
estatisticas_por_tipo = []
for tipo in tipos:
    grupo = df[df['tipo'] == tipo]
    resumo = grupo['preco do m²'].describe()
    coef_var = resumo['std'] / resumo['mean']
    moda = grupo['preco do m²'].mode().iloc[0] if not grupo['preco do m²'].mode().empty else None
    estatisticas_por_tipo.append({
        'tipo': tipo,
        'media': resumo['mean'],
        'mediana': resumo['50%'],
        'min': resumo['min'],
        'max': resumo['max'],
        'std': resumo['std'],
        'coef_var': coef_var,
        'moda': moda
    })
st.dataframe(pd.DataFrame(estatisticas_por_tipo))

st.subheader("🏘️ Estatísticas por Bairro")
bairros = df['bairro'].dropna().unique()
estatisticas_por_bairro = []
for bairro in bairros:
    grupo = df[df['bairro'] == bairro]
    resumo = grupo['preco do m²'].describe()
    coef_var = resumo['std'] / resumo['mean']
    moda = grupo['preco do m²'].mode().iloc[0] if not grupo['preco do m²'].mode().empty else None
    estatisticas_por_bairro.append({
        'bairro': bairro,
        'media': resumo['mean'],
        'mediana': resumo['50%'],
        'min': resumo['min'],
        'max': resumo['max'],
        'std': resumo['std'],
        'coef_var': coef_var,
        'moda': moda
    })
st.dataframe(pd.DataFrame(estatisticas_por_bairro).sort_values(by='media', ascending=False))

st.subheader("🏗️ Estatísticas por Tipo + Bairro")
grupos = df.dropna(subset=['tipo', 'bairro'])
estatisticas_tipo_bairro = []
for (tipo, bairro), grupo in grupos.groupby(['tipo', 'bairro']):
    resumo = grupo['preco do m²'].describe()
    coef_var = resumo['std'] / resumo['mean']
    moda = grupo['preco do m²'].mode().iloc[0] if not grupo['preco do m²'].mode().empty else None
    estatisticas_tipo_bairro.append({
        'tipo': tipo,
        'bairro': bairro,
        'media': resumo['mean'],
        'mediana': resumo['50%'],
        'min': resumo['min'],
        'max': resumo['max'],
        'std': resumo['std'],
        'coef_var': coef_var,
        'moda': moda
    })
st.dataframe(pd.DataFrame(estatisticas_tipo_bairro).sort_values(by='media', ascending=False))
