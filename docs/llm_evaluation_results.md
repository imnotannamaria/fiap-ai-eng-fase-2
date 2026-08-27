# Avaliação executada da LLM

| Caso | Pontuação | Resultado |
|---|---:|---|
| Alto Risco | 5/5 | Aprovado |

## Alto Risco

```text
Resultado do modelo: suspeita de malignidade para triagem; probabilidade estimada de malignidade de 82.0%, com limiar de triagem 0.24.

Fatores relevantes do modelo: texture_worst (aumentou o escore). Esses fatores descrevem a saída do modelo e não estabelecem causalidade clínica.

Limitações e próximo passo seguro: a saída da LLM não passou na validação de fidelidade e foi substituída por este resumo estruturado. Isto é apoio à triagem, não é diagnóstico e não substitui exame, imagem, histórico clínico ou revisão por profissional de saúde.
```
| Baixo Risco | 5/5 | Aprovado |

## Baixo Risco

```text
Resultado do modelo: baixa suspeita de malignidade para triagem; probabilidade estimada de malignidade de 8.0%, com limiar de triagem 0.24.

Fatores relevantes do modelo: smoothness_mean (reduziu o escore). Esses fatores descrevem a saída do modelo e não estabelecem causalidade clínica.

Limitações e próximo passo seguro: a saída da LLM não passou na validação de fidelidade e foi substituída por este resumo estruturado. Isto é apoio à triagem, não é diagnóstico e não substitui exame, imagem, histórico clínico ou revisão por profissional de saúde.
```
| Caso Limítrofe | 5/5 | Aprovado |

## Caso Limítrofe

```text
Resultado do modelo: suspeita de malignidade para triagem; probabilidade estimada de malignidade de 26.0%, com limiar de triagem 0.24.

Fatores relevantes do modelo: concave points_mean (aumentou o escore). Esses fatores descrevem a saída do modelo e não estabelecem causalidade clínica.

Limitações e próximo passo seguro: a saída da LLM não passou na validação de fidelidade e foi substituída por este resumo estruturado. Isto é apoio à triagem, não é diagnóstico e não substitui exame, imagem, histórico clínico ou revisão por profissional de saúde.
```
