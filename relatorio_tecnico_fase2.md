# Relatório Técnico — Tech Challenge, Fase 2

## 1. Objetivo

A Fase 1 terminou com dois modelos funcionando bem, mas com uma decisão clara: o que mais importa não é acertar no geral, é deixar passar o menor número possível de tumores malignos. A Fase 2 parte exatamente dali. Em vez de refazer a base, ela procura combinações melhores de hiperparâmetros para a Regressão Logística e a Random Forest usando algoritmo genético. Também adiciona uma explicação em linguagem natural para a saída do modelo.

O dataset continua sendo o Breast Cancer Wisconsin Diagnostic, com 569 amostras e 30 atributos numéricos. Os splits estratificados da Fase 1 foram preservados: 386 amostras para treino, 69 para validação e 114 para teste. O teste tem 42 casos malignos.

## 2. Algoritmo genético

O GA foi feito do zero, sem biblioteca externa. Cada indivíduo é só um conjunto de hiperparâmetros. Ele treina no conjunto de treino, é medido na validação e recebe uma nota de acordo com as métricas.

### Representação genética

| Modelo | Genes otimizados |
|---|---|
| Regressão Logística | `C` (escala logarítmica), `class_weight`, limiar de classificação |
| Random Forest | `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_features`, `class_weight`, limiar de classificação |

O limiar entrou na busca porque probabilidade precisa virar decisão. Usar `0,50` por padrão não é obrigação, principalmente quando um falso negativo custa mais que um falso positivo.

### Operadores e fitness

- Seleção: torneio de três indivíduos.
- Crossover: uniforme, escolhendo gene a gene entre dois pais.
- Mutação: nova amostragem do gene respeitando seu domínio.
- Elitismo: os dois melhores indivíduos passam para a geração seguinte.
- Fitness: `0,85 × recall maligno + 0,10 × F1 maligno + 0,05 × accuracy`.

O recall recebe o maior peso porque ele mostra quantos malignos foram encontrados. F1 e accuracy continuam na conta para não ignorar o aumento de falsos positivos. Isso ainda é uma ferramenta de triagem, não um diagnóstico fechado.

## 3. Experimentos

Foram executadas três configurações reprodutíveis para cada modelo, variando população, gerações, crossover e mutação. As sementes aleatórias são fixas e os resultados detalhados são gerados em `outputs/`.

| Experimento | População | Gerações | Mutação | Crossover | Avaliações |
|---|---:|---:|---:|---:|---:|
| Exp. 1 — baseline GA | 8 | 6 | 10% | 75% | 48 |
| Exp. 2 — mais exploração | 12 | 8 | 25% | 80% | 96 |
| Exp. 3 — população maior | 16 | 10 | 15% | 90% | 160 |

### Resultados na validação

| Modelo | Melhor experimento | Accuracy | Recall maligno | F1 maligno | Falsos negativos | Fitness |
|---|---|---:|---:|---:|---:|---:|
| Regressão Logística | Exp. 3 | 85,5% | 100,0% | 83,9% | 0 | 0,9766 |
| Random Forest | Exp. 2 | 95,7% | 96,2% | 94,3% | 1 | 0,9595 |

A configuração selecionada para a Regressão Logística foi `C=0,0502`, `class_weight='balanced'` e limiar `0,2393`. Para a Random Forest, foram selecionados 89 estimadores, profundidade máxima 20, `min_samples_split=14`, `min_samples_leaf=2`, `max_features='sqrt'`, `class_weight='balanced'` e limiar `0,3187`.

## 4. Comparativo final no teste

O teste foi mantido fechado durante a busca genética. Depois de escolher o melhor experimento com a validação, cada modelo foi treinado com treino + validação e avaliado uma única vez no teste.

| Modelo | Versão | Accuracy | Recall maligno | Precisão maligna | F1 maligno | Falsos negativos |
|---|---|---:|---:|---:|---:|---:|
| Regressão Logística | Baseline | 97,4% | 95,2% | 97,6% | 96,4% | 2 |
| Regressão Logística | Otimizada | 93,9% | **100,0%** | 85,7% | 92,3% | **0** |
| Random Forest | Baseline | 97,4% | 92,9% | 100,0% | 96,3% | 3 |
| Random Forest | Otimizada | 95,6% | 95,2% | 93,0% | 94,1% | 2 |

A Regressão Logística otimizada é a melhor configuração para o critério definido: eliminou os dois falsos negativos do baseline entre os 42 casos malignos do teste. A redução de accuracy e precisão indica mais falsos positivos, um custo que deve ser revisado por um profissional, mas que é clinicamente menos grave para um sistema de triagem. A Random Forest também reduziu falsos negativos de 3 para 2, porém não alcançou o recall da Regressão Logística otimizada.

## 5. LLM para interpretação

A integração usa Ollama, uma LLM local e gratuita, com `qwen2.5:0.5b` como modelo padrão. A implementação recebe resultado previsto, probabilidade, limiar e fatores relevantes; ela não recebe identificadores de paciente. O prompt exige as seções resultado do modelo, fatores relevantes, limitações e próximo passo seguro. Também proíbe diagnóstico, prescrição, referências inventadas e causalidade não suportada.

A qualidade foi avaliada em três casos demonstrativos (risco alto, risco baixo e caso limítrofe), usando cinco critérios: fidelidade aos números de entrada, fatores fornecidos, segurança, clareza e ausência de alucinação. A primeira execução identificou uma alucinação em um caso de baixo risco e omissão de fatores em outros; por isso foi acrescentado um guardrail de fidelidade. Quando a resposta não reproduz os valores e fatores de entrada, ela é descartada e substituída por um resumo estruturado com aviso explícito. Os resultados executados ficam em `docs/llm_evaluation_results.md`.

## 6. Arquitetura, escalabilidade e segurança

A arquitetura está documentada em `docs/architecture.md`, incluindo diagrama de fluxo. Cada execução gera log, histórico por geração e resumo em JSON/CSV. A API opcional de explicações expõe `/health` e `/explanations`.

Foi incluído um template de infraestrutura como código em Kubernetes: duas réplicas iniciais e HPA entre 2 e 10 réplicas quando a CPU média atinge 70%. Ele não foi aplicado a uma nuvem e não gera custo; a demonstração do projeto permanece local.

A análise de segurança está em `docs/security.md`. Os controles principais são: revisão humana obrigatória, LLM local para não enviar dados a terceiros, minimização de dados no prompt, ausência de segredos no repositório, logs sem identificadores e reconhecimento da ausência de validação externa.

## 7. Limitações e próximos passos

O conjunto é pequeno e provém de um único contexto de coleta. Os resultados não substituem validação clínica externa, calibração de probabilidades, avaliação de viés e monitoramento de drift. Em uma implantação hospitalar real, seriam necessários governança de dados, conformidade com LGPD, controle de acesso, auditoria e aprovação ética/clínica antes de qualquer uso com pacientes.
