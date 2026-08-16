"""Contract tests for Marketplace Template Packages.

Step 7.7 scope:
- immutable TemplateEntry
- immutable TemplatePackageManifest
- immutable TemplatePackage
- reuse of Marketplace artifact identity/version/type
- safe relative template/resource paths
- deterministic ordering
- duplicate-name and duplicate-path rejection

Out of scope:
- Jinja rendering
- generator execution
- filesystem output
- network access
- remote Marketplace
- activation
- CLI
- generator.sdk expansion
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.marketplace.models import (
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)
from generator.marketplace.template_package import (
    TemplateEntry,
    TemplatePackage,
    TemplatePackageManifest,
    TemplatePackageValidationError,
)


def _artifact(
    *,
    artifact_type: ArtifactType = ArtifactType.TEMPLATE,
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace="community",
            name="modern-java-templates",
        ),
        version=ArtifactVersion("1.0.0"),
        artifact_type=artifact_type,
        description="Modern Java courseware templates",
        compatibility=CompatibilityRequirement(">=0.7,<1.0"),
        distribution=DistributionMetadata(
            kind="package",
            reference="community-modern-java-templates-1.0.0",
        ),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest="a" * 64,
        ),
    )


def _template(
    *,
    name: str = "week-readme",
    relative_path: str = "week/README.md.j2",
    media_type: str = "text/markdown+j2",
) -> TemplateEntry:
    return TemplateEntry(
        name=name,
        relative_path=relative_path,
        media_type=media_type,
    )


def _resource(
    *,
    name: str = "course-logo",
    relative_path: str = "assets/logo.svg",
    media_type: str = "image/svg+xml",
) -> TemplateEntry:
    return TemplateEntry(
        name=name,
        relative_path=relative_path,
        media_type=media_type,
    )


def _manifest(
    *,
    templates: tuple[TemplateEntry, ...] | None = None,
    resources: tuple[TemplateEntry, ...] | None = None,
) -> TemplatePackageManifest:
    return TemplatePackageManifest(
        schema_version=1,
        templates=((_template(),) if templates is None else templates),
        resources=((_resource(),) if resources is None else resources),
    )


class TestTemplateEntry:
    def test_preserves_entry_metadata(self) -> None:
        entry = _template()

        assert entry.name == "week-readme"
        assert entry.relative_path == "week/README.md.j2"
        assert entry.media_type == "text/markdown+j2"

    @pytest.mark.parametrize(
        ("name", "relative_path", "media_type"),
        [
            ("", "week/README.md.j2", "text/plain"),
            ("   ", "week/README.md.j2", "text/plain"),
            ("week", "", "text/plain"),
            ("week", "   ", "text/plain"),
            ("week", "week/README.md.j2", ""),
            ("week", "week/README.md.j2", "   "),
        ],
    )
    def test_rejects_blank_required_fields(
        self,
        name: str,
        relative_path: str,
        media_type: str,
    ) -> None:
        with pytest.raises(ValueError):
            TemplateEntry(
                name=name,
                relative_path=relative_path,
                media_type=media_type,
            )

    @pytest.mark.parametrize(
        "relative_path",
        [
            "../README.md.j2",
            "../../secret.txt",
            "/absolute/README.md.j2",
            r"\absolute\README.md.j2",
            "week/../README.md.j2",
            r"week\..\README.md.j2",
            "C:/templates/README.md.j2",
            r"C:\templates\README.md.j2",
        ],
    )
    def test_rejects_unsafe_paths(
        self,
        relative_path: str,
    ) -> None:
        with pytest.raises(ValueError):
            TemplateEntry(
                name="week",
                relative_path=relative_path,
                media_type="text/plain",
            )

    def test_normalizes_backslashes_to_posix_relative_path(self) -> None:
        entry = TemplateEntry(
            name="week",
            relative_path=r"week\README.md.j2",
            media_type="text/plain",
        )

        assert entry.relative_path == "week/README.md.j2"

    def test_is_immutable(self) -> None:
        entry = _template()

        with pytest.raises(FrozenInstanceError):
            entry.name = "renamed"  # type: ignore[misc]


class TestTemplatePackageManifest:
    def test_preserves_schema_templates_and_resources(self) -> None:
        manifest = _manifest()

        assert manifest.schema_version == 1
        assert manifest.templates == (_template(),)
        assert manifest.resources == (_resource(),)

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
            TemplatePackageManifest(
                schema_version=schema_version,
                templates=(_template(),),
                resources=(),
            )

    def test_sorts_templates_deterministically(self) -> None:
        manifest = _manifest(
            templates=(
                _template(
                    name="week",
                    relative_path="week/README.md.j2",
                ),
                _template(
                    name="course",
                    relative_path="course/README.md.j2",
                ),
            ),
            resources=(),
        )

        assert tuple(entry.name for entry in manifest.templates) == (
            "course",
            "week",
        )

    def test_sorts_resources_deterministically(self) -> None:
        manifest = _manifest(
            templates=(),
            resources=(
                _resource(
                    name="z-logo",
                    relative_path="assets/z.svg",
                ),
                _resource(
                    name="a-logo",
                    relative_path="assets/a.svg",
                ),
            ),
        )

        assert tuple(entry.name for entry in manifest.resources) == (
            "a-logo",
            "z-logo",
        )

    def test_rejects_duplicate_template_names(self) -> None:
        with pytest.raises(TemplatePackageValidationError):
            _manifest(
                templates=(
                    _template(
                        name="week",
                        relative_path="week/a.md.j2",
                    ),
                    _template(
                        name="week",
                        relative_path="week/b.md.j2",
                    ),
                ),
                resources=(),
            )

    def test_rejects_duplicate_template_paths(self) -> None:
        with pytest.raises(TemplatePackageValidationError):
            _manifest(
                templates=(
                    _template(
                        name="week-a",
                        relative_path="week/README.md.j2",
                    ),
                    _template(
                        name="week-b",
                        relative_path="week/README.md.j2",
                    ),
                ),
                resources=(),
            )

    def test_rejects_duplicate_resource_names(self) -> None:
        with pytest.raises(TemplatePackageValidationError):
            _manifest(
                templates=(),
                resources=(
                    _resource(
                        name="logo",
                        relative_path="assets/a.svg",
                    ),
                    _resource(
                        name="logo",
                        relative_path="assets/b.svg",
                    ),
                ),
            )

    def test_rejects_duplicate_resource_paths(self) -> None:
        with pytest.raises(TemplatePackageValidationError):
            _manifest(
                templates=(),
                resources=(
                    _resource(
                        name="logo-a",
                        relative_path="assets/logo.svg",
                    ),
                    _resource(
                        name="logo-b",
                        relative_path="assets/logo.svg",
                    ),
                ),
            )

    def test_rejects_path_collision_between_template_and_resource(
        self,
    ) -> None:
        with pytest.raises(TemplatePackageValidationError):
            _manifest(
                templates=(
                    _template(
                        name="shared-template",
                        relative_path="shared/item.txt",
                    ),
                ),
                resources=(
                    _resource(
                        name="shared-resource",
                        relative_path="shared/item.txt",
                        media_type="text/plain",
                    ),
                ),
            )

    def test_rejects_non_template_entry_values(self) -> None:
        with pytest.raises(TypeError):
            TemplatePackageManifest(
                schema_version=1,
                templates=(object(),),  # type: ignore[arg-type]
                resources=(),
            )

    def test_is_immutable(self) -> None:
        manifest = _manifest()

        with pytest.raises(FrozenInstanceError):
            manifest.schema_version = 2  # type: ignore[misc]


class TestTemplatePackage:
    def test_composes_template_artifact_and_manifest(self) -> None:
        artifact = _artifact()
        manifest = _manifest()

        package = TemplatePackage(
            artifact=artifact,
            manifest=manifest,
        )

        assert package.artifact == artifact
        assert package.manifest == manifest
        assert package.coordinate == artifact.coordinate

    def test_requires_template_artifact_type(self) -> None:
        with pytest.raises(TemplatePackageValidationError):
            TemplatePackage(
                artifact=_artifact(
                    artifact_type=ArtifactType.PLUGIN,
                ),
                manifest=_manifest(),
            )

    def test_requires_marketplace_artifact(self) -> None:
        with pytest.raises(TypeError):
            TemplatePackage(
                artifact=object(),  # type: ignore[arg-type]
                manifest=_manifest(),
            )

    def test_requires_template_package_manifest(self) -> None:
        with pytest.raises(TypeError):
            TemplatePackage(
                artifact=_artifact(),
                manifest=object(),  # type: ignore[arg-type]
            )

    def test_is_immutable(self) -> None:
        package = TemplatePackage(
            artifact=_artifact(),
            manifest=_manifest(),
        )

        with pytest.raises(FrozenInstanceError):
            package.manifest = _manifest(  # type: ignore[misc]
                templates=(),
                resources=(),
            )

    def test_equal_inputs_produce_equal_packages(self) -> None:
        first = TemplatePackage(
            artifact=_artifact(),
            manifest=_manifest(),
        )
        second = TemplatePackage(
            artifact=_artifact(),
            manifest=_manifest(),
        )

        assert first == second
        assert hash(first) == hash(second)

    def test_package_contract_has_no_filesystem_side_effect(
        self,
        tmp_path,
    ) -> None:
        before = tuple(tmp_path.iterdir())

        TemplatePackage(
            artifact=_artifact(),
            manifest=_manifest(),
        )

        assert tuple(tmp_path.iterdir()) == before
