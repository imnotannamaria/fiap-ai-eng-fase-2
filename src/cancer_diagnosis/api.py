"""API opcional para expor explicações da LLM em uma futura implantação."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from cancer_diagnosis.llm import OllamaClient, PredictionContext


app = FastAPI(
    title="Cancer Diagnosis Explanation API",
    version="0.1.0",
    description="API de apoio à triagem. Não é um sistema de diagnóstico clínico.",
)


class ExplanationRequest(BaseModel):
    model_name: str = Field(max_length=100)
    predicted_label: str = Field(max_length=100)
    probability_malignant: float = Field(ge=0, le=1)
    threshold: float = Field(gt=0, lt=1)
    top_features: list[dict[str, str]] = Field(max_length=10)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "llm-explanation-api"}


@app.post("/explanations")
def create_explanation(request: ExplanationRequest) -> dict[str, str]:
    context = PredictionContext(**request.model_dump())
    try:
        explanation = OllamaClient().explain(context)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"explanation": explanation, "disclaimer": "Apoio à triagem; revisão profissional obrigatória."}
