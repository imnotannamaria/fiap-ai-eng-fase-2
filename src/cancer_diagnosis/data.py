"""Leitura dos splits já criados na Fase 1, sem refazer a separação dos dados."""

from pathlib import Path

import pandas as pd


TARGET_COLUMN = "diagnosis"


def load_split(path: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    """Carrega um CSV processado e separa as features do diagnóstico."""
    frame = pd.read_csv(path)
    if TARGET_COLUMN not in frame:
        raise ValueError(f"Coluna alvo '{TARGET_COLUMN}' não encontrada em {path}.")
    return frame.drop(columns=TARGET_COLUMN), frame[TARGET_COLUMN]


def load_splits(data_dir: str | Path) -> dict[str, tuple[pd.DataFrame, pd.Series]]:
    """Carrega treino, validação e teste a partir de ``data/processed``."""
    base_path = Path(data_dir)
    return {
        split: load_split(base_path / f"{split}.csv")
        for split in ("train", "val", "test")
    }
