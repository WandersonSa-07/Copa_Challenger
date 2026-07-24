# 🏆 Copa Challenger: Data Science & Machine Learning

**Autor:** Wanderson Souza Sá Filho  
**Status:** Concluído  

Este repositório contém a resolução completa do desafio **Copa Challenger**, um projeto *end-to-end* de Ciência de Dados focado na análise do histórico das Copas do Mundo (1930-2022) e na previsão de resultados para a fase de grupos da Copa de 2026.

O projeto foi dividido em quatro missões principais, varrendo desde a extração e estruturação dos dados até o deploy de um modelo de Inteligência Artificial.

---

## 🛠️ Tecnologias Utilizadas
* **Banco de Dados:** PostgreSQL e pgAdmin (SQL)
* **Linguagem:** Python
* **Análise e Manipulação:** Pandas
* **Visualização:** Matplotlib e Plotly
* **Machine Learning:** Scikit-Learn
* **Deploy e Dashboard:** Streamlit Community Cloud

---

## 🚀 Arquitetura do Projeto

### Missão 1: Engenharia de Dados (SQL)
* Construção do esquema do banco de dados relacional.
* Modelagem de tabelas utilizando dialeto PostgreSQL (`VARCHAR`, `INT`, `FLOAT`, `DATE`).
* Importação de arquivos brutos (CSV) e execução de consultas de perfilamento (*Data Profiling*) para validação de integridade, identificação de valores nulos e contagem de registros.

### Missão 2: Análise Exploratória de Dados (EDA)
* Filtragem do escopo analítico para as Copas de 2018 e 2022.
* **Público e Engajamento:** Identificação de *outliers* de público, comprovando a lotação máxima (88.966 espectadores) no Estádio Lusail no Catar, impulsionada pelo engajamento da torcida argentina.
* **Disciplina vs. Sobrevivência:** Análise correlacionando o acúmulo de cartões amarelos com o avanço de fases no torneio (Argentina, Croácia e França liderando a métrica).
* **A Ilusão do Favoritismo (xG):** Cruzamento de gols reais com a métrica de *Expected Goals* (xG). Destaque para o déficit de conversão do Brasil (-7.7 gols), ilustrado pelo estudo de caso do jogo Brasil x Croácia (2.5 xG vs 0.6 xG).

### Missão 3: Dashboard e Storytelling
* Link do dashboard: https://copachallenger-wandersonsouzasa.streamlit.app/
* Desenvolvimento de uma aplicação web interativa utilizando **Streamlit**.
* Criação de KPIs dinâmicos e plotagem de gráficos para comunicação visual dos insights gerados na etapa de EDA.
* Foco na experiência do usuário para facilitar a compreensão da disparidade entre criação ofensiva e conversão real.

### Missão 4: Machine Learning e Previsões (Copa 2026)
* **Engenharia de Atributos (Feature Engineering):** Geração de novas variáveis de entrada (`diferenca_ranking` e `diferenca_pontos`) baseadas no ranking oficial da FIFA.
* **Seleção de Modelo:** Comparação entre *Random Forest* e *Regressão Logística* utilizando Validação Cruzada (*StratifiedKFold*).
* **Avaliação da IA:** O modelo de Regressão Logística foi escolhido pela maior estabilidade (59% de acurácia média). Foram aplicados conceitos rigorosos de avaliação (*Precision*, *Recall* e *F1-Score*). 
* **Limitações e Aprendizados:** Identificou-se a limitação natural do modelo em prever "empates" (classe minoritária no futebol). Mesmo com o uso de `class_weight='balanced'`, a IA demonstrou que o futebol possui uma variância intrínseca que desafia a pura diferença de pontuação.
* **Inferência:** Aplicação do modelo treinado na tabela de jogos da Copa do Mundo de 2026, gerando o arquivo `previsoes_copa_2026.csv` com as probabilidades matemáticas de cada confronto.

---

## 📈 Como Executar o Dashboard Localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/WandersonSa-07/Copa_Challenger.git](https://github.com/WandersonSa-07/Copa_Challenger.git)
