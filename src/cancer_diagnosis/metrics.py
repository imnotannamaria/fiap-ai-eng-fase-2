"""Métricas clínicas e fitness usadas durante a otimização."""

from dataclasses import asdict, dataclass

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    recall_malignant: float
    precision_malignant: float
    f1_malignant: float
    false_negatives: int
    fitness: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


def calculate_metrics(y_true, probabilities, threshold: float = 0.5) -> ClassificationMetrics:
    """Calcula métricas com maligno (1) como classe positiva.

    A fitness prioriza recall, pois um falso negativo é o erro mais grave
    para o objetivo de triagem deste projeto. F1 e accuracy evitam que a busca
    aceite configurações que marquem todos os casos como malignos.
    """
    if not 0 < threshold < 1:
        raise ValueError("O limiar de decisão deve estar entre 0 e 1.")

    y_true = np.asarray(y_true)
    y_pred = (np.asarray(probabilities) >= threshold).astype(int)
    recall = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    precision = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)
    false_negatives = int(((y_true == 1) & (y_pred == 0)).sum())
    fitness = 0.85 * recall + 0.10 * f1 + 0.05 * accuracy

    return ClassificationMetrics(
        accuracy=float(accuracy),
        recall_malignant=float(recall),
        precision_malignant=float(precision),
        f1_malignant=float(f1),
        false_negatives=false_negatives,
        fitness=float(fitness),
    )
