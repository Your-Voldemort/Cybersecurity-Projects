"""
©AngelaMos | 2026
test_training.py
"""

import numpy as np
import pytest

from ml.train_autoencoder import train_autoencoder
from ml.train_classifiers import train_isolation_forest, train_random_forest


class TestAutoencoderTraining:

    @pytest.fixture
    def normal_data(self) -> np.ndarray:
        rng = np.random.default_rng(42)
        return (rng.standard_normal((300, 35)) * 0.3 + 0.5).astype(np.float32).clip(0, 1)

    def test_returns_model_and_threshold(self, normal_data: np.ndarray) -> None:
        result = train_autoencoder(normal_data, epochs=5, batch_size=32)
        assert "model" in result
        assert "threshold" in result
        assert "scaler" in result
        assert "history" in result

    def test_threshold_is_positive(self, normal_data: np.ndarray) -> None:
        result = train_autoencoder(normal_data, epochs=5, batch_size=32)
        assert result["threshold"] > 0.0

    def test_history_has_train_loss(self, normal_data: np.ndarray) -> None:
        result = train_autoencoder(normal_data, epochs=5, batch_size=32)
        assert "train_loss" in result["history"]
        assert len(result["history"]["train_loss"]) == 5

    def test_custom_percentile(self, normal_data: np.ndarray) -> None:
        result_95 = train_autoencoder(
            normal_data, epochs=3, batch_size=32, percentile=95.0
        )
        result_99 = train_autoencoder(
            normal_data, epochs=3, batch_size=32, percentile=99.0
        )
        assert result_99["threshold"] >= result_95["threshold"]

    def test_model_is_in_eval_mode(self, normal_data: np.ndarray) -> None:
        result = train_autoencoder(normal_data, epochs=3, batch_size=32)
        assert not result["model"].training


class TestRandomForestTraining:

    @pytest.fixture
    def labeled_data(self) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(42)
        X = rng.standard_normal((400, 35)).astype(np.float32)
        y = np.concatenate([np.zeros(300, dtype=np.int64), np.ones(100, dtype=np.int64)])
        return X, y

    def test_returns_model_and_metrics(
        self, labeled_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        X, y = labeled_data
        result = train_random_forest(X, y)
        assert "model" in result
        assert "metrics" in result

    def test_model_has_predict_proba(
        self, labeled_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        X, y = labeled_data
        result = train_random_forest(X, y)
        assert hasattr(result["model"], "predict_proba")

    def test_metrics_contain_required_keys(
        self, labeled_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        X, y = labeled_data
        result = train_random_forest(X, y)
        for key in ("f1", "pr_auc", "accuracy", "precision", "recall"):
            assert key in result["metrics"]

    def test_probabilities_in_valid_range(
        self, labeled_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        X, y = labeled_data
        result = train_random_forest(X, y)
        proba = result["model"].predict_proba(X[:10])
        assert proba.min() >= 0.0
        assert proba.max() <= 1.0

    def test_metrics_values_in_valid_range(
        self, labeled_data: tuple[np.ndarray, np.ndarray]
    ) -> None:
        X, y = labeled_data
        result = train_random_forest(X, y)
        for value in result["metrics"].values():
            assert 0.0 <= value <= 1.0


class TestIsolationForestTraining:

    @pytest.fixture
    def normal_data(self) -> np.ndarray:
        rng = np.random.default_rng(42)
        return rng.standard_normal((200, 35)).astype(np.float32)

    def test_returns_model(self, normal_data: np.ndarray) -> None:
        result = train_isolation_forest(normal_data)
        assert "model" in result

    def test_model_has_score_samples(self, normal_data: np.ndarray) -> None:
        result = train_isolation_forest(normal_data)
        assert hasattr(result["model"], "score_samples")

    def test_returns_metrics_with_n_samples(self, normal_data: np.ndarray) -> None:
        result = train_isolation_forest(normal_data)
        assert result["metrics"]["n_samples"] == 200

    def test_anomaly_scores_distinguish_normal_and_outlier(
        self, normal_data: np.ndarray
    ) -> None:
        result = train_isolation_forest(normal_data)
        model = result["model"]
        normal_scores = model.score_samples(normal_data[:50])
        outlier_data = np.full((50, 35), 10.0, dtype=np.float32)
        outlier_scores = model.score_samples(outlier_data)
        assert normal_scores.mean() > outlier_scores.mean()
