# %% Importações e carregamento dos dados
import pandas as pd

matches = pd.read_csv('matches_1930_2022.csv')
ranking_2022 = pd.read_csv('fifa_ranking_2022-10-06.csv')

# %% Criar a variável-alvo (resultado do jogo)
def definir_resultado(row):
    if row['home_score'] > row['away_score']:
        return 'vitoria_mandante'
    elif row['home_score'] < row['away_score']:
        return 'vitoria_visitante'
    else:
        return 'empate'

matches['resultado'] = matches.apply(definir_resultado, axis=1)

# %% Restringir a 2018/2022 e juntar com o ranking FIFA
matches_filtrado = matches[matches['Year'].isin([2018, 2022])].copy()

print(matches_filtrado['resultado'].value_counts())
print("\nBaseline (sempre prever vitória do mandante):",
      round(matches_filtrado['resultado'].value_counts(normalize=True)['vitoria_mandante'] * 100, 1), "%")

matches_filtrado = matches_filtrado.merge(
    ranking_2022[['team', 'rank', 'points']], left_on='home_team', right_on='team'
).rename(columns={'rank': 'rank_home', 'points': 'points_home'}).drop(columns='team')

matches_filtrado = matches_filtrado.merge(
    ranking_2022[['team', 'rank', 'points']], left_on='away_team', right_on='team'
).rename(columns={'rank': 'rank_away', 'points': 'points_away'}).drop(columns='team')

matches_filtrado['diferenca_ranking'] = matches_filtrado['rank_away'] - matches_filtrado['rank_home']
matches_filtrado['diferenca_pontos'] = matches_filtrado['points_home'] - matches_filtrado['points_away']

print(matches_filtrado[['home_team', 'away_team', 'diferenca_ranking', 'diferenca_pontos', 'resultado']].head(10))



# %% Separar treino/teste e treinar o primeiro modelo
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X = matches_filtrado[['diferenca_ranking', 'diferenca_pontos']]
y = matches_filtrado['resultado']

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_treino, y_treino)

previsoes = modelo.predict(X_teste)
acuracia = accuracy_score(y_teste, previsoes)

print(f"Tamanho do treino: {len(X_treino)} jogos")
print(f"Tamanho do teste: {len(X_teste)} jogos")
print(f"Acurácia do modelo: {acuracia * 100:.1f}%")
print(f"Baseline (sempre mandante): 43.0%")


# %% Validar com cross-validation (mais confiável que um único split, dado o tamanho pequeno do dataset)
from sklearn.model_selection import cross_val_score, StratifiedKFold

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(modelo, X, y, cv=cv, scoring='accuracy')

print("Acurácia em cada uma das 5 partições:", [f"{s*100:.1f}%" for s in scores])
print(f"Acurácia média: {scores.mean()*100:.1f}% (± {scores.std()*100:.1f}%)")


# %% Comparar com Regressão Logística (modelo mais simples) e ver importância dos atributos
from sklearn.linear_model import LogisticRegression

modelo_simples = LogisticRegression(max_iter=1000)
scores_simples = cross_val_score(modelo_simples, X, y, cv=cv, scoring='accuracy')

print("Regressão Logística — acurácia média:", f"{scores_simples.mean()*100:.1f}% (± {scores_simples.std()*100:.1f}%)")
print("Random Forest — acurácia média:      ", f"{scores.mean()*100:.1f}% (± {scores.std()*100:.1f}%)")

# Importância dos atributos no Random Forest (treinado com todos os dados)
modelo.fit(X, y)
importancias = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nImportância dos atributos (Random Forest):")
print(importancias)



# %% Avaliar o modelo por categoria (não só a acurácia geral)
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix

previsoes_cv = cross_val_predict(modelo_simples, X, y, cv=cv)

print(classification_report(y, previsoes_cv))
print("\nMatriz de confusão (linhas = real, colunas = previsto):")
print(confusion_matrix(y, previsoes_cv, labels=['vitoria_mandante', 'empate', 'vitoria_visitante']))



# %% Testar com balanceamento de classes (dar mais peso ao empate, que é minoritário)
modelo_balanceado = LogisticRegression(max_iter=1000, class_weight='balanced')

scores_balanceado = cross_val_score(modelo_balanceado, X, y, cv=cv, scoring='accuracy')
previsoes_balanceado = cross_val_predict(modelo_balanceado, X, y, cv=cv)

print("Acurácia média (balanceado):", f"{scores_balanceado.mean()*100:.1f}% (± {scores_balanceado.std()*100:.1f}%)")
print(classification_report(y, previsoes_balanceado))
print("\nMatriz de confusão (balanceado):")
print(confusion_matrix(y, previsoes_balanceado, labels=['vitoria_mandante', 'empate', 'vitoria_visitante']))



# %% Aplicar o modelo final (com probabilidades) aos jogos da Copa 2026
ranking_2026 = pd.read_csv('fifa_ranking_2026-06-08.csv')
schedule_2026 = pd.read_csv('schedule_2026.csv')

# Retreinar o modelo escolhido (Regressão Logística, sem balanceamento) com todos os 128 jogos disponíveis
modelo_final = LogisticRegression(max_iter=1000)
modelo_final.fit(X, y)

# Preparar os atributos dos jogos futuros da mesma forma que fizemos com o histórico
schedule_com_ranking = schedule_2026.merge(
    ranking_2026[['team', 'rank', 'points']], left_on='home_team', right_on='team'
).rename(columns={'rank': 'rank_home', 'points': 'points_home'}).drop(columns='team')

schedule_com_ranking = schedule_com_ranking.merge(
    ranking_2026[['team', 'rank', 'points']], left_on='away_team', right_on='team'
).rename(columns={'rank': 'rank_away', 'points': 'points_away'}).drop(columns='team')

schedule_com_ranking['diferenca_ranking'] = schedule_com_ranking['rank_away'] - schedule_com_ranking['rank_home']
schedule_com_ranking['diferenca_pontos'] = schedule_com_ranking['points_home'] - schedule_com_ranking['points_away']

print(f"Jogos do schedule_2026 originais: {len(schedule_2026)}")
print(f"Jogos após o merge com o ranking: {len(schedule_com_ranking)}")

X_2026 = schedule_com_ranking[['diferenca_ranking', 'diferenca_pontos']]
probabilidades = modelo_final.predict_proba(X_2026)

resultado_previsto = pd.DataFrame(probabilidades, columns=modelo_final.classes_)
previsoes_2026 = pd.concat([
    schedule_com_ranking[['home_team', 'away_team']].reset_index(drop=True),
    resultado_previsto
], axis=1)

print(previsoes_2026.head(10))



# %% Identificar quais times do schedule_2026 não bateram com o ranking_2026
times_schedule = set(schedule_2026['home_team']).union(set(schedule_2026['away_team']))
times_ranking = set(ranking_2026['team'])

print("Times no schedule_2026 que NÃO aparecem no ranking_2026:")
print(times_schedule - times_ranking)



# %% Ver como esses times aparecem no ranking_2026 (buscando por trechos do nome)
candidatos = ranking_2026[ranking_2026['team'].str.contains('States|Verde|Bosnia', case=False, na=False)]
print(candidatos[['team']])


# %% Buscar variações para "United States" de forma mais ampla
candidatos_usa = ranking_2026[ranking_2026['team'].str.contains('USA|U.S.|United', case=False, na=False)]
print(candidatos_usa[['team']])


# %% Corrigir nomes divergentes e gerar as previsões completas
correcao_nomes = {
    'United States': 'USA',
    'Cape Verde': 'Cabo Verde',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
}

schedule_2026['home_team'] = schedule_2026['home_team'].replace(correcao_nomes)
schedule_2026['away_team'] = schedule_2026['away_team'].replace(correcao_nomes)

schedule_com_ranking = schedule_2026.merge(
    ranking_2026[['team', 'rank', 'points']], left_on='home_team', right_on='team'
).rename(columns={'rank': 'rank_home', 'points': 'points_home'}).drop(columns='team')

schedule_com_ranking = schedule_com_ranking.merge(
    ranking_2026[['team', 'rank', 'points']], left_on='away_team', right_on='team'
).rename(columns={'rank': 'rank_away', 'points': 'points_away'}).drop(columns='team')

schedule_com_ranking['diferenca_ranking'] = schedule_com_ranking['rank_away'] - schedule_com_ranking['rank_home']
schedule_com_ranking['diferenca_pontos'] = schedule_com_ranking['points_home'] - schedule_com_ranking['points_away']

print(f"Jogos após correção: {len(schedule_com_ranking)} de {len(schedule_2026)} originais")

X_2026 = schedule_com_ranking[['diferenca_ranking', 'diferenca_pontos']]
probabilidades = modelo_final.predict_proba(X_2026)

resultado_previsto = pd.DataFrame(probabilidades, columns=modelo_final.classes_)
previsoes_2026 = pd.concat([
    schedule_com_ranking[['home_team', 'away_team']].reset_index(drop=True),
    resultado_previsto
], axis=1)

previsoes_2026.to_csv('previsoes_copa_2026.csv', index=False)
print(previsoes_2026.head(15))
