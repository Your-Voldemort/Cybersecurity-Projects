"""
©AngelaMos | 2026
test_config_ml.py
"""

from app.config import settings


def test_default_detection_mode_is_rules() -> None:
    assert settings.detection_mode == "rules"


def test_default_ensemble_weights_sum_to_one() -> None:
    total = (
        settings.ensemble_weight_ae
        + settings.ensemble_weight_rf
        + settings.ensemble_weight_if
    )
    assert abs(total - 1.0) < 1e-6


def test_default_model_dir() -> None:
    assert settings.model_dir == "data/models"


def test_default_ae_threshold_percentile() -> None:
    assert settings.ae_threshold_percentile == 99.5


def test_default_mlflow_tracking_uri() -> None:
    assert settings.mlflow_tracking_uri == "file:./mlruns"
