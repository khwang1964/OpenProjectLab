import pytest

from generator.core.exceptions import GeneratorNotFoundError
from generator.core.registry import GeneratorRegistry
from generator.generators.bootstrap_generator import BootstrapGenerator


def test_registry():
    r = GeneratorRegistry()
    r.register("bootstrap", BootstrapGenerator)
    assert isinstance(r.create("bootstrap"), BootstrapGenerator)


def test_missing():
    with pytest.raises(GeneratorNotFoundError):
        GeneratorRegistry().create("missing")
