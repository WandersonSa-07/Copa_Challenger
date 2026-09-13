# Relatório da Missão 1: Entendimento dos Dados

**Ferramentas:** PostgreSQL, pgAdmin e VS Code.

Essas parte consiste em explorar de maneira inicial o conjunto de dados do desafio buscando entender o dataset e encontrar alguns insights.

## 1. Contar quantas linhas cada tabela tem

* **Objetivo:** ter uma noção de escala das tabelas relevantes para o escopo do desafio (2018 e 2022) e perceber se alguma delas veio incompleta na importação.
* **Consulta SQL:**

```sql
SELECT 'matches' AS tabela, COUNT(*) FROM matches
UNION ALL
SELECT 'world_cups_history', COUNT(*) FROM world_cups_history
UNION ALL
SELECT 'fifa_ranking_2022', COUNT(*) FROM fifa_ranking_2022;
```

* **Resultado:** a tabela matches tem 964 partidas (de todas as Copas, 1930–2022), world_cups_history tem 22 edições, e fifa_ranking_2022 tem 211 seleções. 

* **Insight:** o volume de dados está consistente com o esperado (22 Copas realizadas entre 1930 e 2022, e 211 seleções filiadas à FIFA no ranking). As tabelas fifa_ranking_2026 e schedule_2026 existem no banco, mas ficam fora do escopo desta missão, pois elas dizem respeito à Copa de 2026 e serão retomadas na Missão 4.

## 2. Existe vantagem de jogar em casa?

* **Objetivo:** verificar se, historicamente, o time listado como "mandante" tem uma taxa de vitória maior  (um padrão clássico no futebol de clubes, mas que pode não se repetir em Copa do Mundo, já que "mandante" aqui normalmente não significa jogar no próprio país).

* **Consulta SQL:**
```sql
SELECT
    COUNT(*) FILTER (WHERE home_score > away_score) AS vitorias_mandante,
    COUNT(*) FILTER (WHERE home_score < away_score) AS vitorias_visitante,
    COUNT(*) FILTER (WHERE home_score = away_score) AS empates
FROM matches
WHERE year IN (2018, 2022);
```

* **Resultado:** em 128 jogos (Copas de 2018 e 2022), o mandante venceu 55 vezes (43%), o visitante venceu 45 vezes (35%) e houve 28 empates (22%).

* **Insight:** existe uma leve vantagem para o "mandante" (43% vs 35%), mas bem menor do que a observada em ligas de clubes — onde jogar em casa costuma passar de 45-50% de vitórias. Isso reforça a hipótese de que, em Copa do Mundo, "mandante" é só uma posição na tabela/chave do confronto, não um fator real de vantagem de campo (já que raramente é o país-sede jogando).


## 3. O campeão de 2018 e 2022 estava bem ranqueado?

* **Objetivo:** verificar se existe relação entre a posição no ranking FIFA antes da Copa e o time que efetivamente venceu o torneio — testando a hipótese de que "o favorito no papel tende a ser campeão".

* **Consulta SQL:**
```sql
SELECT wc.year, wc.champion, r.ranking AS ranking_pre_copa, r.points
FROM world_cups_history wc
JOIN fifa_ranking_2022 r ON r.team = wc.champion
WHERE wc.year = 2022;
```

* **Resultado:** em 2022, a Argentina foi campeã estando na 3ª posição do ranking FIFA, com 1773,88 pontos (ou seja, não era a 1ª colocada no papel).

* **Insight:** o campeão de 2022 (Argentina) não era o favorito número 1 do ranking FIFA pré-torneio (posição ocupada pelo Brasil, como confirmado na consulta seguinte). Isso sugere que, em Copa do Mundo, o ranking pré-torneio é um indicador de força relativa entre seleções, mas não é determinante: fases eliminatórias têm um componente de acaso/momento que o ranking não captura. Não foi possível replicar essa análise para 2018, pois o dataset não contém um ranking FIFA daquele período, apenas os rankings pré-2022 e pré-2026 (este último fora do escopo desta missão).


## 4. Favoritos em 2022

* **Objetivo:** identificar quais eram as 5 seleções mais bem ranqueadas pela FIFA antes da Copa de 2022, para comparar com quem realmente foi campeã.

* **Consulta SQL:**
```sql
SELECT team, r.ranking AS posicao, points
FROM fifa_ranking_2022 r
ORDER BY r.ranking ASC
LIMIT 5;
```

* **Resultado:** o top 5 do ranking FIFA pré-Copa 2022 era: Brasil (1º, 1841.3 pts), Bélgica (2º, 1816.71 pts), Argentina (3º, 1773.88 pts), França (4º, 1759.78 pts) e Inglaterra (5º, 1728.47 pts).

* **Insight:** o time favorito no ranking (Brasil) não foi o campeão, quem venceu foi a Argentina, a 3ª colocada. Isso reforça o insight anterior: ranking FIFA indica força relativa entre seleções, mas não é um preditor confiável do resultado final de mata-mata. Fatores como sorte de chaveamento, forma física no momento do torneio e jogos decididos em pênaltis pesam mais do que a pontuação acumulada ao longo dos anos.

## 5. Entender como o Brasil (primeiro colocado) saiu da copa de 2022?

* **Objetivo:** rastrear a trajetória do Brasil (favorito nº1 no ranking pré-Copa) na Copa de 2022, jogo a jogo, para identificar em que fase ele foi eliminado.

* **Consulta SQL:**
```sql
SELECT round, date, home_team, home_score, away_team, away_score
FROM matches
WHERE year = 2022
  AND (home_team = 'Brazil' OR away_team = 'Brazil')
ORDER BY date;
```

* **Resultado:** o Brasil venceu os 3 jogos da fase de grupos (2x0 Sérvia, 1x0 Suíça, e perdeu 1x0 para Camarões já classificado) e nas oitavas goleou a Coreia do Sul por 4x1. Nas quartas de final, empatou em 1x1 com a Croácia no tempo normal — sendo eliminado (o placar de 1x1 indica decisão nos pênaltis, já que era jogo eliminatório).

* **Insight:** o favorito nº1 do ranking FIFA (Brasil) teve campanha dominante na fase de grupos e oitavas, mas foi eliminado nas quartas de final em um jogo decidido nos pênaltis, ou seja, num confronto estatisticamente equilibrado (1x1), não por inferioridade técnica clara. Isso reforça o padrão observado nas consultas anteriores: o ranking FIFA prevê bem o desempenho ao longo da fase de grupos, mas perde poder preditivo em jogos únicos de mata-mata, onde jogos decididos nos pênaltis introduzem um elemento de acaso que nenhum ranking consegue capturar.
