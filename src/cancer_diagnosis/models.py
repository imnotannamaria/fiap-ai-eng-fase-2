"""Criação e avaliação de modelos com o mesmo pré-processamento da Fase 1."""

from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from cancer_diagnosis.metrics import ClassificationMetrics, calculate_metrics


def build_model(model_name: str, params: dict[str, Any], random_state: int):
    """Cria um classificador a partir de um cromossomo já decodificado."""
    params = {key: value for key, value in params.items() if key != "threshold"}
    if model_name == "logistic_regression":
        classifier = LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            **params,
        )
    elif model_name == "random_forest":
        classifier = RandomForestClassifier(
            random_state=random_state,
            n_jobs=-1,
            **params,
        )
    else:
        raise ValueError(f"Modelo não suportado: {model_name}")
    return Pipeline([("scaler", StandardScaler()), ("classifier", classifier)])


def fit_and_evaluate(
    model_name: str,
    params: dict[str, Any],
    x_train,
    y_train,
    x_eval,
    y_eval,
    random_state: int,
) -> tuple[Pipeline, ClassificationMetrics]:
    """Treina somente no treino e avalia no split recebido."""
    model = build_model(model_name, params, random_state)
    model.fit(x_train, y_train)
    probabilities = np.asarray(model.predict_proba(x_eval)[:, 1])
    metrics = calculate_metrics(y_eval, probabilities, float(params.get("threshold", 0.5)))
    return model, metrics
