"""Freeze the exact OpenProjectLab v1 public Plugin SDK export surface."""

from generator import sdk

EXPECTED_V1_PUBLIC_SYMBOLS = frozenset(
    {
        "BaseGenerator",
        "GenerateRequest",
        "GenerationOperation",
        "GenerationPlan",
        "GenerationResult",
        "GeneratorState",
        "GeneratorValidationError",
        "PluginError",
        "RuntimeOptions",
        "WritePolicy",
        "WriteResult",
        "WriteStatus",
    }
)


def test_v1_public_sdk_exports_exact_contract() -> None:
    """Expose exactly the reviewed v1 public Plugin SDK symbols."""
    actual = frozenset(sdk.__all__)

    assert actual == EXPECTED_V1_PUBLIC_SYMBOLS


def test_v1_public_sdk_exports_are_unique() -> None:
    """Prevent duplicate names from entering the public SDK declaration."""
    assert len(sdk.__all__) == len(set(sdk.__all__))


def test_v1_public_sdk_exports_are_importable() -> None:
    """Require every declared v1 public symbol to resolve from generator.sdk."""
    missing = sorted(name for name in EXPECTED_V1_PUBLIC_SYMBOLS if not hasattr(sdk, name))

    assert not missing, f"Missing v1 public SDK symbols: {missing}"
