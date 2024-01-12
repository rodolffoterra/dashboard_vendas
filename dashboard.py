import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout= 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /=1000
    return f'{prefixo} {valor:.2f} milhões'


st.title("Dashboard de Vendas :shopping_trolley:")

url = 'https://labdados.com/produtos'
regiao = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']

st.sidebar.title("Filtros")
regiao = st.sidebar.selectbox('Região', regiao)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados e todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano',2020,2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())

if response.status_code == 200:
    dados = pd.DataFrame.from_dict(response.json())
else:
    st.error(f"Erro na requisição. Código de status: {response.status_code}")

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtros_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtros_vendedores:
    dados = dados[dados['Vendedor'].isin(filtros_vendedores)]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center;'><img src='https://static.wixstatic.com/media/cc8e7f_419c008271044d3a8c3726079edef05b~mv2.png/v1/fill/w_201,h_98,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/logo_cubo.png' alt='logo' width='201' height='98'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center;'><a href='https://www.a2ttechnology.com.br/' class='button'>Conheça nosso site</a></div>", unsafe_allow_html=True)


## Tables
### Tabelas de Receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month

# Mapeamento dos números dos meses para os nomes em português
meses_em_portugues = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

# Aplicar a transformação para obter os nomes dos meses em português
receita_mensal['Mes'] = receita_mensal['Mes'].map(meses_em_portugues)

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabela de Quantidade de vendas
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat','lon']].merge(vendas_estados, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending = False)

venda_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count().reset_index()
venda_mensal['Ano'] = venda_mensal['Data da Compra'].dt.year
venda_mensal['Mes'] = venda_mensal['Data da Compra'].dt.month
venda_mensal['Mes'] = venda_mensal['Mes'].map(meses_em_portugues)

venda_categoria = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending = False)


### Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby("Vendedor")['Preço'].agg(['sum','count']))

## Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x="Mes",
                             y='Preço',
                             markers=True,
                             color="Ano",
                             line_dash="Ano",
                             title="Receita Mensal")
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title= "Top 5 estados (Receita)"
                             )
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_recita_categorias = px.bar(receita_categoria,
                             text_auto= True,
                             title= "Receita por categoria"
                             )
fig_recita_categorias.update_layout(yaxis_title='Receita')

fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Vendas por estado')

fig_vendas_mensal = px.line(venda_mensal,
                             x="Mes",
                             y='Preço',
                             markers=True,
                             color="Ano",
                             line_dash="Ano",
                             title="Quantidade de vendas mensal")
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title= "Top 5 estados (Receita)"
                             )
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(venda_categoria,
                             text_auto= True,
                             title= "Vendas por categoria"
                             )
fig_recita_categorias.update_layout(yaxis_title='Quantidade de vendas')


## Visualização no Streamilit
aba1, aba2, aba3 = st.tabs(['Receitas','Quantidade de vendas','Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_recita_categorias, use_container_width= True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Quantidade', formata_numero(dados['Preço'].sum(),"R$"))
        st.plotly_chart(fig_mapa_vendas, use_container_width= True)
        st.plotly_chart(fig_vendas_estados, use_container_width= True)


    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width= True)
        st.plotly_chart(fig_vendas_categorias, use_container_width= True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f"Tpo. {qtd_vendedores} vendedores (receita).")
        st.plotly_chart(fig_receita_vendedores, use_container_width= True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f"Tpo. {qtd_vendedores} vendedores (quantidade de vendas).")
        st.plotly_chart(fig_vendas_vendedores, use_container_width= True)

    

