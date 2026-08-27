from cancer_diagnosis.config import GAConfig
from cancer_diagnosis.genetic_algorithm import GeneticOptimizer
from cancer_diagnosis.search_space import Gene


def test_genetic_optimizer_keeps_gene_values_in_search_space():
    config = GAConfig(
        name="test", population_size=6, generations=4, mutation_rate=0.2, crossover_rate=0.8
    )
    optimizer = GeneticOptimizer((Gene("value", "int", (1, 5)),), config)
    result = optimizer.run(lambda individual: float(individual["value"]))

    assert len(result.history) == 4
    assert 1 <= result.best_individual["value"] <= 5
    assert result.best_fitness == result.best_individual["value"]
