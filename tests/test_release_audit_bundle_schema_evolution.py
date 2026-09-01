import json

import pytest

from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleCompatibilityCategory,
    AuditBundleMigrationEdge,
    AuditBundleMigrationError,
    AuditBundleSchemaRegistry,
    inspect_audit_bundle_schema,
)


def test_default_registry_classifies_only_explicit_schema_identities() -> None:
    assert (
        DEFAULT_SCHEMA_REGISTRY.classify("1").category is AuditBundleCompatibilityCategory.CURRENT
    )
    migratable = DEFAULT_SCHEMA_REGISTRY.classify("0")
    assert migratable.category is AuditBundleCompatibilityCategory.MIGRATABLE
    assert migratable.migration_steps == ("upgrade-0-to-1",)
    assert DEFAULT_SCHEMA_REGISTRY.classify("2").category is AuditBundleCompatibilityCategory.FUTURE
    assert (
        DEFAULT_SCHEMA_REGISTRY.classify("01").category
        is AuditBundleCompatibilityCategory.UNSUPPORTED
    )


def test_migration_plan_is_deterministic_and_non_executing() -> None:
    first = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    second = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    assert first == second
    assert first.steps == ("upgrade-0-to-1",)
    assert len(first.preview_fingerprint) == 64


def test_planner_rejects_missing_and_ambiguous_paths() -> None:
    with pytest.raises(AuditBundleMigrationError, match="no explicit migration path"):
        DEFAULT_SCHEMA_REGISTRY.plan("1", "0")

    registry = AuditBundleSchemaRegistry(
        current_schema="3",
        supported_schemas=("0", "1", "2", "3"),
        migration_edges=(
            AuditBundleMigrationEdge("0", "1", "a"),
            AuditBundleMigrationEdge("0", "2", "b"),
            AuditBundleMigrationEdge("1", "3", "c"),
            AuditBundleMigrationEdge("2", "3", "d"),
        ),
    )
    with pytest.raises(AuditBundleMigrationError, match="ambiguous migration path"):
        registry.plan("0", "3")


def test_schema_inspection_does_not_decode_unknown_bundle() -> None:
    document = json.dumps({"schema_version": "future-name"})
    assert inspect_audit_bundle_schema(document) == "future-name"
