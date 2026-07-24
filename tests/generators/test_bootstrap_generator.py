from generator.core.context import GeneratorContext
from generator.generators.bootstrap_generator import BootstrapGenerator


def test_bootstrap(tmp_path):
    out = tmp_path / "demo"
    BootstrapGenerator().run(GeneratorContext(out, {"project_name": "Demo", "version": "1.2.3"}))
    assert (out / "README.md").exists()
