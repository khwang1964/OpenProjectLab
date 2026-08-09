"""Contract tests for the public Plugin SDK export surface."""

from generator import sdk

REQUIRED_PUBLIC_SYMBOLS = (
    "BaseGenerator",
    "GenerateRequest",
    "GenerationOperation",
    "GenerationPlan",
    "GenerationResult",
    "GeneratorValidationError",
    "PluginError",
    "RuntimeOptions",
    "WritePolicy",
    "WriteResult",
    "WriteStatus",
)


def test_plugin_sdk_exports_required_public_contracts() -> None:
    """Expose every Plugin SDK v1 contract through generator.sdk."""
    missing = set(REQUIRED_PUBLIC_SYMBOLS).difference(dir(sdk))

    assert not missing, f"Missing public SDK symbols: {sorted(missing)}"


def test_generator_state_remains_importable_for_compatibility() -> None:
    """Keep GeneratorState importable during its compatibility period."""
    assert hasattr(sdk, "GeneratorState")
