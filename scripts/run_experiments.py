"""Executa os três experimentos obrigatórios do algoritmo genético."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cancer_diagnosis.data import load_splits
from cancer_diagnosis.experiments import baseline_params, run_all_experiments
from cancer_diagnosis.models import fit_and_evaluate


def main() -> None:
    parser = argparse.ArgumentParser(description="Otimização por algoritmo genético")
    parser.add_argument(
        "--model",
        choices=("logistic_regression", "random_forest"),
        default="logistic_regression",
        help="Modelo a otimizar. Comece pela regressão logística, mais rápida.",
    )
    args = parser.parse_args()

    splits = load_splits(ROOT / "data" / "processed")
    x_train, y_train = splits["train"]
    x_val, y_val = splits["val"]
    x_test, y_test = splits["test"]
    output_dir = ROOT / "outputs" / args.model

    _, baseline_val = fit_and_evaluate(
        args.model, baseline_params(args.model), x_train, y_train, x_val, y_val, random_state=42
    )
    results = run_all_experiments(args.model, x_train, y_train, x_val, y_val, output_dir)
    best = max(results, key=lambda item: item["metrics_validation"]["fitness"])

    # O teste permanece fechado durante a busca: ele é usado apenas uma vez aqui,
    # após escolher a melhor configuração pela validação.
    # O baseline da Fase 1 também foi treinado só no split de treino. Mantemos
    # essa condição para que o comparativo não misture o efeito do GA com o de
    # acrescentar mais dados ao ajuste final.
    _, baseline_test = fit_and_evaluate(
        args.model,
        baseline_params(args.model),
        x_train,
        y_train,
        x_test,
        y_test,
        random_state=42,
    )
    _, optimized_test = fit_and_evaluate(
        args.model,
        best["best_params"],
        x_train,
        y_train,
        x_test,
        y_test,
        random_state=42,
    )
    comparison = {
        "model": args.model,
        "baseline_validation": baseline_val.as_dict(),
        "selected_experiment": best["experiment"],
        "selected_params": best["best_params"],
        "baseline_test": baseline_test.as_dict(),
        "optimized_test": optimized_test.as_dict(),
    }
    (output_dir / "final_comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
