"""
©AngelaMos | 2026
scaler.py
"""

import json
from pathlib import Path

import numpy as np
from sklearn.preprocessing import RobustScaler


class FeatureScaler:
    """
    IQR-based feature scaler persisted as JSON (not pickle).

    Wraps sklearn RobustScaler for outlier-robust normalization.
    Used only for autoencoder input — tree models are scale-invariant.
    """

    def __init__(self) -> None:
        self._scaler: RobustScaler | None = None
        self._fitted = False

    @property
    def n_features(self) -> int:
        """
        Number of features the scaler was fitted on.
        """
        if not self._fitted or self._scaler is None:
            raise RuntimeError("Scaler has not been fitted")
        return int(self._scaler.n_features_in_)

    def fit(self, X: np.ndarray) -> FeatureScaler:
        """
        Fit the scaler on training data.
        """
        self._scaler = RobustScaler()
        self._scaler.fit(X)
        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features using the fitted scaler parameters.
        """
        if not self._fitted or self._scaler is None:
            raise RuntimeError("Scaler has not been fitted")
        return self._scaler.transform(X).astype(np.float32)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Reverse the scaling transformation.
        """
        if not self._fitted or self._scaler is None:
            raise RuntimeError("Scaler has not been fitted")
        return self._scaler.inverse_transform(X).astype(np.float32)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit and transform in one step.
        """
        self.fit(X)
        return self.transform(X)

    def save_json(self, path: Path | str) -> None:
        """
        Serialize scaler parameters to a human-readable JSON file.
        """
        if not self._fitted or self._scaler is None:
            raise RuntimeError("Scaler has not been fitted")
        data = {
            "center": self._scaler.center_.tolist(),
            "scale": self._scaler.scale_.tolist(),
            "n_features": int(self._scaler.n_features_in_),
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load_json(cls, path: Path | str) -> FeatureScaler:
        """
        Reconstruct a fitted scaler from a JSON file.
        """
        data = json.loads(Path(path).read_text())
        scaler = cls()
        scaler._scaler = RobustScaler()
        scaler._scaler.center_ = np.array(data["center"], dtype=np.float64)
        scaler._scaler.scale_ = np.array(data["scale"], dtype=np.float64)
        scaler._scaler.n_features_in_ = data["n_features"]
        scaler._fitted = True
        return scaler
