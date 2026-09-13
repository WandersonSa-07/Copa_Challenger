# %% Importações e carregamento dos dados

import pandas as pd


matches = pd.read_csv('matches_1930_2022.csv')
world_cup = pd.read_csv('world_cup.csv')
ranking_2022 = pd.read_csv('fifa_ranking_2022-10-06.csv')


print(matches.shape)
print(world_cup.shape)
print(ranking_2022.shape)


# %% Identificando valores ausentes
# Filtrando para o escopo do desafio (2018 e 2022) antes de checar nulos
matches_filtrado = matches[matches['Year'].isin([2018, 2022])].copy()


print("Valores ausentes em matches (2018 e 2022):")
print(matches_filtrado.isnull().sum())

print("\nValores ausentes em world_cup:")
print(world_cup.isnull().sum())

print("\nValores ausentes em ranking_2022:")
print(ranking_2022.isnull().sum())


# %% Uma observação: nem todo nulo é um dado faltando, algumas coisas podem não ter acontecido e por isso nem precisaram ser registradas

# Então por isso, as colunas que serão investigadas são: home_goal, away_goal e Notes
# Notes:
print(matches_filtrado[matches_filtrado['Notes'].notnull()][['Date', 'home_team', 'away_team', 'Notes']])


# Inicialmente pensei que essa coluna não serviria de nada, só olhei por desencargo de consciência
# Porém, olhando ela percebi que nela há informações de jogos que foram decididos por pênaltis


# %% Por essa razão, decidi criar uma nova coluna, que indica se o jogo foi decidido por pênalti ou não

# Criando o indicador "decidido nos pênaltis"
matches_filtrado['penaltis'] = matches_filtrado['Notes'].str.contains('penalty kicks', na=False)

print(matches_filtrado['penaltis'].value_counts())
print("\nJogos decididos nos pênalis:")
print(matches_filtrado[matches_filtrado['penaltis']][['Date', 'home_team', 'away_team', "Score"]])

# Resultado:
# Dos 128 jogos de 2018 e 2022, 9 foram decididos na disputade pênaltis, incluindo o jogo Brasil X Croácia analisado na Missão 1. Um jogo adicional teve prorrogação sem ir aos pênaltis.

# Insight:
# A coluna "Notes", originalmente quase toda nula, não representa dado faltando, representa a ausência do evento "empate no tempo normal em jogo eliminatório".
# Trnaformar ela em uma coluna boolena (penaltis), fez com que ela deixasse de ser um texto livre e inútil para passar a alimentar diretamente as análises qualitativas, como taxa de jogos decididos por pênaltis no mata-mata

# %% Identificar inconsistências/ detectar outliers
# Attendance = é o público no estádio, e pode variar muito (de estádios pequenos ao Maracanã lotado)

# Attendance:
print(matches_filtrado['Attendance'].describe())

import matplotlib.pyplot as plt


plt.figure(figsize=(6,4))
plt.boxplot(matches_filtrado['Attendance'])
plt.title('Distribuição de público (2018 e 2022)')
plt.ylabel('Público (Attendance)')
plt.show()

# %% Identificar os jogos com maior público (outliers)
top_publico = matches_filtrado.nlargest(5, 'Attendance')[['Date', 'home_team', 'away_team', 'Round', 'Attendance']]
print(top_publico)


# Resultado:
# Os 5 jogos com maior público de 2018/2022 foram todos da Copa de 2022, sediados no Estádio Lusail (Catar), com destaque para 3 jogos com exatamente 88.966 pessoas (a capacidade máxima do estádio): a final (Argentina x França), a semifinal (Argentina x Croácia) e um jogo de fase de grupos (Argentina x México).
# Insight:
# Os outliers de público não indicam erro de coleta, mas sim lotação máxima do maior estádio da Copa 2022 (Lusail), atingida em jogos de fases distintas, inclusive um jogo de fase de grupos. Um padrão adicional interessante: 3 dos 5 jogos mais concorridos envolveram a Argentina, sugerindo que a torcida argentina teve grande presença/procura por ingressos ao longo de todo o torneio, não só na final.


# %% Evolução do público ao longo do torneio ( 2018 vs 2022)
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

for ax, ano in zip(axes, [2018, 2022]):
    dados = matches_filtrado[matches_filtrado['Year'] == ano].sort_values('Date')
    ax.plot(dados['Date'], dados['Attendance'], marker='o', linestyle='-')
    ax.set_title(f'Copa {ano}')
    ax.set_xlabel('Data')
    ax.tick_params(axis='x', rotation=45)

axes[0].set_ylabel('Público (Attendance)')
plt.tight_layout()
plt.show()

# %% Explorar cartões: quem mais recebeu cartão amarelo/vermelho

# Converter a string em lista e contar cartões por jogo
import ast

def contar_cartoes(valor):
    if pd.isnull(valor):
        return 0
    lista = ast.literal_eval(valor)
    return len(lista)


matches_filtrado['qtd_amarelo_home'] = matches_filtrado['home_yellow_card_long'].apply(contar_cartoes)
matches_filtrado['qtd_amarelo_away'] = matches_filtrado['away_yellow_card_long'].apply(contar_cartoes)


print(matches_filtrado[['home_team', 'away_team', 'qtd_amarelo_home', 'qtd_amarelo_away']].head(10))

# Objetivo: transformar a string bruta em uma contagem numérica simples por jogo, que aí sim pode ser somada/comparada entre times.


# %% Contar cartões vermelhos (formato de string única, não lista) e consolidar por seleção
matches_filtrado['qtd_vermelho_home'] = matches_filtrado['home_red_card'].notnull().astype(int)
matches_filtrado['qtd_vermelho_away'] = matches_filtrado['away_red_card'].notnull().astype(int)

cartoes_home = matches_filtrado.groupby('home_team')[['qtd_amarelo_home', 'qtd_vermelho_home']].sum()
cartoes_away = matches_filtrado.groupby('away_team')[['qtd_amarelo_away', 'qtd_vermelho_away']].sum()

cartoes_home.columns = ['amarelos', 'vermelhos']
cartoes_away.columns = ['amarelos', 'vermelhos']

cartoes_total = cartoes_home.add(cartoes_away, fill_value=0)
cartoes_total = cartoes_total.sort_values('amarelos', ascending=False)
cartoes_total.index.name = 'selecao'
print(cartoes_total.head(10))

# Resultado:
# A Argentina lidera em cartões amarelos no período (30), seguida por Croácia (23), Sérvia (21) e França (20). Cartões vermelhos são raros no geral, só 2 casos aparecem no Top 10 (Suíça e Coreia do Sul, 1 cada)

# Insight:
# É interessante notar que Argentina, Croácia e França, os 3 times com mais cartões amarelos, foram justamente os 3 finalistas/semifinalistas de 2022 (Argentina campeã, França vice, Croácia 3º lugar)
# Isso sugere uma explicação plausível: quanto mais jogos um time disputa no torneio (por avançar de fase), mais cartões acumula, não necessariamente porque joga "mais sujo", mas porque joga mais partidas, incluindo jogos de mata-mata com prorrogação, que tendem a ser mais desgastantes e tensos
# Vale notar que essa contagem não é normalizada por número de jogos disputados, times que foram mais longe no torneio têm vantagem "artificial" nesse ranking bruto


# %% Comparar xG (gols esperados) vs gols reais por seleção
xg_home = matches_filtrado.groupby('home_team').agg(
    gols_feitos=('home_score', 'sum'),
    xg_total=('home_xg', 'sum')
)
xg_away = matches_filtrado.groupby('away_team').agg(
    gols_feitos=('away_score', 'sum'),
    xg_total=('away_xg', 'sum')
)

xg_total = xg_home.add(xg_away, fill_value=0)
xg_total['diferenca'] = xg_total['gols_feitos'] - xg_total['xg_total']
xg_total = xg_total.sort_values('diferenca', ascending=False)

print(xg_total)

# Objetivo: 
# Somar, por seleção, quantos gols cada time fez de verdade (gols_feitos) e quantos "deveria" ter feito segundo a qualidade das chances criadas (xg_total). A coluna "diferenca" mostra quem superou a expectativa (positivo: converteu mais do que criaria esperar, indicando eficiência ou sorte na finalização) e quem ficou abaixo (negativo: criou chances mas não converteu)


# Resultado:
# A França liderou o ranking de eficiência ofensiva, convertendo 7,1 gols a mais do que o esperado pelo xG (30 gols feitos vs 22,9 esperados). No extremo oposto, o Brasil teve o pior desempenho de conversão do período: fez 16 gols reais contra um xG de 23,7 (um déficit de quase 8 gols, o maior entre todas as 38 seleções analisadas)


# Insight:
# O Brasil criou volume de chances muito acima da média (23,7 xG é um dos maiores totais da tabela, atrás só de times como França e Inglaterra), mas converteu muito abaixo do esperado. Isso dá um contraponto estatístico importante ao insight da Missão 1: o Brasil não foi eliminado por falta de criação ofensiva, pelo contrário, criou tanta chance quanto os favoritos ao título, mas por ineficiência na finalização, um problema que fica mascarado quando se olha só o resultado final (eliminação nos pênaltis contra a Croácia)
# Isso reforça a hipótese de "azar/momento" da Missão 1, agora com evidência quantitativa: o time teve material ofensivo de campeão, mas não converteu




# %% Detalhe do jogo Brasil x Croácia (quartas de final, 2022)
jogo_brasil_croacia = matches_filtrado[
    ((matches_filtrado['home_team'] == 'Brazil') & (matches_filtrado['away_team'] == 'Croatia')) |
    ((matches_filtrado['home_team'] == 'Croatia') & (matches_filtrado['away_team'] == 'Brazil'))
]

print(jogo_brasil_croacia[['home_team', 'home_score', 'home_xg', 'away_team', 'away_score', 'away_xg']])

# Resultado:
# No confronto das quartas de final de 2022, o Brasil teve xG de 2,5 contra 0,6 da Croácia, uma diferença de mais de 4x na qualidade das chances criadas, mas o placar terminou empatado em 1x1, sendo o Brasil eliminado na disputa de pênaltis


# Insight:
# Esse jogo específico é a evidência mais direta de todo o arco de análise construído desde a Missão 1: o Brasil dominou estatisticamente o confronto (xG de 2,5 vs 0,6), tinha o ranking FIFA mais alto entre os 32 times, mas foi eliminado por uma combinação de baixa conversão de chances (consistente com seu déficit de -7,7 no torneio inteiro) e o fator de acaso inerente a uma disputa de pênaltis. Isso demonstra, com dados concretos, o limite do "favoritismo no papel" (ranking, xG, criação de jogo) em prever resultados de mata-mata no futebol, o torneio é, em parte, decidido por variância que nenhuma métrica pré-jogo capta plenamente.

