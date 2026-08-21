"""v1.1.4.6 deterministic Marketplace rendering and diagnostics tests."""

from __future__ import annotations

import hashlib
import json

import pytest

from generator.cli.main import build_parser
from generator.cli.marketplace import (
    MarketplaceCliOutput,
    MarketplaceInstallOutcome,
    VerifiedMarketplacePayload,
    render_marketplace_failure,
    render_marketplace_inspect,
    render_marketplace_install,
    render_marketplace_verify,
    render_marketplace_versions,
)
from generator.marketplace.installation import (
    ArtifactInstallationResult,
    ArtifactInstallationStatus,
)
from generator.marketplace.models import (
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)


def _artifact(payload: bytes = b"payload") -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity("community", "demo"),
        version=ArtifactVersion("1.2.3"),
        artifact_type=ArtifactType.TEMPLATE,
        description="Unicode fixture: 台灣",
        compatibility=CompatibilityRequirement(">=1.0,<2.0"),
        distribution=DistributionMetadata(kind="file", reference="packages/demo.opl"),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=hashlib.sha256(payload).hexdigest(),
        ),
    )


def _verified(payload: bytes = b"payload") -> VerifiedMarketplacePayload:
    artifact = _artifact(payload)
    return VerifiedMarketplacePayload(
        artifact=artifact,
        payload=payload,
        digest=hashlib.sha256(payload).hexdigest(),
        payload_size=len(payload),
    )


def _json(output: MarketplaceCliOutput) -> dict[str, object]:
    assert output.exit_code == 0
    assert output.stderr == ""
    assert output.stdout.endswith("\n")
    assert output.stdout.count("\n") == 1
    return json.loads(output.stdout)


def _top_level_commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI subcommand registry was not found")


def test_versions_json_is_sorted_compact_and_repeatable() -> None:
    identity = ArtifactIdentity("community", "demo")
    versions = tuple(ArtifactVersion(value) for value in ("2.0.0", "1.10.0", "1.2.0"))

    first = render_marketplace_versions(identity, versions, json_output=True)
    second = render_marketplace_versions(identity, tuple(reversed(versions)), json_output=True)

    assert first == second
    assert first.stdout == (
        '{"command":"versions","identity":"community/demo","schema_version":1,'
        '"versions":["1.2.0","1.10.0","2.0.0"]}\n'
    )


def test_versions_human_output_is_sorted_and_empty_is_success() -> None:
    identity = ArtifactIdentity("community", "demo")

    rendered = render_marketplace_versions(
        identity,
        (ArtifactVersion("2.0.0"), ArtifactVersion("1.0.0")),
    )

    assert rendered == MarketplaceCliOutput("1.0.0\n2.0.0\n", "", 0)
    assert render_marketplace_versions(identity, ()) == MarketplaceCliOutput("", "", 0)


def test_inspect_json_has_canonical_fields_and_preserves_utf8() -> None:
    output = render_marketplace_inspect(_artifact(), json_output=True)
    document = _json(output)

    assert document == {
        "artifact_type": "template",
        "command": "inspect",
        "compatibility": ">=1.0,<2.0",
        "coordinate": "community/demo@1.2.3",
        "description": "Unicode fixture: 台灣",
        "distribution_kind": "file",
        "distribution_reference": "packages/demo.opl",
        "integrity_algorithm": "sha256",
        "integrity_digest": hashlib.sha256(b"payload").hexdigest(),
        "schema_version": 1,
    }
    assert "台灣" in output.stdout
    assert "\\u53f0" not in output.stdout


def test_verify_never_exposes_payload_bytes() -> None:
    verified = _verified(b"secret payload")

    output = render_marketplace_verify(verified, json_output=True)
    document = _json(output)

    assert document["command"] == "verify"
    assert document["verified"] is True
    assert document["payload_size"] == len(b"secret payload")
    assert "secret payload" not in output.stdout


@pytest.mark.parametrize("dry_run", (False, True))
def test_install_json_distinguishes_install_from_dry_run(dry_run: bool) -> None:
    verified = _verified()
    installation = None
    if not dry_run:
        installation = ArtifactInstallationResult(
            artifact=verified.artifact,
            status=ArtifactInstallationStatus.INSTALLED,
            payload_size=verified.payload_size,
        )
    outcome = MarketplaceInstallOutcome(verified, installation, dry_run)

    document = _json(render_marketplace_install(outcome, json_output=True))

    assert document["command"] == "install"
    assert document["dry_run"] is dry_run
    assert document["status"] == ("verified" if dry_run else "installed")


def test_human_rendering_uses_stdout_only() -> None:
    for output in (
        render_marketplace_inspect(_artifact()),
        render_marketplace_verify(_verified()),
        render_marketplace_install(MarketplaceInstallOutcome(_verified(), None, True)),
    ):
        assert output.exit_code == 0
        assert output.stdout
        assert output.stderr == ""


def test_handled_failure_uses_stderr_only_and_emits_no_json() -> None:
    output = render_marketplace_failure(ValueError("catalog failed"))

    assert output == MarketplaceCliOutput("", "error: catalog failed\n", 2)
    assert "{" not in output.stderr


def test_empty_failure_message_uses_exception_class() -> None:
    assert render_marketplace_failure(ValueError()).stderr == "error: ValueError\n"


@pytest.mark.parametrize(
    ("factory", "argument"),
    (
        (render_marketplace_versions, (ArtifactIdentity("community", "demo"), ())),
        (render_marketplace_inspect, (_artifact(),)),
        (render_marketplace_verify, (_verified(),)),
        (render_marketplace_install, (MarketplaceInstallOutcome(_verified(), None, True),)),
    ),
)
def test_renderers_require_real_boolean_json_flag(
    factory: object,
    argument: tuple[object, ...],
) -> None:
    with pytest.raises(TypeError, match="json_output"):
        factory(*argument, json_output=1)  # type: ignore[operator]


def test_output_invariants_reject_mixed_or_unknown_process_states() -> None:
    with pytest.raises(ValueError, match="stderr"):
        MarketplaceCliOutput("success\n", "warning\n", 0)
    with pytest.raises(ValueError, match="stdout"):
        MarketplaceCliOutput("partial\n", "error\n", 2)
    with pytest.raises(ValueError, match="0 or 2"):
        MarketplaceCliOutput("", "", 1)


def test_rendering_is_used_after_production_registration() -> None:
    assert "marketplace" in _top_level_commands()
