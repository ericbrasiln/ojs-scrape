"""Configuração dos testes."""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="executa testes que acessam endpoints reais na internet",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-integration"):
        return

    skip_integration = pytest.mark.skip(reason="use --run-integration para executar")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
