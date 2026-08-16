"""Contract tests for the Milestone 7 Marketplace artifact model.

These tests define the minimum contract described by ADR 0023.

Scope:
- artifact identity
- artifact version
- artifact type
- artifact coordinate
- OPL compatibility requirements
- distribution metadata
- SHA-256 integrity metadata
- immutable MarketplaceArtifact composition

Out of scope:
- repository/index discovery
- acquisition/download
- installation/activation
- CLI
- network access
- filesystem side effects
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.marketplace.models import (
    ArtifactCoordinate,
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)

VALID_SHA256 = "a" * 64


def _identity() -> ArtifactIdentity:
    return ArtifactIdentity(
        namespace="community",
        name="modern-java-templates",
    )


def _version() -> ArtifactVersion:
    return ArtifactVersion("1.2.0")


def _compatibility() -> CompatibilityRequirement:
    return CompatibilityRequirement(">=0.7,<1.0")


def _distribution() -> DistributionMetadata:
    return DistributionMetadata(
        kind="package",
        reference="example-distribution-reference",
    )


def _integrity() -> IntegrityMetadata:
    return IntegrityMetadata(
        algorithm="sha256",
        digest=VALID_SHA256,
    )


def _artifact(
    *,
    artifact_type: ArtifactType = ArtifactType.TEMPLATE,
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=_identity(),
        version=_version(),
        artifact_type=artifact_type,
        description="Templates for Modern Java courseware.",
        compatibility=_compatibility(),
        distribution=_distribution(),
        integrity=_integrity(),
    )


class TestArtifactIdentity:
    def test_requires_namespace_and_name(self) -> None:
        identity = _identity()

        assert identity.namespace == "community"
        assert identity.name == "modern-java-templates"

    @pytest.mark.parametrize(
        ("namespace", "name"),
        [
            ("", "artifact"),
            ("   ", "artifact"),
            ("community", ""),
            ("community", "   "),
        ],
    )
    def test_rejects_blank_components(
        self,
        namespace: str,
        name: str,
    ) -> None:
        with pytest.raises(ValueError):
            ArtifactIdentity(
                namespace=namespace,
                name=name,
            )

    @pytest.mark.parametrize(
        ("namespace", "name"),
        [
            ("..", "artifact"),
            ("community", ".."),
            ("../outside", "artifact"),
            ("community", "../outside"),
            ("/absolute", "artifact"),
            ("community", "/absolute"),
            ("community/sub", "artifact"),
            ("community", "artifact/sub"),
            (r"community\sub", "artifact"),
            ("community", r"artifact\sub"),
        ],
    )
    def test_rejects_path_semantics(
        self,
        namespace: str,
        name: str,
    ) -> None:
        with pytest.raises(ValueError):
            ArtifactIdentity(
                namespace=namespace,
                name=name,
            )

    def test_is_immutable(self) -> None:
        identity = _identity()

        with pytest.raises(FrozenInstanceError):
            identity.name = "renamed"  # type: ignore[misc]


class TestArtifactVersion:
    @pytest.mark.parametrize(
        "value",
        [
            "0.0.0",
            "0.7.0",
            "1.2.3",
            "10.20.30",
        ],
    )
    def test_accepts_explicit_semantic_versions(
        self,
        value: str,
    ) -> None:
        version = ArtifactVersion(value)

        assert str(version) == value

    @pytest.mark.parametrize(
        "value",
        [
            "",
            " ",
            "latest",
            "stable",
            "current",
            "1",
            "1.2",
            "1.2.x",
            "v1.2.3",
            "1.2.3.4",
            "1.02.3",
        ],
    )
    def test_rejects_noncanonical_versions(
        self,
        value: str,
    ) -> None:
        with pytest.raises(ValueError):
            ArtifactVersion(value)

    def test_equality_is_deterministic(self) -> None:
        assert ArtifactVersion("1.2.3") == ArtifactVersion("1.2.3")
        assert ArtifactVersion("1.2.3") != ArtifactVersion("1.2.4")


class TestArtifactType:
    def test_exposes_initial_artifact_types(self) -> None:
        assert ArtifactType.PLUGIN.value == "plugin"
        assert ArtifactType.GENERATOR.value == "generator"
        assert ArtifactType.TEMPLATE.value == "template"

    @pytest.mark.parametrize(
        "value",
        [
            "plugin",
            "generator",
            "template",
        ],
    )
    def test_constructs_known_types(
        self,
        value: str,
    ) -> None:
        assert ArtifactType(value).value == value

    def test_rejects_unknown_type(self) -> None:
        with pytest.raises(ValueError):
            ArtifactType("provider")


class TestArtifactCoordinate:
    def test_combines_identity_and_version(self) -> None:
        coordinate = ArtifactCoordinate(
            identity=_identity(),
            version=_version(),
        )

        assert coordinate.identity == _identity()
        assert coordinate.version == _version()

    def test_equality_is_deterministic(self) -> None:
        first = ArtifactCoordinate(
            identity=_identity(),
            version=_version(),
        )
        second = ArtifactCoordinate(
            identity=_identity(),
            version=_version(),
        )

        assert first == second
        assert hash(first) == hash(second)

    def test_is_immutable(self) -> None:
        coordinate = ArtifactCoordinate(
            identity=_identity(),
            version=_version(),
        )

        with pytest.raises(FrozenInstanceError):
            coordinate.version = ArtifactVersion("2.0.0")  # type: ignore[misc]


class TestCompatibilityRequirement:
    @pytest.mark.parametrize(
        "requirement",
        [
            ">=0.7,<1.0",
            ">=0.7.0,<1.0.0",
            "==0.7.0",
        ],
    )
    def test_accepts_supported_requirement_syntax(
        self,
        requirement: str,
    ) -> None:
        compatibility = CompatibilityRequirement(requirement)

        assert str(compatibility) == requirement

    @pytest.mark.parametrize(
        "requirement",
        [
            "",
            " ",
            "latest",
            ">=x",
            "0.7 - 1.0",
        ],
    )
    def test_rejects_invalid_requirement_syntax(
        self,
        requirement: str,
    ) -> None:
        with pytest.raises(ValueError):
            CompatibilityRequirement(requirement)

    @pytest.mark.parametrize(
        ("runtime_version", "expected"),
        [
            ("0.6.9", False),
            ("0.7.0", True),
            ("0.9.9", True),
            ("1.0.0", False),
        ],
    )
    def test_supports_runtime_version_deterministically(
        self,
        runtime_version: str,
        expected: bool,
    ) -> None:
        compatibility = _compatibility()

        assert compatibility.supports(runtime_version) is expected


class TestDistributionMetadata:
    def test_preserves_distribution_kind_and_reference(self) -> None:
        distribution = _distribution()

        assert distribution.kind == "package"
        assert distribution.reference == "example-distribution-reference"

    @pytest.mark.parametrize(
        ("kind", "reference"),
        [
            ("", "reference"),
            ("   ", "reference"),
            ("package", ""),
            ("package", "   "),
        ],
    )
    def test_rejects_blank_required_fields(
        self,
        kind: str,
        reference: str,
    ) -> None:
        with pytest.raises(ValueError):
            DistributionMetadata(
                kind=kind,
                reference=reference,
            )

    def test_is_immutable(self) -> None:
        distribution = _distribution()

        with pytest.raises(FrozenInstanceError):
            distribution.kind = "archive"  # type: ignore[misc]


class TestIntegrityMetadata:
    def test_accepts_sha256_digest(self) -> None:
        integrity = _integrity()

        assert integrity.algorithm == "sha256"
        assert integrity.digest == VALID_SHA256

    @pytest.mark.parametrize(
        "digest",
        [
            "",
            "abc",
            "g" * 64,
            "a" * 63,
            "a" * 65,
        ],
    )
    def test_rejects_malformed_sha256_digest(
        self,
        digest: str,
    ) -> None:
        with pytest.raises(ValueError):
            IntegrityMetadata(
                algorithm="sha256",
                digest=digest,
            )

    def test_rejects_unsupported_algorithm(self) -> None:
        with pytest.raises(ValueError):
            IntegrityMetadata(
                algorithm="md5",
                digest="a" * 32,
            )

    def test_is_immutable(self) -> None:
        integrity = _integrity()

        with pytest.raises(FrozenInstanceError):
            integrity.digest = "b" * 64  # type: ignore[misc]


class TestMarketplaceArtifact:
    def test_composes_the_common_artifact_contract(self) -> None:
        artifact = _artifact()

        assert artifact.schema_version == 1
        assert artifact.identity == _identity()
        assert artifact.version == _version()
        assert artifact.artifact_type is ArtifactType.TEMPLATE
        assert artifact.description == "Templates for Modern Java courseware."
        assert artifact.compatibility == _compatibility()
        assert artifact.distribution == _distribution()
        assert artifact.integrity == _integrity()

    def test_coordinate_is_derived_deterministically(self) -> None:
        artifact = _artifact()

        assert artifact.coordinate == ArtifactCoordinate(
            identity=_identity(),
            version=_version(),
        )

    @pytest.mark.parametrize(
        "schema_version",
        [
            0,
            -1,
            2,
        ],
    )
    def test_rejects_unsupported_schema_versions(
        self,
        schema_version: int,
    ) -> None:
        with pytest.raises(ValueError):
            MarketplaceArtifact(
                schema_version=schema_version,
                identity=_identity(),
                version=_version(),
                artifact_type=ArtifactType.TEMPLATE,
                description="Templates for Modern Java courseware.",
                compatibility=_compatibility(),
                distribution=_distribution(),
                integrity=_integrity(),
            )

    @pytest.mark.parametrize(
        "artifact_type",
        [
            ArtifactType.PLUGIN,
            ArtifactType.GENERATOR,
            ArtifactType.TEMPLATE,
        ],
    )
    def test_accepts_all_initial_artifact_types(
        self,
        artifact_type: ArtifactType,
    ) -> None:
        artifact = _artifact(
            artifact_type=artifact_type,
        )

        assert artifact.artifact_type is artifact_type

    def test_is_immutable(self) -> None:
        artifact = _artifact()

        with pytest.raises(FrozenInstanceError):
            artifact.description = "changed"  # type: ignore[misc]

    def test_equal_inputs_produce_equal_artifacts(self) -> None:
        first = _artifact()
        second = _artifact()

        assert first == second
        assert hash(first) == hash(second)
