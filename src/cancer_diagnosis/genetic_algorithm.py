"""Algoritmo genético simples, auditável e específico para hiperparâmetros."""

from dataclasses import asdict, dataclass
from typing import Any, Callable

import numpy as np

from cancer_diagnosis.config import GAConfig
from cancer_diagnosis.search_space import Gene


Individual = dict[str, Any]
FitnessFunction = Callable[[Individual], float]


@dataclass(frozen=True)
class GenerationRecord:
    generation: int
    best_fitness: float
    mean_fitness: float
    best_individual: Individual

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GAResult:
    best_individual: Individual
    best_fitness: float
    history: list[GenerationRecord]


class GeneticOptimizer:
    """Implementa população, torneio, crossover uniforme, mutação e elitismo."""

    def __init__(self, genes: tuple[Gene, ...], config: GAConfig):
        self.genes = genes
        self.config = config
        self.rng = np.random.default_rng(config.random_state)

    def _new_individual(self) -> Individual:
        return {gene.name: gene.sample(self.rng) for gene in self.genes}

    def _tournament(self, population: list[Individual], scores: list[float]) -> Individual:
        candidates = self.rng.choice(len(population), size=self.config.tournament_size, replace=False)
        winner_index = max(candidates, key=lambda index: scores[index])
        return population[int(winner_index)].copy()

    def _crossover(self, parent_a: Individual, parent_b: Individual) -> tuple[Individual, Individual]:
        if self.rng.random() > self.config.crossover_rate:
            return parent_a.copy(), parent_b.copy()
        child_a, child_b = {}, {}
        for gene in self.genes:
            if self.rng.random() < 0.5:
                child_a[gene.name], child_b[gene.name] = parent_a[gene.name], parent_b[gene.name]
            else:
                child_a[gene.name], child_b[gene.name] = parent_b[gene.name], parent_a[gene.name]
        return child_a, child_b

    def _mutate(self, individual: Individual) -> Individual:
        child = individual.copy()
        for gene in self.genes:
            if self.rng.random() < self.config.mutation_rate:
                child[gene.name] = gene.sample(self.rng)
        return child

    def run(self, fitness_function: FitnessFunction) -> GAResult:
        population = [self._new_individual() for _ in range(self.config.population_size)]
        history: list[GenerationRecord] = []
        overall_best: Individual | None = None
        overall_fitness = float("-inf")

        for generation in range(self.config.generations):
            scores = [float(fitness_function(individual)) for individual in population]
            ranked = sorted(zip(population, scores), key=lambda item: item[1], reverse=True)
            best_individual, best_fitness = ranked[0]
            if best_fitness > overall_fitness:
                overall_best, overall_fitness = best_individual.copy(), best_fitness
            history.append(
                GenerationRecord(
                    generation=generation + 1,
                    best_fitness=best_fitness,
                    mean_fitness=float(np.mean(scores)),
                    best_individual=best_individual.copy(),
                )
            )

            next_population = [item[0].copy() for item in ranked[: self.config.elitism_size]]
            while len(next_population) < self.config.population_size:
                parent_a = self._tournament(population, scores)
                parent_b = self._tournament(population, scores)
                child_a, child_b = self._crossover(parent_a, parent_b)
                next_population.append(self._mutate(child_a))
                if len(next_population) < self.config.population_size:
                    next_population.append(self._mutate(child_b))
            population = next_population

        assert overall_best is not None
        return GAResult(overall_best, overall_fitness, history)
