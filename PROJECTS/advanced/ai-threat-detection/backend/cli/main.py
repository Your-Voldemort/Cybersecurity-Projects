"""
©AngelaMos | 2026
main.py
"""

from pathlib import Path

import typer

app = typer.Typer(
    name="vigil",
    help="AngelusVigil — AI-powered threat detection engine",
    no_args_is_help=True,
)

DEFAULT_MODEL_DIR = "data/models"
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 256
DEFAULT_SERVER_URL = "http://localhost:8000"


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind address"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False,
                                help="Enable auto-reload for development"),
) -> None:
    """
    Start the AngelusVigil API server
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def train(
    dataset: Path = typer.Option(..., help="Path to CSIC 2010 CSV dataset"),
    output_dir: Path = typer.Option(
        DEFAULT_MODEL_DIR,
        help="Directory to save ONNX models",
    ),
    epochs: int = typer.Option(
        DEFAULT_EPOCHS,
        help="Autoencoder training epochs",
    ),
    batch_size: int = typer.Option(
        DEFAULT_BATCH_SIZE,
        help="Training batch size",
    ),
) -> None:
    """
    Train all ML models and export to ONNX
    """
    import json

    import numpy as np
    from sklearn.model_selection import train_test_split

    from ml.export_onnx import (
        export_autoencoder,
        export_isolation_forest,
        export_random_forest,
    )
    from ml.train_autoencoder import train_autoencoder
    from ml.train_classifiers import (
        train_isolation_forest,
        train_random_forest,
    )

    if not dataset.exists():
        typer.echo(
            f"Error: dataset not found at {dataset}",
            err=True,
        )
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Loading dataset from {dataset}")
    data = np.loadtxt(str(dataset), delimiter=",", dtype=np.float32)
    X = data[:, :-1]
    y = data[:, -1].astype(int)

    X_normal = X[y == 0]
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        test_size=0.2,
                                                        stratify=y,
                                                        random_state=42)

    typer.echo(f"Training autoencoder for {epochs} epochs")
    ae_result = train_autoencoder(
        X_normal,
        epochs=epochs,
        batch_size=batch_size,
    )
    export_autoencoder(ae_result["model"], output_dir / "ae.onnx")
    ae_result["scaler"].save_json(output_dir / "scaler.json")
    threshold_data = {"threshold": float(ae_result["threshold"])}
    (output_dir / "threshold.json").write_text(json.dumps(threshold_data))
    typer.echo(f"  AE threshold: {ae_result['threshold']:.6f}")

    typer.echo("Training random forest")
    rf_result = train_random_forest(X_train, y_train)
    export_random_forest(rf_result["model"], X.shape[1],
                         output_dir / "rf.onnx")
    typer.echo(f"  RF F1: {rf_result['metrics']['f1']:.4f}")

    typer.echo("Training isolation forest")
    if_result = train_isolation_forest(X_normal)
    export_isolation_forest(if_result["model"], X.shape[1],
                            output_dir / "if.onnx")
    typer.echo(f"  IF samples: {if_result['metrics']['n_samples']}")

    typer.echo(f"Models exported to {output_dir}")


@app.command()
def replay(
        log_file: Path = typer.Option(...,
                                      help="Path to nginx access log file"),
        url: str = typer.Option(
            DEFAULT_SERVER_URL,
            help="Running server URL to send logs to",
        ),
        batch_size: int = typer.Option(100, help="Lines per batch"),
) -> None:
    """
    Replay historical log lines through the pipeline
    """
    import httpx

    if not log_file.exists():
        typer.echo(
            f"Error: log file not found at {log_file}",
            err=True,
        )
        raise typer.Exit(code=1)

    lines = log_file.read_text().strip().splitlines()
    typer.echo(f"Replaying {len(lines)} lines to {url}")

    sent = 0
    with httpx.Client(timeout=30.0) as client:
        for i in range(0, len(lines), batch_size):
            batch = lines[i:i + batch_size]
            response = client.post(
                f"{url}/ingest/batch",
                json={"lines": batch},
            )
            if response.status_code == 200:
                sent += len(batch)
            else:
                typer.echo(
                    f"  Batch {i} failed: {response.status_code}",
                    err=True,
                )

    typer.echo(f"Replayed {sent}/{len(lines)} lines")


@app.command()
def config() -> None:
    """
    Print the current configuration (secrets redacted)
    """
    from app.config import settings

    safe_fields = {}
    for key, value in settings.model_dump().items():
        if any(secret in key for secret in (
                "key",
                "password",
                "secret",
                "token",
        )):
            safe_fields[key] = "***REDACTED***"
        elif "url" in key and "@" in str(value):
            safe_fields[key] = _redact_url(str(value))
        else:
            safe_fields[key] = value

    for key, value in sorted(safe_fields.items()):
        typer.echo(f"  {key}: {value}")


@app.command()
def health(
    url: str = typer.Option(
        DEFAULT_SERVER_URL,
        help="Base URL of the running server",
    ),
) -> None:
    """
    Ping the running server's /health endpoint
    """
    import httpx

    try:
        response = httpx.get(f"{url}/health", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        typer.echo(f"  status: {data.get('status', 'unknown')}")
        typer.echo(f"  uptime: {data.get('uptime_seconds', 0):.0f}s")
        typer.echo(
            f"  pipeline: {'running' if data.get('pipeline_running') else 'stopped'}"
        )
    except httpx.ConnectError:
        typer.echo("Error: cannot connect to server", err=True)
        raise typer.Exit(code=1) from None
    except httpx.HTTPStatusError as exc:
        typer.echo(
            f"Error: server returned {exc.response.status_code}",
            err=True,
        )
        raise typer.Exit(code=1) from None


def _redact_url(url: str) -> str:
    """
    Replace the user:password portion of a database
    URL with ***:***
    """
    if "://" not in url or "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    _, host_part = rest.rsplit("@", 1)
    return f"{scheme}://***:***@{host_part}"


if __name__ == "__main__":
    app()
