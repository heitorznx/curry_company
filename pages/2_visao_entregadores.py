from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
import pandas as pd
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title='Visão Entregadores',page_icon='🚚',layout='wide')

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
def top_delivers(df1,top_asc):
    df2 = df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']].groupby(['City','Delivery_person_ID']).max().sort_values(['City','Time_taken(min)'],ascending=top_asc).reset_index()

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index()
    
    return df3
#--------------------------------------------------------------------------------------------------------

#Import Dataset
df = pd.read_csv('arquivos/train.csv')
#--------------------------------------------------

#Limpando dados
df1 = clean_code(df)

#============================================================
#     Barra lateral
#============================================================
st.header('Marketplace - Visão Entregadores')

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
#============================================================
#     Layout no streamlit 
#============================================================

tab1 , tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        #Overall metrics
        st.title('Overall metrics')
        
        col1,col2,col3,col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].min()
            col3.metric('Melhor condição de veículo',melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:,'Vehicle_condition'].max()
            col4.metric('Pior condição de veículo',pior_condicao)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1,col2 = st.columns(2,gap = 'large')
        with col1:
            st.markdown('##### Avaliações médias por entregador')
            columns = ['Delivery_person_ID','Delivery_person_Ratings']
            avaliacoes_media_entregador = df1.loc[:,columns].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(avaliacoes_media_entregador)
        with col2:
            st.markdown('##### Avaliações média por transito')

            columns = ['Delivery_person_Ratings','Road_traffic_density']

            df_avg_std_rating_by_traffic = (df1.loc[:,columns].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean','std']}))
            df_avg_std_rating_by_traffic.columns = ['delivery_mean','delivery_std']

            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.markdown('##### Avaliações média por Condições climáticas')
            columns = ['Delivery_person_Ratings','Weatherconditions']

            df_avg_std_weatherconditions = (df1.loc[:,columns].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']}))
            df_avg_std_weatherconditions.columns = ['delivery_mean','delivery_std']

            df_avg_std_weatherconditions = df_avg_std_weatherconditions.reset_index()
        
            st.dataframe(df_avg_std_weatherconditions)
        
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1,col2 = st.columns(2, gap = 'large')
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers (df1,top_asc=True)
            st.dataframe(df3)            
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers (df1,top_asc=False)
            st.dataframe(df3)
