# API de explicações

Esta API é opcional para a demonstração, mas mostra como a explicação da LLM pode ser exposta separadamente do processo pesado de otimização.

Com o ambiente ativado e o Ollama em execução:

```bash
uvicorn cancer_diagnosis.api:app --app-dir src --reload
```

Abra `http://127.0.0.1:8000/docs` para a documentação interativa. A rota `POST /explanations` recebe o resultado já produzido pelo modelo e fatores relevantes sem qualquer identificador do paciente.

Exemplo de corpo da requisição:

```json
{
  "model_name": "Regressão Logística otimizada por GA",
  "predicted_label": "suspeita de malignidade para triagem",
  "probability_malignant": 0.82,
  "threshold": 0.24,
  "top_features": [
    {"feature": "texture_worst", "direction": "aumentou o escore do modelo"}
  ]
}
```
