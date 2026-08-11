"""Contract tests for the example third-party Plugin distribution."""

from __future__ import annotations

import ast
import importlib
import sys
import tomllib
from pathlib import Path

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = PROJECT_ROOT / "examples" / "plugins" / "hello-generator"
EXAMPLE_SRC = EXAMPLE_ROOT / "src"
PYPROJECT = EXAMPLE_ROOT / "pyproject.toml"
GENERATOR_SOURCE = EXAMPLE_SRC / "opl_hello_plugin" / "generator.py"

ENTRY_POINT_GROUP = "openprojectlab.generators"
ENTRY_POINT_NAME = "hello-plugin"
ENTRY_POINT_TARGET = "opl_hello_plugin.generator:HelloGenerator"


def _load_example_generator() -> type[BaseGenerator]:
    """Import the example exactly as a third-party src-layout package."""
    sys.path.insert(0, str(EXAMPLE_SRC))
    try:
        module = importlib.import_module("opl_hello_plugin.generator")
        return module.HelloGenerator
    finally:
        sys.path.remove(str(EXAMPLE_SRC))
        sys.modules.pop("opl_hello_plugin.generator", None)
        sys.modules.pop("opl_hello_plugin", None)


def _example_metadata() -> dict[str, object]:
    """Return the example distribution metadata."""
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_example_distribution_structure_exists() -> None:
    """Keep the documented third-party distribution structure intact."""
    assert PYPROJECT.is_file()
    assert (EXAMPLE_ROOT / "README.md").is_file()
    assert (EXAMPLE_SRC / "opl_hello_plugin" / "__init__.py").is_file()
    assert GENERATOR_SOURCE.is_file()
    assert (EXAMPLE_ROOT / "tests" / "test_plugin.py").is_file()


def test_example_distribution_matches_host_python_requirement() -> None:
    """Keep the example's Python floor aligned with the host package."""
    root_metadata = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    example_metadata = _example_metadata()

    assert (
        example_metadata["project"]["requires-python"]
        == root_metadata["project"]["requires-python"]
    )


def test_example_declares_canonical_generator_entry_point() -> None:
    """Declare one Generator under the canonical Plugin SDK Entry Point group."""
    metadata = _example_metadata()
    entry_points = metadata["project"]["entry-points"]

    assert entry_points[ENTRY_POINT_GROUP] == {
        ENTRY_POINT_NAME: ENTRY_POINT_TARGET,
    }


def test_example_generator_uses_only_public_opl_sdk_imports() -> None:
    """Prevent the example from depending on host implementation namespaces."""
    tree = ast.parse(
        GENERATOR_SOURCE.read_text(encoding="utf-8"),
        filename=str(GENERATOR_SOURCE),
    )
    opl_imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            opl_imports.update(
                alias.name
                for alias in node.names
                if alias.name == "generator" or alias.name.startswith("generator.")
            )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "generator" or module.startswith("generator."):
                opl_imports.add(module)

    assert opl_imports == {"generator.sdk"}


def test_example_generator_satisfies_public_generator_contract() -> None:
    """Instantiate the example with zero arguments through the public SDK contract."""
    generator_type = _load_example_generator()

    assert issubclass(generator_type, BaseGenerator)
    assert generator_type.name == ENTRY_POINT_NAME

    generator = generator_type()

    request = GenerateRequest(
        generator_name=ENTRY_POINT_NAME,
        target=PROJECT_ROOT,
        options=RuntimeOptions(dry_run=True),
    )

    plan = generator.plan(request)
    result = generator.execute(request, plan)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == ENTRY_POINT_NAME
    assert isinstance(result, GenerationResult)
    assert result.generator_name == ENTRY_POINT_NAME
    assert result.dry_run is True


def test_example_entry_point_identity_matches_generator_name() -> None:
    """Keep packaging metadata and runtime public identity identical."""
    generator_type = _load_example_generator()

    assert generator_type.name == ENTRY_POINT_NAME
