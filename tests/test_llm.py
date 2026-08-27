from cancer_diagnosis.llm import PredictionContext, SYSTEM_PROMPT, _is_grounded


def test_llm_prompt_is_deidentified_and_contains_required_context():
    context = PredictionContext(
        predicted_label="suspeita de malignidade",
        probability_malignant=0.82,
        threshold=0.40,
        top_features=[{"feature": "texture_worst", "direction": "aumentou o escore"}],
        model_name="Regressão Logística otimizada",
    )
    prompt = context.to_prompt()

    assert "82.0%" in prompt
    assert "texture_worst" in prompt
    assert "diagnóstico" in SYSTEM_PROMPT.lower()
    assert "não substitui" in SYSTEM_PROMPT.lower()
    assert "EXATAMENTE" in SYSTEM_PROMPT


def test_grounding_check_rejects_hallucinated_or_incomplete_response():
    context = PredictionContext(
        predicted_label="suspeita", probability_malignant=0.82, threshold=0.24,
        top_features=[{"feature": "texture_worst", "direction": "aumentou"}], model_name="modelo"
    )

    assert not _is_grounded("Probabilidade de 82.0% para triagem de cães.", context)
    assert _is_grounded("82.0% com texture_worst como fator relevante.", context)
