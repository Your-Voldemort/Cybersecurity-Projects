"""
©AngelaMos | 2026
export_onnx.py
"""

from pathlib import Path

import torch
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.base import BaseEstimator

from ml.autoencoder import ThreatAutoencoder

ONNX_OPSET = 17
SKL_TARGET_OPSET = {"": 17, "ai.onnx.ml": 3}


def export_autoencoder(
    model: ThreatAutoencoder,
    path: Path | str,
    opset: int = ONNX_OPSET,
) -> Path:
    """
    Export a PyTorch autoencoder to ONNX with dynamic batch dimension
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    model.eval()
    dummy = torch.randn(1, model.input_dim)

    batch_dim = torch.export.Dim("batch_size", min=1)

    torch.onnx.export(
        model,
        dummy,
        str(path),
        opset_version=opset,
        export_params=True,
        do_constant_folding=True,
        input_names=["features"],
        output_names=["reconstructed"],
        dynamic_shapes={"x": {
            0: batch_dim
        }},
    )
    return path


def export_random_forest(
    model: BaseEstimator,
    n_features: int,
    path: Path | str,
) -> Path:
    """
    Export a sklearn random forest (or calibrated wrapper) to ONNX
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    initial_type = [("features", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        target_opset=SKL_TARGET_OPSET,
    )
    path.write_bytes(onnx_model.SerializeToString())
    return path


def export_isolation_forest(
    model: BaseEstimator,
    n_features: int,
    path: Path | str,
) -> Path:
    """
    Export a sklearn isolation forest to ONNX
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    initial_type = [("features", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        target_opset=SKL_TARGET_OPSET,
    )
    path.write_bytes(onnx_model.SerializeToString())
    return path
