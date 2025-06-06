import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

df = pd.read_csv('dados_vendas_acai.csv', sep=',', encoding='utf-8')
df = df.dropna(subset=['data_venda'])
df['data_venda'] = pd.to_datetime(df['data_venda'])

st.sidebar.title("📌 Menu")
painel = st.sidebar.radio("Escolha o painel", ["📊 Indicadores", "📈 Gráficos", "📋 Tabelas"])

faturamento_total = df['valor_total'].sum()
ticket_medio = df['valor_total'].mean()
total_vendas = df.shape[0]
clientes_unicos = df['cliente'].nunique()
forma_de_pagamento = df['forma_pagamento'].value_counts().idxmax()

produto_mais_vendido = df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(1)
produto_top = produto_mais_vendido.index[0]
quantidade_top = produto_mais_vendido.iloc[0]

def card(titulo, valor, cor):
    st.markdown(f"""
        <div style="
            background-color: {cor};
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h5 style="margin-bottom: 0.5rem;">{titulo}</h5>
            <h2 style="margin: 0;">{valor}</h2>
        </div>
    """, unsafe_allow_html=True)

if painel == "📊 Indicadores":
    st.title("📊 Indicadores de Vendas")
    st.markdown("Acompanhe os principais indicadores de vendas do seu negócio.")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        card("💰 Faturamento", f"R$ {faturamento_total:,.2f}", "#42A5F5")
    with col2:
        card("🎟️ Ticket Médio", f"R$ {ticket_medio:,.2f}", "#66BB6A")
    with col3:
        card("🏆 Produto Mais Vendido", f"{produto_top}", "#FFA726")

    col4, col5, col6 = st.columns(3)
    with col4:
        card("📊 Total de Vendas", f"{total_vendas}", "#AB47BC")
    with col5:
        card("👤 Clientes Únicos", f"{clientes_unicos}", "#8D6E63")
    with col6:
        card("💳 Pagamento Principal", forma_de_pagamento, "#4DB6AC")

elif painel == "📈 Gráficos":
    st.title("📈 Gráficos de Vendas")
    st.markdown("Visualize os dados de vendas através de gráficos interativos.")
    st.markdown("---")

    top_produtos = df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).reset_index()
    fig1 = px.pie(top_produtos, values='quantidade', names='produto', title='Produtos Mais Vendidos')

    top_categorias = df.groupby('categoria')['quantidade'].sum().sort_values(ascending=False).reset_index()
    fig2 = px.pie(top_categorias, values='quantidade', names='categoria', title='Categorias Mais Vendidas')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    dias_em_portugues = {
        'Monday': 'segunda-feira', 'Tuesday': 'terça-feira', 'Wednesday': 'quarta-feira',
        'Thursday': 'quinta-feira', 'Friday': 'sexta-feira', 'Saturday': 'sábado', 'Sunday': 'domingo'
    }
    df['dia_semana'] = df['data_venda'].dt.day_name().map(dias_em_portugues)
    dias = list(dias_em_portugues.values())
    vendas_por_dia = df.groupby('dia_semana')['quantidade'].sum().reindex(dias).reset_index()
    fig3 = px.bar(vendas_por_dia, x='dia_semana', y='quantidade', title='Vendas por Dia da Semana')
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📈 Evolução de Vendas por Produto")
    produtos = df['produto'].unique()
    produto_selecionado = st.selectbox("Selecione um produto", produtos)
    df_produto = df[df['produto'] == produto_selecionado]
    evolucao = df_produto.groupby(df_produto['data_venda'].dt.to_period('M'))['valor_total'].sum().reset_index()
    evolucao['data_venda'] = evolucao['data_venda'].astype(str)
    fig4 = px.line(evolucao, x='data_venda', y='valor_total', markers=True, title=f'Evolução de Vendas - {produto_selecionado}')
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("🕒 Horário de Pico de Vendas")
    df['hora_venda'] = pd.to_datetime(df['data_venda']).dt.hour
    horario_pico = df['hora_venda'].value_counts().sort_index().reset_index()
    horario_pico.columns = ['hora', 'vendas']
    fig5 = px.bar(horario_pico, x='hora', y='vendas', title='Horário de Pico de Vendas')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("👥 Clientes Mais Compradores")
    top_clientes = df['cliente'].value_counts().head(10).reset_index()
    top_clientes.columns = ['cliente', 'compras']
    fig6 = px.bar(top_clientes, x='cliente', y='compras', title='Clientes Mais Compradores')
    st.plotly_chart(fig6, use_container_width=True)

elif painel == "📋 Tabelas":
    st.title("📋 Tabelas de Vendas")
    st.markdown("Explore os dados de vendas com filtros interativos.")
    st.markdown("---")

    with st.expander("📊 Filtros de Vendas"):
        col1, col2 = st.columns(2)
        with col1:
            clientes = st.multiselect("Filtrar por Clientes", df['cliente'].unique())
            categorias = st.multiselect("Filtrar por Categoria", df['categoria'].unique())
        with col2:
            data_min = df['data_venda'].min().date()
            data_max = df['data_venda'].max().date()
            data_inicio = st.date_input("Data inicial", data_min)
            data_fim = st.date_input("Data final", data_max)

    df_filtrado = df.copy()
    if clientes:
        df_filtrado = df_filtrado[df_filtrado['cliente'].isin(clientes)]
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias)]
    df_filtrado = df_filtrado[(df_filtrado['data_venda'].dt.date >= data_inicio) & (df_filtrado['data_venda'].dt.date <= data_fim)]

    st.subheader("📄 Dados Filtrados")
    st.dataframe(df_filtrado.reset_index(drop=True))
