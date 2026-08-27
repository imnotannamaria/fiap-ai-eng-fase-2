# Diagnóstico de Câncer de Mama: Tech Challenge B

> Fase 2 — otimização por algoritmos genéticos e explicações por LLM local.

Projeto de Machine Learning para classificar tumores de mama como malignos ou benignos a partir de medições extraídas de biópsias por agulha fina.

Dataset: Breast Cancer Wisconsin (UCI), 569 amostras, 30 features numéricas.

Modelo final: Regressão Logística. 97,4% de accuracy no teste, 95,2% de recall para a classe maligna, 2 falsos negativos de 42.

---

## O problema

O dataset contém medições de células extraídas de imagens de biópsias. Cada amostra tem 30 features (raio, textura, perímetro, área e derivados), medidas em três formas: média, erro padrão e o valor mais extremo encontrado. O objetivo é classificar o tumor como maligno (M) ou benigno (B).

A métrica principal não é accuracy. No contexto médico, um falso negativo (dizer que é benigno quando é maligno) é muito mais grave que um falso positivo. Por isso o modelo foi escolhido com base no **recall da classe maligna**.

---

## O que mudou da Fase 1 para a Fase 2

Na Fase 1, o foco foi sair do dado bruto e chegar num modelo que fizesse sentido para o problema. Foram feitas EDA, limpeza, splits de treino/validação/teste, normalização, comparação entre Regressão Logística e Random Forest e explicabilidade com SHAP. A Regressão Logística foi escolhida porque deixou passar menos casos malignos.

Na Fase 2, a base não foi refeita. Os mesmos splits foram mantidos e os dois modelos passaram por otimização de hiperparâmetros com algoritmo genético. Entraram também logs dos experimentos, testes automatizados, uma API pequena para as explicações, uma LLM rodando localmente, documentação de arquitetura, análise de segurança e um template de escalabilidade automática. A ideia continua a mesma: ajudar na triagem, não substituir quem vai olhar o caso.

---

## Notebooks

Os notebooks seguem uma ordem e precisam ser rodados em sequência:

| Notebook | O que faz |
|---|---|
| `01_eda.ipynb` | Análise exploratória: distribuições, correlações, separação entre classes |
| `02_preprocessing.ipynb` | Normalização, divisão treino/val/teste, pipeline de pré-processamento |
| `03_modeling.ipynb` | Treino de Regressão Logística e Random Forest, comparação, avaliação no teste |
| `04_explainability.ipynb` | Feature importance, SHAP values, análise de um falso negativo |

---

## Resultados

| Modelo | Accuracy | Recall (M) | Precision (M) | Falsos negativos |
|---|---|---|---|---|
| Regressão Logística | 97,4% | 95,2% | 97,6% | 2 de 42 |
| Random Forest | 97,4% | 92,9% | 100,0% | 3 de 42 |

Mesma accuracy, erros em lugares diferentes. O RF não gerou nenhum falso positivo, mas deixou passar mais malignos. A Logística foi escolhida por ter menos falsos negativos.

As features mais relevantes nas predições foram `texture_worst`, `concave points_mean`, `concave points_worst` e `area_worst`, que são características de irregularidade e tamanho das células nas regiões mais atípicas do tumor.

---

## Gráficos

Os notebooks salvam todos os gráficos na pasta `figures/`. Os principais estão abaixo.

**Distribuição das classes**
![Distribuição das classes](figures/01_target_distribution.png)

**Matrizes de confusão no teste**
![Matrizes de confusão no teste](figures/09_confusion_matrices_test.png)

**Feature importance (Random Forest)**
![Feature importance](figures/10_feature_importance_rf.png)

**SHAP summary (Regressão Logística)**
![SHAP summary](figures/12_shap_summary_lr.png)

<!-- INSERIR IMAGEM: adicione aqui outras figuras da pasta figures/ que quiser destacar -->

---

## Como rodar

**Local**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Rodar em ordem: `01_eda`, depois `02_preprocessing`, `03_modeling` e `04_explainability`.

O dataset `data/data.csv` precisa estar presente antes de começar. Download em [kaggle.com/datasets/uciml/breast-cancer-wisconsindata](https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsindata/data).

**Docker**

```bash
docker build -t cancer-diagnosis .
docker run -p 8888:8888 -v $(pwd):/app cancer-diagnosis
```

Acesse `http://localhost:8888`.

---

## Fase 2: otimização e interpretação

Esta etapa mantém os dados e modelos da Fase 1 e adiciona uma camada de otimização reproduzível. A Regressão Logística e a Random Forest têm hiperparâmetros representados como genes; o algoritmo realiza seleção por torneio, crossover uniforme, mutação e elitismo.

A função de fitness prioriza o recall de tumores malignos: `0,85 × recall + 0,10 × F1 + 0,05 × accuracy`. Assim, reduzir falsos negativos é mais importante que preservar a accuracy isoladamente.

Com o ambiente virtual ativado, execute os três experimentos obrigatórios:

```bash
python scripts/run_experiments.py --model logistic_regression
python scripts/run_experiments.py --model random_forest
```

Cada comando salva logs, histórico por geração, resumo CSV e comparação final em `outputs/`. O teste é usado somente depois de escolher a melhor configuração pela validação.

### Explicação em linguagem natural

Instale o Ollama e baixe um modelo local:

```bash
ollama pull qwen2.5:0.5b
python scripts/demo_llm.py
```

O prompt e a rubrica de avaliação estão em [docs/llm.md](docs/llm.md). A LLM explica a predição para apoio à triagem e nunca deve diagnosticar ou prescrever.

### Documentação da Fase 2

- [Arquitetura e escalabilidade](docs/architecture.md)
- [Segurança e uso responsável](docs/security.md)
- [Integração e avaliação da LLM](docs/llm.md)
- [API de explicações](docs/api.md)
- [Template Kubernetes com HPA](infra/kubernetes/README.md)

---

## Estrutura

```
├── data/
│   ├── data.csv                  # dataset original (baixar do Kaggle)
│   └── processed/                # splits gerados pelo 02_preprocessing
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
├── figures/                      # gráficos gerados pelos notebooks
├── models/                       # modelos e pipeline serializados (.pkl)
├── src/cancer_diagnosis/          # GA, métricas, LLM local e API
├── scripts/run_experiments.py     # três experimentos e comparativo final
├── tests/                         # testes automatizados
├── docs/                          # arquitetura, segurança, LLM e API
├── infra/kubernetes/              # template de escalabilidade automática
├── 01_eda.ipynb
├── 02_preprocessing.ipynb
├── 03_modeling.ipynb
├── 04_explainability.ipynb
├── relatorio_tecnico.md
├── requirements.txt
└── Dockerfile
```
