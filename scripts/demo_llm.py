"""Demonstra a geração de uma explicação com a LLM local."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cancer_diagnosis.llm import OllamaClient, PredictionContext


def main() -> None:
    # Caso demonstrativo anonimizado. Não corresponde a um paciente real.
    context = PredictionContext(
        model_name="Regressão Logística otimizada por GA",
        predicted_label="suspeita de malignidade para triagem",
        probability_malignant=0.82,
        threshold=0.24,
        top_features=[
            {"feature": "texture_worst", "direction": "aumentou o escore do modelo"},
            {"feature": "concave points_mean", "direction": "aumentou o escore do modelo"},
            {"feature": "area_worst", "direction": "aumentou o escore do modelo"},
        ],
    )
    print(OllamaClient().explain(context))


if __name__ == "__main__":
    main()
