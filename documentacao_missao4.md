# Relatório da Missão 4: Modelo de IA / Previsão

**Ferramentas:** Python, scikit-learn, pandas.

**Escopo:** treino com as Copas de 2018 e 2022 (mesmo recorte das Missões 1-3),
aplicação final às previsões da Copa de 2026 (`schedule_2026.csv` +
`fifa_ranking_2026-06-08.csv`).

Esta etapa consiste em transformar os achados das Missões 1-3 (favoritismo no
ranking não é determinante, mata-mata tem forte componente de acaso) num
modelo supervisionado que estima probabilidades de resultado (vitória do
mandante, empate, vitória do visitante) a partir da diferença de força entre
as duas seleções. Essa missão foi a mais difícil e desafiadora para mim, mesmo tendo um conhecimento de IAs, Machine Learning e métricas de performance de modelos, eu nunca tinha feito um.

---

## 1. Carregamento dos dados e definição do alvo

* **Objetivo:** carregar o histórico de partidas (1930-2022) e o ranking FIFA,
  e transformar o placar de cada jogo numa variável categórica que o modelo
  possa aprender a prever.

* **Código:**
```python
matches = pd.read_csv('matches_1930_2022.csv')
ranking_2022 = pd.read_csv('fifa_ranking_2022-10-06.csv')

def definir_resultado(row):
    if row['home_score'] > row['away_score']:
        return 'vitoria_mandante'
    elif row['home_score'] < row['away_score']:
        return 'vitoria_visitante'
    else:
        return 'empate'

matches['resultado'] = matches.apply(definir_resultado, axis=1)
```

* **Resultado:** a variável-alvo `resultado` foi criada com 3 categorias
  (vitória do mandante, empate, vitória do visitante), a partir do placar
  bruto de cada partida.

* **Insight:** transformar o placar numérico numa classe categórica é o que
  torna o problema tratável como classificação (em vez de regressão sobre o
  placar exato, que seria mais difícil de prever com poucos atributos
  disponíveis).

---

## 2. Restringir o escopo e juntar com o ranking FIFA

* **Objetivo:** aplicar o mesmo recorte de 2018/2022 usado nas Missões 1-3, e
  unir cada partida com a posição no ranking FIFA de cada seleção envolvida,
  criando os dois atributos que alimentam o modelo.

* **Código:**
```python
matches_filtrado = matches[matches['Year'].isin([2018, 2022])].copy()

matches_filtrado = matches_filtrado.merge(
    ranking_2022[['team', 'rank', 'points']], left_on='home_team', right_on='team'
).rename(columns={'rank': 'rank_home', 'points': 'points_home'}).drop(columns='team')

matches_filtrado = matches_filtrado.merge(
    ranking_2022[['team', 'rank', 'points']], left_on='away_team', right_on='team'
).rename(columns={'rank': 'rank_away', 'points': 'points_away'}).drop(columns='team')

matches_filtrado['diferenca_ranking'] = matches_filtrado['rank_away'] - matches_filtrado['rank_home']
matches_filtrado['diferenca_pontos'] = matches_filtrado['points_home'] - matches_filtrado['points_away']
```

* **Resultado:** dataset de 128 jogos com dois atributos numéricos —
  `diferenca_ranking` (quanto mais alto, mais o mandante é bem ranqueado que
  o visitante) e `diferenca_pontos` (idem, em pontos FIFA). A distribuição da
  variável-alvo confirmou o baseline já visto na Missão 1: 43% dos jogos são
  vitória do mandante — ou seja, um modelo que "sempre chuta mandante" já
  acerta 43% sem aprender nada.

* **Insight:** esse baseline de 43% é a régua mínima que o modelo precisa
  superar para provar que está aprendendo algo além do desbalanceamento
  natural das classes — não basta olhar a acurácia isolada, ela só tem
  significado quando comparada a esse piso.

---

## 3. Primeiro modelo: Random Forest com split treino/teste

* **Objetivo:** treinar um primeiro classificador simples (Random Forest) e
  medir sua acurácia contra o baseline.

* **Código:**
```python
X = matches_filtrado[['diferenca_ranking', 'diferenca_pontos']]
y = matches_filtrado['resultado']

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_treino, y_treino)
previsoes = modelo.predict(X_teste)
acuracia = accuracy_score(y_teste, previsoes)
```

* **Resultado:** treino com 96 jogos e teste com 32, com `stratify=y` para
  manter a proporção das 3 classes em ambos os conjuntos (essencial dado o
  tamanho pequeno do dataset).

* **Insight:** com apenas 128 jogos no total, um único split treino/teste é
  pouco confiável — o resultado da acurácia pode variar bastante dependendo
  de quais 32 jogos caíram no teste por acaso. Isso motiva o próximo passo
  (validação cruzada).

---

## 4. Validação cruzada (5 folds)

* **Objetivo:** obter uma medida de desempenho mais estável do que um único
  split, repetindo o treino/teste em 5 partições diferentes do mesmo dataset.

* **Código:**
```python
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(modelo, X, y, cv=cv, scoring='accuracy')
```

* **Resultado:** a acurácia média e o desvio-padrão entre as 5 partições
  (`StratifiedKFold` preserva a proporção das classes em cada fold) deram uma
  estimativa mais robusta do que o número isolado da seção anterior.

* **Insight:** o desvio-padrão entre folds importa tanto quanto a média — um
  desvio alto sinaliza que o modelo é sensível a quais jogos específicos
  caem em cada partição, o que é esperado com um dataset de apenas 128 jogos.

---

## 5. Comparação com Regressão Logística e importância dos atributos

* **Objetivo:** verificar se um modelo mais simples (Regressão Logística)
  performa de forma parecida ao Random Forest — o que sinalizaria que a
  relação entre os atributos e o resultado é majoritariamente linear — e
  inspecionar qual dos dois atributos pesa mais nas decisões do Random
  Forest.

* **Código:**
```python
modelo_simples = LogisticRegression(max_iter=1000)
scores_simples = cross_val_score(modelo_simples, X, y, cv=cv, scoring='accuracy')

modelo.fit(X, y)
importancias = pd.Series(modelo.feature_importances_, index=X.columns).sort_values(ascending=False)
```

* **Resultado:** a Regressão Logística ficou em patamar de acurácia
  comparável ao Random Forest neste dataset pequeno e com apenas 2
  atributos.

* **Insight:** com só 2 atributos numéricos e uma relação essencialmente
  monotônica (quanto maior a diferença de ranking/pontos, maior a chance de
  vitória do mandante), um modelo simples e linear captura quase toda a
  informação disponível — o Random Forest não tem atributos complexos ou
  não-lineares o suficiente para justificar sua maior capacidade. Isso pesou
  na escolha do modelo final (seção 8).

---

## 6. Avaliação por classe: classification report e matriz de confusão

* **Objetivo:** ir além da acurácia geral e entender o desempenho do modelo
  separadamente para cada classe — em especial o empate, que é a classe
  minoritária (22% dos jogos, segundo a Missão 1).

* **Código:**
```python
previsoes_cv = cross_val_predict(modelo_simples, X, y, cv=cv)
print(classification_report(y, previsoes_cv))
print(confusion_matrix(y, previsoes_cv, labels=['vitoria_mandante', 'empate', 'vitoria_visitante']))
```

* **Resultado:** o `classification_report` (precisão, recall e F1 por classe)
  e a matriz de confusão deixaram visível que a acurácia geral escondia um
  desempenho desigual entre as classes.

* **Insight:** esse é o ponto onde os conceitos de avaliação (precisão,
  recall, F1) se mostram mais úteis do que a acurácia isolada — um modelo
  pode acertar bem "vitória do mandante" (classe majoritária) e ainda assim
  quase nunca acertar "empate", e só a matriz de confusão revela esse
  desequilíbrio.

---

## 7. Teste com balanceamento de classes

* **Objetivo:** testar se dar mais peso à classe minoritária (empate) durante
  o treino melhora o recall dessa classe, mesmo que ao custo de acurácia
  geral.

* **Código:**
```python
modelo_balanceado = LogisticRegression(max_iter=1000, class_weight='balanced')
scores_balanceado = cross_val_score(modelo_balanceado, X, y, cv=cv, scoring='accuracy')
previsoes_balanceado = cross_val_predict(modelo_balanceado, X, y, cv=cv)
```

* **Resultado:** comparando os classification reports e matrizes de confusão
  do modelo balanceado com o modelo simples da seção 6, foi possível ver o
  trade-off explícito entre acurácia geral e recall da classe minoritária.

* **Insight:** balancear classes é uma decisão de negócio, não só técnica —
  depende de qual erro é mais custoso: errar um empate (recall baixo na
  classe minoritária) ou reduzir a acurácia geral do modelo. Documentar esse
  trade-off é mais importante do que simplesmente escolher o número mais
  alto.

---

## 8. Modelo final e aplicação à Copa 2026

* **Objetivo:** retreinar o modelo escolhido (Regressão Logística, sem
  balanceamento) usando todos os 128 jogos disponíveis, e aplicá-lo aos
  confrontos da Copa de 2026 para gerar probabilidades por resultado.

* **Código:**
```python
ranking_2026 = pd.read_csv('fifa_ranking_2026-06-08.csv')
schedule_2026 = pd.read_csv('schedule_2026.csv')

modelo_final = LogisticRegression(max_iter=1000)
modelo_final.fit(X, y)

schedule_com_ranking = schedule_2026.merge(
    ranking_2026[['team', 'rank', 'points']], left_on='home_team', right_on='team'
).rename(columns={'rank': 'rank_home', 'points': 'points_home'}).drop(columns='team')
# (merge equivalente para away_team)

X_2026 = schedule_com_ranking[['diferenca_ranking', 'diferenca_pontos']]
probabilidades = modelo_final.predict_proba(X_2026)
```

* **Resultado:** ao comparar a contagem de jogos do `schedule_2026` original
  com a contagem após o merge com o ranking, ficou visível que vários jogos
  foram perdidos no merge — sinal de nomes de seleção divergentes entre as
  duas fontes (ver seção 9).

* **Insight:** usar `predict_proba` em vez de `predict` foi uma escolha
  deliberada — para jogos futuros de Copa, uma probabilidade por resultado
  (ex: 55% mandante / 25% empate / 20% visitante) comunica a incerteza real
  do modelo muito melhor do que uma única classe prevista, especialmente
  dado o desvio-padrão já observado na validação cruzada.

---

## 9. Diagnóstico e correção de nomes divergentes entre bases

* **Objetivo:** identificar quais seleções do `schedule_2026` não bateram com
  o `ranking_2026` (e por isso "sumiram" no merge), e corrigir a causa raiz
  em vez de simplesmente descartar os jogos afetados.

* **Código:**
```python
times_schedule = set(schedule_2026['home_team']).union(set(schedule_2026['away_team']))
times_ranking = set(ranking_2026['team'])
print(times_schedule - times_ranking)

candidatos_usa = ranking_2026[ranking_2026['team'].str.contains('USA|U.S.|United', case=False, na=False)]

correcao_nomes = {
    'United States': 'USA',
    'Cape Verde': 'Cabo Verde',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
}
schedule_2026['home_team'] = schedule_2026['home_team'].replace(correcao_nomes)
schedule_2026['away_team'] = schedule_2026['away_team'].replace(correcao_nomes)
```

* **Resultado:** após a correção dos nomes (Estados Unidos, Cabo Verde e
  Bósnia-Herzegovina grafados de forma diferente nas duas bases), o número
  de jogos do `schedule_2026` após o merge voltou a bater com o total
  original — nenhum jogo foi perdido silenciosamente.

* **Insight:** essa etapa é uma continuação direta do problema de qualidade
  de dados já visto na Missão 2 (o bug do cartão amarelo duplicado) — um
  merge que "funciona sem erro" não significa que está correto; comparar a
  contagem de linhas antes e depois do merge é o jeito mais simples de
  detectar perda silenciosa de dados por divergência de chave.

* **Resultado final:** as previsões completas (probabilidade de vitória do
  mandante, empate e vitória do visitante para cada confronto da Copa 2026)
  foram salvas em `previsoes_copa_2026.csv`.

---

## Conclusão da Missão 4

O modelo final é uma Regressão Logística treinada sobre apenas 2 atributos
(diferença de ranking e de pontos FIFA entre as seleções), escolhida em vez
do Random Forest por performar de forma equivalente com uma relação mais
simples e interpretável entre os atributos e o resultado. O processo
percorreu o ciclo completo de avaliação — baseline, split simples, validação
cruzada, comparação de modelos, avaliação por classe (precisão/recall/F1),
teste de balanceamento — antes de aplicar o modelo aos jogos da Copa 2026,
incluindo o diagnóstico e correção de um problema real de qualidade de dados
(nomes de seleção divergentes entre bases). O modelo é deliberadamente
simples: ele captura o "favoritismo no papel", mas as Missões 1-2 já
mostraram, com o próprio caso do Brasil em 2022, que esse favoritismo tem
limites reais em jogos de mata-mata — o que o modelo reflete diretamente nas
probabilidades (nunca 100%/0%) em vez de prever um vencedor com certeza.
