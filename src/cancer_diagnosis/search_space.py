"""Codificação genética dos hiperparâmetros dos classificadores."""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np


GeneKind = Literal["float", "int", "choice", "log_float"]


@dataclass(frozen=True)
class Gene:
    """Um gene e o conjunto de valores que ele pode representar."""

    name: str
    kind: GeneKind
    values: tuple[Any, ...]

    def sample(self, rng: np.random.Generator) -> Any:
        if self.kind == "choice":
            return self.values[int(rng.integers(len(self.values)))]
        low, high = self.values
        if self.kind == "int":
            return int(rng.integers(low, high + 1))
        if self.kind == "log_float":
            return float(10 ** rng.uniform(np.log10(low), np.log10(high)))
        return float(rng.uniform(low, high))


LOGISTIC_REGRESSION_SPACE = (
    Gene("C", "log_float", (0.01, 10.0)),
    Gene("class_weight", "choice", (None, "balanced")),
    Gene("threshold", "float", (0.20, 0.65)),
)

RANDOM_FOREST_SPACE = (
    Gene("n_estimators", "int", (50, 150)),
    Gene("max_depth", "choice", (None, 3, 5, 8, 12, 16, 20)),
    Gene("min_samples_split", "int", (2, 14)),
    Gene("min_samples_leaf", "int", (1, 8)),
    Gene("max_features", "choice", ("sqrt", "log2", None)),
    Gene("class_weight", "choice", (None, "balanced")),
    Gene("threshold", "float", (0.20, 0.65)),
)


def get_search_space(model_name: str) -> tuple[Gene, ...]:
    spaces = {
        "logistic_regression": LOGISTIC_REGRESSION_SPACE,
        "random_forest": RANDOM_FOREST_SPACE,
    }
    try:
        return spaces[model_name]
    except KeyError as exc:
        raise ValueError(f"Modelo não suportado: {model_name}") from exc
