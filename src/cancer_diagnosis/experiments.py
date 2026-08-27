"""Orquestra os experimentos e registra artefatos reproduzíveis."""

import csv
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cancer_diagnosis.config import EXPERIMENTS, GAConfig
from cancer_diagnosis.genetic_algorithm import GeneticOptimizer
from cancer_diagnosis.models import fit_and_evaluate
from cancer_diagnosis.search_space import get_search_space


def configure_logging(log_path: str | Path) -> logging.Logger:
    """Cria um log em arquivo para acompanhar desempenho e auditoria."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("cancer_diagnosis.optimization")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger


def baseline_params(model_name: str) -> dict[str, Any]:
    if model_name == "logistic_regression":
        return {"C": 1.0, "class_weight": None, "threshold": 0.5}
    if model_name == "random_forest":
        return {
            "n_estimators": 200,
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "sqrt",
            "class_weight": None,
            "threshold": 0.5,
        }
    raise ValueError(f"Modelo não suportado: {model_name}")


def run_experiment(
    model_name: str,
    config: GAConfig,
    x_train,
    y_train,
    x_val,
    y_val,
    logger: logging.Logger,
) -> dict[str, Any]:
    """Executa uma configuração do GA apenas contra o conjunto de validação."""
    logger.info(
        "Iniciando %s | modelo=%s | pop=%s | geracoes=%s | mutacao=%.2f | crossover=%.2f",
        config.name,
        model_name,
        config.population_size,
        config.generations,
        config.mutation_rate,
        config.crossover_rate,
    )
    evaluations = 0

    def fitness(individual: dict[str, Any]) -> float:
        nonlocal evaluations
        _, metrics = fit_and_evaluate(
            model_name, individual, x_train, y_train, x_val, y_val, config.random_state
        )
        evaluations += 1
        return metrics.fitness

    optimizer = GeneticOptimizer(get_search_space(model_name), config)
    result = optimizer.run(fitness)
    _, metrics = fit_and_evaluate(
        model_name, result.best_individual, x_train, y_train, x_val, y_val, config.random_state
    )
    logger.info(
        "Finalizado %s | fitness=%.4f | recall=%.4f | F1=%.4f | FN=%s | avaliacoes=%s",
        config.name,
        metrics.fitness,
        metrics.recall_malignant,
        metrics.f1_malignant,
        metrics.false_negatives,
        evaluations,
    )
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model": model_name,
        "experiment": config.name,
        "ga_config": config.__dict__,
        "best_params": result.best_individual,
        "metrics_validation": metrics.as_dict(),
        "evaluations": evaluations,
        "generation_history": [record.as_dict() for record in result.history],
    }


def run_all_experiments(
    model_name: str,
    x_train,
    y_train,
    x_val,
    y_val,
    output_dir: str | Path,
    configs: tuple[GAConfig, ...] = EXPERIMENTS,
) -> list[dict[str, Any]]:
    """Executa os três experimentos obrigatórios e salva JSON + resumo CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(output_dir / "optimization.log")
    results = [
        run_experiment(model_name, config, x_train, y_train, x_val, y_val, logger)
        for config in configs
    ]
    (output_dir / f"{model_name}_experiments.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    rows = []
    for result in results:
        rows.append(
            {
                "model": result["model"],
                "experiment": result["experiment"],
                "evaluations": result["evaluations"],
                **result["ga_config"],
                **result["metrics_validation"],
                "best_params": json.dumps(result["best_params"], ensure_ascii=False),
            }
        )
    with (output_dir / f"{model_name}_summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return results
