import numpy as np

from cancer_diagnosis.metrics import calculate_metrics


def test_metrics_prioritize_malignant_recall_and_count_false_negatives():
    metrics = calculate_metrics(
        y_true=np.array([1, 1, 0, 0]),
        probabilities=np.array([0.9, 0.3, 0.7, 0.1]),
        threshold=0.5,
    )

    assert metrics.recall_malignant == 0.5
    assert metrics.false_negatives == 1
    assert 0 < metrics.fitness < 1


def test_metrics_reject_invalid_threshold():
    try:
        calculate_metrics([0, 1], [0.1, 0.9], threshold=1.0)
    except ValueError as error:
        assert "limiar" in str(error)
    else:
        raise AssertionError("Era esperado ValueError para limiar inválido")
