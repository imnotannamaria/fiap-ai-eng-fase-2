"""Configurações reprodutíveis dos experimentos do algoritmo genético."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GAConfig:
    """Parâmetros de execução do algoritmo genético."""

    name: str
    population_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism_size: int = 2
    tournament_size: int = 3
    random_state: int = 42


EXPERIMENTS = (
    GAConfig(
        name="exp_01_baseline_ga",
        population_size=8,
        generations=6,
        mutation_rate=0.10,
        crossover_rate=0.75,
        random_state=42,
    ),
    GAConfig(
        name="exp_02_more_exploration",
        population_size=12,
        generations=8,
        mutation_rate=0.25,
        crossover_rate=0.80,
        random_state=43,
    ),
    GAConfig(
        name="exp_03_larger_population",
        population_size=16,
        generations=10,
        mutation_rate=0.15,
        crossover_rate=0.90,
        random_state=44,
    ),
)
