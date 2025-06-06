from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
import pandas as pd
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title='Visão Empresa',page_icon='📈',layout='wide')


#Funções
def clean_code(df1):
    
    """Esta funcao tem a responsabilidade de limpar o dataframe
        
        Tipos de Limpeza:c
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérca)
        
        Input: Dataframe
        Output: Dataframe
    """
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy() 

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy() 

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy() 

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy() 

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y' )

    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy() 
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(float)

    df1.loc[:,'ID'] =df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] =df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_vehicle'] =df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] =df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] =df1.loc[:,'Festival'].str.strip()

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")
    
    return df1
#--------------------------------------------------------------------------------------------------------
def order_metric(df1):
    cols = ['ID','Order_Date']
    df_aux = df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()

    #gráfico
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    
    return fig
#--------------------------------------------------------------------------------------------------------
def traffic_order_share( df1 ):
    cols = ['ID','Road_traffic_density']

    df_aux = df1.loc[:,cols].groupby(['Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]

    df_aux['perc_ID'] = (df_aux['ID']/df_aux['ID'].sum()) * 100
    #gráfico

    fig = px.pie(df_aux,values='perc_ID',names='Road_traffic_density')
    
    return fig
#--------------------------------------------------------------------------------------------------------
def traffic_order_city(df1):
    col = ['ID','City','Road_traffic_density']

    df_aux = df1.loc[:,col].groupby(['City','Road_traffic_density']).count().reset_index()
    #gráfico
    fig = px.scatter(df_aux,x= 'City', y='Road_traffic_density',size='ID' )
    
    return fig
#--------------------------------------------------------------------------------------------------------
def order_by_week(df1):  
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")

    cols = ['week_of_year','ID']
    df_aux = df1.loc[:, cols].groupby('week_of_year').count().reset_index()

    #gráfico
    fig = px.line(df_aux,x='week_of_year',y= 'ID')
    
    return fig
#--------------------------------------------------------------------------------------------------------
def order_by_share_week(df1):
    #quantidade de pedidos por semana / quantidade de entregadores/semana

    #quantidade de entregadores/semana
    df_aux1 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()

    #quantidade de pedidos por semana
    df_aux2 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

    df_aux = pd.merge(df_aux1,df_aux2,how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    #gráfico

    fig = px.line(df_aux, x = 'week_of_year', y = 'order_by_delivery')
    
    return fig
#--------------------------------------------------------------------------------------------------------
def country_maps(df1):
    columns = [
    'City',
    'Road_traffic_density',
    'Delivery_location_latitude',
    'Delivery_location_longitude'
    ]
    columns_groupby = ['City', 'Road_traffic_density']
    data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map= folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
            location_info['Delivery_location_longitude']],
            popup=location_info[['City', 'Road_traffic_density']] ).add_to( map)
    st_folium(map, width=1024, height=600)
    
    return None
#--------------------------------------------------Inicio da Estrutura Lógica do código------------------------------

#Import Dataset
df = pd.read_csv('arquivos/train.csv')
#--------------------------------------------------

#Limpando dados
df1 = clean_code(df)

#============================================================
#     Barra lateral
#============================================================
st.header('Marketplace - Visão Cliente')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image,width=300)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider =st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

# st.header(date_slider )
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Heitor')

#filtro de data

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

st.dataframe(df1)
#============================================================
#     Layout no streamlit 
#============================================================

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #Order metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig,use_container_width=True)
with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.header('Order by Week')
        st.plotly_chart(fig,use_container_width=True)
             
    with st.container():
        fig = order_by_share_week(df1)
        st.header('Order by Share Week')
        st.plotly_chart(fig,use_container_width=True)
            
with tab3:
    st.header('Country Maps')
    country_maps(df1)

