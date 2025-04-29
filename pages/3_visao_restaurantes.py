from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
import pandas as pd
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Visão Restaurantes',page_icon='🍽️',layout='wide')

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
def distance(df1):
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
    df1['distance'] = df1.loc[:,cols].apply(lambda x:
                            haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'] ,x['Delivery_location_longitude'])), axis=1)
    
    avg_distance = np.round(df1['distance'].mean(),2)
    
    return avg_distance
#--------------------------------------------------------------------------------------------------------
def avg_std_time_delivery(df1,festival,op):
    df_aux = (df1.loc[:,['Time_taken(min)','Festival']]
            .groupby('Festival')
            .agg({'Time_taken(min)': ['mean','std']}))

    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    
    df_aux = np.round(df_aux.loc[df_aux['Festival']==festival,op],2)
    return df_aux
#--------------------------------------------------------------------------------------------------------
def avg_std_time_graph(df1):            
    df_aux = df1.loc[:,['City','Time_taken(min)']].groupby('City').agg( {'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux =df_aux.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',x = df_aux['City'], y = df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    
    return fig
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

#Import Dataset
df = pd.read_csv('arquivos/train.csv')
#--------------------------------------------------

#Limpando dados
df1 = clean_code(df)

#============================================================
#     Barra lateral
#============================================================
st.header('Marketplace - Visão Restaurantes')

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
tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with st.container():
    st.title("Overal Metrics")
    col1, col2, col3, col4,col5,col6 = st.columns(6)
    with col1:
        delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
        col1.metric('Entregadores únicos',delivery_unique)
    with col2:
        avg_distance =  distance(df1)
        col2.metric('A distancia media',avg_distance) 
    with col3:
        df_aux = avg_std_time_delivery(df1,'Yes','avg_time')
        col3.metric('Tempo médio ', df_aux)        
    with col4:
        df_aux = avg_std_time_delivery(df1,'Yes','std_time')
        col4.metric('STD Entrega ', df_aux)
    with col5:
        df_aux = avg_std_time_delivery(df1,'No','avg_time')
        col5.metric('Tempo médio ', df_aux)
    with col6:
        df_aux = avg_std_time_delivery(df1,'No','std_time')
        col6.metric('STD Entrega ', df_aux)

with st.container():
    st.markdown("""---""")
    st.title('Distribuição da média por cidade')
    
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
    df1['distance'] =df1.loc[:,cols].apply(lambda x:
                                            haversine ((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                       (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
    
    avg_distance =df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
    
    fig = go.Figure(data=[go.Pie(labels = avg_distance['City'],values=avg_distance['distance'],pull=[0,0.1,0])])
    st.plotly_chart(fig)

with st.container():
    st.markdown("""---""")
    st.title("Distribuição de tempo")
    col1, col2= st.columns(2)
    
    with col1:
        fig = avg_std_time_graph(df1)
        st.markdown('## Distribuição do tempo por cidade')
        st.plotly_chart(fig)
    with col2:
            st.markdown('## Tempo médio por entrega')
            cols = ['City','Time_taken(min)','Road_traffic_density']
            df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time','std_time']
            
            df_aux = df_aux.reset_index()
            
            fig = px.sunburst(df_aux, path = ['City','Road_traffic_density'],values='avg_time',
                            color= 'std_time',color_continuous_scale='RdBu',
                            color_continuous_midpoint= np.average(df_aux['std_time']))
            
            st.plotly_chart(fig)
        
with st.container():
    st.markdown("""---""")
    st.title('Distribuição da distância')
    
    df_aux = (df1.loc[:,['City','Time_taken(min)','Type_of_order']]
                .groupby(['City','Type_of_order'])
                .agg({'Time_taken(min)':['mean','std']}))
    
    df_aux.columns = ['avg_time','std_time']
    
    df_aux = df_aux.reset_index()
    
    st.dataframe( df_aux)
    
    
