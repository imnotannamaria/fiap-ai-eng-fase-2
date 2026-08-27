"""Cliente local do Ollama e prompt seguro para explicar uma predição."""

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


SYSTEM_PROMPT = """Você é um assistente de apoio à triagem clínica.
Explique resultados de um modelo de classificação de câncer de mama para
profissionais de saúde, em português do Brasil. Nunca faça diagnóstico,
prescrição ou recomendação de tratamento. Use apenas os dados fornecidos; não
invente causalidade nem referências. Responda em até 110 palavras e siga
EXATAMENTE este formato:
Resultado do modelo: ...
Fatores relevantes: ...
Limitações: isto é apoio à triagem e não substitui exame, imagem, histórico ou revisão profissional.
Próximo passo seguro: revisão por profissional de saúde."""


@dataclass(frozen=True)
class PredictionContext:
    predicted_label: str
    probability_malignant: float
    threshold: float
    top_features: list[dict[str, Any]]
    model_name: str

    def to_prompt(self) -> str:
        return (
            f"Modelo: {self.model_name}\n"
            f"Classificação prevista: {self.predicted_label}\n"
            f"Probabilidade estimada de malignidade: {self.probability_malignant:.1%}\n"
            f"Limiar de triagem: {self.threshold:.2f}\n"
            f"Fatores do modelo (não são causalidade): {json.dumps(self.top_features, ensure_ascii=False)}\n"
            "Gere uma explicação concisa seguindo as regras do sistema."
        )


class OllamaClient:
    """Cliente mínimo para uma LLM local; não envia dados para serviços externos."""

    def __init__(self, model: str = "qwen2.5:0.5b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def explain(self, context: PredictionContext, timeout: int = 120) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "system": SYSTEM_PROMPT,
                "prompt": context.to_prompt(),
                "stream": False,
                "options": {"temperature": 0.2},
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            raise RuntimeError(
                "Não foi possível conectar ao Ollama. Instale-o, inicie o serviço e baixe o modelo indicado em docs/llm.md."
            ) from exc
        if not body.get("response"):
            raise RuntimeError("Ollama retornou uma resposta vazia.")
        response = str(body["response"]).strip()
        if not _is_grounded(response, context):
            return _grounded_fallback(context)
        return _with_safety_disclaimer(response)


def _is_grounded(response: str, context: PredictionContext) -> bool:
    """Evita expor texto da LLM que diverge dos dados estruturados de entrada."""
    normalized = response.lower()
    unsafe_terms = ("cães", "prescri", "tratamento", "medicamento", "diagnóstico definitivo")
    return (
        f"{context.probability_malignant:.1%}" in response
        and all(item["feature"].lower() in normalized for item in context.top_features)
        and not any(term in normalized for term in unsafe_terms)
    )


def _with_safety_disclaimer(response: str) -> str:
    return (
        f"{response}\n\n"
        "Limitações e próximo passo seguro: esta explicação é apoio à triagem, "
        "não é diagnóstico e não substitui exame, imagem, histórico clínico ou "
        "revisão por profissional de saúde."
    )


def _grounded_fallback(context: PredictionContext) -> str:
    factors = "; ".join(
        f"{item['feature']} ({item['direction']})" for item in context.top_features
    )
    return (
        f"Resultado do modelo: {context.predicted_label}; probabilidade estimada de malignidade "
        f"de {context.probability_malignant:.1%}, com limiar de triagem {context.threshold:.2f}.\n\n"
        f"Fatores relevantes do modelo: {factors}. Esses fatores descrevem a saída do modelo e "
        "não estabelecem causalidade clínica.\n\n"
        "Limitações e próximo passo seguro: a saída da LLM não passou na validação de fidelidade "
        "e foi substituída por este resumo estruturado. Isto é apoio à triagem, não é diagnóstico "
        "e não substitui exame, imagem, histórico clínico ou revisão por profissional de saúde."
    )
