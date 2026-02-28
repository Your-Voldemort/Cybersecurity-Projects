"""
©AngelaMos | 2026
test_cli.py

Tests the Typer CLI commands: help output, argument validation, and error handling for missing paths.
"""

from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


class TestCLICommands:

    def test_train_help(self) -> None:
        """
        train --help exits cleanly and mentions 'dataset' in its output.
        """
        result = runner.invoke(app, ["train", "--help"])
        assert result.exit_code == 0
        assert "dataset" in result.output.lower()

    def test_replay_help(self) -> None:
        """
        replay --help exits cleanly and mentions 'log' in its output.
        """
        result = runner.invoke(app, ["replay", "--help"])
        assert result.exit_code == 0
        assert "log" in result.output.lower()

    def test_serve_help(self) -> None:
        """
        serve --help exits cleanly and mentions 'host' in its output.
        """
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "host" in result.output.lower()

    def test_config_help(self) -> None:
        """
        config --help exits cleanly.
        """
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0

    def test_health_help(self) -> None:
        """
        health --help exits cleanly.
        """
        result = runner.invoke(app, ["health", "--help"])
        assert result.exit_code == 0

    def test_train_missing_dataset_fails(self) -> None:
        """
        train with a non-existent dataset path exits with a non-zero code.
        """
        result = runner.invoke(
            app,
            [
                "train",
                "--dataset",
                "/nonexistent/data.csv",
            ],
        )
        assert result.exit_code != 0

    def test_replay_missing_log_fails(self) -> None:
        """
        replay with a non-existent log file exits with a non-zero code.
        """
        result = runner.invoke(
            app,
            [
                "replay",
                "--log-file",
                "/nonexistent/access.log",
            ],
        )
        assert result.exit_code != 0
