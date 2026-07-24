import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast

# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Copa Challenger — Dashboard",
    page_icon="⚽",
    layout="wide",
)

# CSS pra dar identidade visual (cores da Copa, cards mais destacados)
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1c1c24;
        border: 1px solid #2e2e3a;
        border-radius: 10px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Copa do Mundo 2018 e 2022 — A Ilusão do Favoritismo")
st.markdown(
    "Uma análise de dados sobre público, disciplina e eficiência ofensiva — "
    "e como estatísticas pré-jogo não garantem o título."
)

# ============================================================
# 2. CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ============================================================
@st.cache_data
def carregar_dados():
    matches = pd.read_csv('matches_1930_2022.csv')
    df = matches[matches['Year'].isin([2018, 2022])].copy()

    df['penaltis'] = df['Notes'].str.contains('penalty kicks', na=False)

    def contar_cartoes(valor):
        if pd.isnull(valor):
            return 0
        return len(ast.literal_eval(valor))

    df['qtd_amarelo_home'] = df['home_yellow_card_long'].apply(contar_cartoes)
    df['qtd_amarelo_away'] = df['away_yellow_card_long'].apply(contar_cartoes)
    df['qtd_vermelho_home'] = df['home_red_card'].notnull().astype(int)
    df['qtd_vermelho_away'] = df['away_red_card'].notnull().astype(int)

    return df

df_matches = carregar_dados()

@st.cache_data
def calcular_cartoes(df):
    home = df.groupby('home_team')[['qtd_amarelo_home', 'qtd_vermelho_home']].sum()
    away = df.groupby('away_team')[['qtd_amarelo_away', 'qtd_vermelho_away']].sum()
    home.columns = ['amarelos', 'vermelhos']
    away.columns = ['amarelos', 'vermelhos']
    total = home.add(away, fill_value=0)
    total.index.name = 'selecao'
    return total.reset_index()

@st.cache_data
def calcular_xg(df):
    home = df.groupby('home_team').agg(gols=('home_score', 'sum'), xg=('home_xg', 'sum'))
    away = df.groupby('away_team').agg(gols=('away_score', 'sum'), xg=('away_xg', 'sum'))
    total = home.add(away, fill_value=0)
    total['diferenca'] = total['gols'] - total['xg']
    total.index.name = 'selecao'
    return total.reset_index()

cartoes_df = calcular_cartoes(df_matches)
xg_df = calcular_xg(df_matches)

# ============================================================
# 3. BARRA LATERAL — FILTROS
# ============================================================
st.sidebar.header("🔍 Filtros")
anos_selecionados = st.sidebar.multiselect(
    "Edição da Copa",
    options=[2018, 2022],
    default=[2018, 2022]
)

if not anos_selecionados:
    st.sidebar.warning("Selecione ao menos uma edição.")
    st.stop()

df_filtrado = df_matches[df_matches['Year'].isin(anos_selecionados)]
cartoes_filtrado = calcular_cartoes(df_filtrado)
xg_filtrado = calcular_xg(df_filtrado)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Sobre:** dashboard construído a partir da análise das Missões 1 (SQL) "
    "e 2 (EDA em Python) da Copa Challenger."
)

# ============================================================
# 4. ABAS
# ============================================================
tab_geral, tab_publico, tab_disciplina, tab_eficiencia, tab_estudo_caso = st.tabs(
    ["📊 Visão Geral", "🏟️ Público", "🟨 Disciplina", "🎯 Eficiência Ofensiva", "🔎 Estudo de Caso: Brasil"]
)

# ---------------- TAB 1: VISÃO GERAL ----------------
with tab_geral:
    st.subheader("Indicadores gerais")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partidas analisadas", len(df_filtrado))
    col2.metric("Público médio", f"{int(df_filtrado['Attendance'].mean()):,}".replace(',', '.'))
    col3.metric("Decisões por pênaltis", int(df_filtrado['penaltis'].sum()))
    taxa_penaltis = df_filtrado['penaltis'].sum() / len(df_filtrado) * 100
    col4.metric("Taxa de jogos c/ pênaltis", f"{taxa_penaltis:.1f}%")

    st.markdown("---")
    st.markdown(
        """
        Esse dashboard resume a jornada analítica das Missões 1 e 2: o ranking FIFA
        aponta favoritos, mas jogos de mata-mata em Copa do Mundo têm um componente
        de acaso — visível em pênaltis, cartões acumulados e diferenças entre a
        qualidade de chances criadas (xG) e os gols realmente convertidos.
        Explore as abas para ver cada parte da análise.
        """
    )

# ---------------- TAB 2: PÚBLICO ----------------
with tab_publico:
    st.subheader("Evolução do público ao longo do torneio")

    fig_publico = px.line(
        df_filtrado.sort_values('Date'),
        x='Date', y='Attendance', color='Year',
        markers=True,
        labels={'Attendance': 'Público', 'Date': 'Data', 'Year': 'Edição'},
        color_discrete_map={2018: '#5DA9E9', 2022: '#F2A93B'}
    )
    fig_publico.update_layout(hovermode='x unified')
    st.plotly_chart(fig_publico, use_container_width=True)

    st.markdown(
        "O público não sobe de forma suave conforme o torneio avança — as "
        "oscilações refletem principalmente o **tamanho do estádio de cada jogo "
        "específico**, não uma tendência temporal."
    )

    st.subheader("Distribuição de público e outliers")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig_box = px.box(df_filtrado, y='Attendance', points='all',
                          labels={'Attendance': 'Público'})
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        top5 = df_filtrado.nlargest(5, 'Attendance')[['Date', 'home_team', 'away_team', 'Round', 'Attendance']]
        st.markdown("**Top 5 jogos com maior público**")
        st.dataframe(top5, hide_index=True, use_container_width=True)
        st.info(
            "Os 5 jogos mais concorridos foram todos da Copa de 2022, no "
            "**Estádio Lusail** (Catar) — 3 deles atingiram exatamente 88.966 "
            "pessoas, a capacidade máxima do estádio, em fases diferentes do "
            "torneio (grupos, semifinal e final)."
        )

# ---------------- TAB 3: DISCIPLINA ----------------
with tab_disciplina:
    st.subheader("Cartões por seleção")

    top_n = st.slider("Quantas seleções mostrar?", 5, 20, 10)
    cartoes_top = cartoes_filtrado.sort_values('amarelos', ascending=False).head(top_n)

    fig_cartoes = px.bar(
        cartoes_top, x='amarelos', y='selecao', orientation='h',
        color='vermelhos', color_continuous_scale='Reds',
        labels={'amarelos': 'Cartões amarelos', 'selecao': 'Seleção', 'vermelhos': 'Vermelhos'},
        text='amarelos'
    )
    fig_cartoes.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cartoes, use_container_width=True)

    st.markdown(
        "Argentina, Croácia e França — os 3 times com mais cartões amarelos — "
        "foram justamente os 3 finalistas/semifinalistas de 2022. Isso sugere que "
        "**jogar mais fases** (logo, mais partidas, incluindo mata-matas com "
        "prorrogação) acumula mais cartões — não necessariamente que o time joga "
        "\"mais sujo\". *Esta contagem não é normalizada por jogos disputados.*"
    )

# ---------------- TAB 4: EFICIÊNCIA OFENSIVA (xG) ----------------
with tab_eficiencia:
    st.subheader("Gols reais vs. Gols esperados (xG)")

    xg_ordenado = xg_filtrado.sort_values('diferenca')
    destaque = st.multiselect(
        "Destacar seleção(ões) no gráfico",
        options=xg_ordenado['selecao'].tolist(),
        default=['Brazil', 'France'] if 'Brazil' in xg_ordenado['selecao'].values else []
    )

    cores = ['#E74C3C' if s in destaque else '#4C6B8A' for s in xg_ordenado['selecao']]

    fig_xg = go.Figure(go.Bar(
        x=xg_ordenado['diferenca'],
        y=xg_ordenado['selecao'],
        orientation='h',
        marker_color=cores,
        text=xg_ordenado['diferenca'].round(1),
        textposition='outside'
    ))
    fig_xg.update_layout(
        xaxis_title="Gols reais − xG (déficit / superávit de conversão)",
        yaxis_title="",
        height=800
    )
    st.plotly_chart(fig_xg, use_container_width=True)

    st.markdown(
        "Barras à **direita (positivas)** indicam times que converteram mais "
        "gols do que a qualidade das chances sugeria (eficiência/sorte na "
        "finalização). Barras à **esquerda (negativas)** indicam times que "
        "criaram chances, mas não converteram."
    )

# ---------------- TAB 5: ESTUDO DE CASO — BRASIL ----------------
with tab_estudo_caso:
    st.header("🔎 Estudo de caso: o favorito que caiu no xG e nos pênaltis")

    st.markdown(
        """
        Esta seção conecta três achados da análise (Missões 1 e 2) para contar
        uma única história: **por que o time apontado como favorito não foi
        campeão em 2022.**
        """
    )

    st.markdown("### 1. O favoritismo no papel")
    ranking_top5 = pd.DataFrame({
        'Seleção': ['Brasil', 'Bélgica', 'Argentina', 'França', 'Inglaterra'],
        'Posição no ranking FIFA (pré-Copa 2022)': [1, 2, 3, 4, 5],
        'Pontos': [1841.3, 1816.71, 1773.88, 1759.78, 1728.47]
    })
    st.dataframe(ranking_top5, hide_index=True, use_container_width=True)
    st.markdown(
        "O Brasil chegou à Copa de 2022 como **favorito número 1** do ranking "
        "FIFA — à frente inclusive da Argentina, que viria a ser a campeã (3ª "
        "colocada no ranking)."
    )

    st.markdown("### 2. A trajetória do Brasil na Copa")
    jogos_brasil = df_matches[
        (df_matches['Year'] == 2022) &
        ((df_matches['home_team'] == 'Brazil') | (df_matches['away_team'] == 'Brazil'))
    ][['Date', 'Round', 'home_team', 'home_score', 'away_team', 'away_score']].sort_values('Date')
    st.dataframe(jogos_brasil, hide_index=True, use_container_width=True)
    st.markdown(
        "Campanha dominante até as oitavas (3 vitórias na fase de grupos, "
        "goleada de 4x1 sobre a Coreia do Sul), mas eliminado nas **quartas de "
        "final**, empatado em 1x1 com a Croácia no tempo normal — decidido nos "
        "pênaltis."
    )

    st.markdown("### 3. O que os números do próprio jogo mostram")
    col_x, col_y, col_z = st.columns(3)
    col_x.metric("xG do Brasil no jogo", "2.5")
    col_y.metric("xG da Croácia no jogo", "0.6")
    col_z.metric("Razão de domínio", "≈ 4×")

    st.markdown(
        """
        O Brasil criou **mais de 4 vezes** a qualidade de chances de gol da
        Croácia naquele jogo específico (xG de 2,5 contra 0,6) — mas o placar
        terminou empatado, e a eliminação veio na disputa de pênaltis.

        Esse resultado não é isolado: ao longo de toda a Copa de 2022, o Brasil
        teve o **maior déficit de conversão do torneio** — fez 16 gols reais
        contra um xG acumulado de 23,7 (quase 8 gols "perdidos" em relação ao
        que a qualidade das chances sugeria).
        """
    )

    st.success(
        """
        **Conclusão do estudo de caso:** o Brasil não foi eliminado por falta de
        criação ofensiva — pelo contrário, criou tanta chance de gol quanto os
        favoritos ao título. A queda se explica por uma combinação de
        **ineficiência na finalização** (consistente durante todo o torneio,
        não só nesse jogo) e o **fator de acaso inerente a uma disputa de
        pênaltis**. Isso demonstra, com dados concretos, o limite de ranking,
        xG e criação de jogo como preditores de resultado em mata-mata — o
        torneio é, em parte, decidido por variância que nenhuma métrica
        pré-jogo capta plenamente.
        """
    )