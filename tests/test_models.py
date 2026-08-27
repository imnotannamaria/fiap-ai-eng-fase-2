from cancer_diagnosis.experiments import baseline_params
from cancer_diagnosis.models import build_model


def test_logistic_baseline_uses_the_same_solver_configuration_as_phase_one():
    model = build_model("logistic_regression", baseline_params("logistic_regression"), random_state=42)
    classifier = model.named_steps["classifier"]

    assert classifier.solver == "lbfgs"
    assert classifier.max_iter == 1000
