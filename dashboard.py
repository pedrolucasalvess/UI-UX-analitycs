import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


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

produto_mais_vendido = df.groupby('produto')['quantidade'].sum()
produto_mais_vendido = produto_mais_vendido.sort_values(ascending=False).head(1)
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

    top_produtos = df.groupby('produto')['quantidade'].sum().sort_values(ascending=False)
    categoria_mais_vendida = df.groupby('categoria')['quantidade'].sum().sort_values(ascending=False)

    fig1, ax1 = plt.subplots(figsize=(4, 4), facecolor='none')
    ax1.pie(top_produtos, labels=top_produtos.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax1.axis('equal')
    ax1.set_position([0.1, 0.1, 0.8, 0.8])
    fig1.patch.set_alpha(0)

    fig2, ax2 = plt.subplots(figsize=(4, 4), facecolor='none')
    ax2.pie(categoria_mais_vendida, labels=categoria_mais_vendida.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax2.axis('equal')
    ax2.set_position([0.1, 0.1, 0.8, 0.8])
    fig2.patch.set_alpha(0)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("\U0001F355 Produtos Mais Vendidos")
        st.pyplot(fig1)
    with col2:
        st.subheader("\U0001F4C9 Categorias Mais Vendidas")
        st.pyplot(fig2)

    df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
    dias_em_portugues = {
        'Monday': 'segunda-feira', 'Tuesday': 'terça-feira', 'Wednesday': 'quarta-feira',
        'Thursday': 'quinta-feira', 'Friday': 'sexta-feira', 'Saturday': 'sábado', 'Sunday': 'domingo'
    }
    df['dia_semana'] = df['data_venda'].dt.day_name().map(dias_em_portugues)
    dias = list(dias_em_portugues.values())
    vendas_por_dia = df.groupby('dia_semana')['quantidade'].sum().reindex(dias)

    # Evolução por produto
    st.subheader("\U0001F4C8 Evolução de Vendas por Produto")
    produtos = df['produto'].unique()
    produto_selecionado = st.selectbox("Selecione um produto", produtos)
    df_produto = df[df['produto'] == produto_selecionado]
    evolucao = df_produto.groupby(df_produto['data_venda'].dt.to_period('M'))['valor_total'].sum().reset_index()
    evolucao['data_venda'] = evolucao['data_venda'].astype(str)

    fig4, ax4 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=evolucao, x='data_venda', y='valor_total', marker='o', ax=ax4)
    ax4.set_title(f'Evolução de Vendas - {produto_selecionado}')
    ax4.set_xlabel('Mês')
    ax4.set_ylabel('Faturamento (R$)')
    ax4.grid(True)
    st.pyplot(fig4)

elif painel == "📋 Tabelas":
    st.title("📋 Tabelas de Vendas")
    st.markdown("Explore os dados de vendas em tabelas interativas.")
    st.markdown("---")
    tab_cliente, tab_data, tab_pagamento = st.tabs(["\U0001F464 Cliente", "\U0001F4C5 Data", "\U0001F4B3 Forma de Pagamento"])

    with tab_cliente:
        clientes = df['cliente'].unique()
        cliente_selecionado = st.selectbox("Selecione o cliente", clientes)
        df_filtrado = df[df['cliente'] == cliente_selecionado]
        st.dataframe(df_filtrado)

    with tab_data:
        data_min = df['data_venda'].min()
        data_max = df['data_venda'].max()
        data_inicio = st.date_input("Data inicial", data_min)
        data_fim = st.date_input("Data final", data_max)
        df_filtrado = df[(df['data_venda'] >= pd.to_datetime(data_inicio)) & (df['data_venda'] <= pd.to_datetime(data_fim))]
        st.dataframe(df_filtrado)

    with tab_pagamento:
        formas = df['forma_pagamento'].unique()
        forma_selecionada = st.selectbox("Selecione a forma de pagamento", formas)
        df_filtrado = df[df['forma_pagamento'] == forma_selecionada]
        st.dataframe(df_filtrado)