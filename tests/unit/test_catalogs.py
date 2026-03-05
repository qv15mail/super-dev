"""
枚举目录一致性测试
"""

import pytest

from super_dev.catalogs import (
    BACKEND_TEMPLATE_CATALOG,
    CICD_PLATFORM_CATALOG,
    CICD_PLATFORM_IDS,
    CICD_PLATFORM_TARGET_IDS,
    DOMAIN_CATALOG,
    DOMAIN_IDS,
    FULL_FRONTEND_TEMPLATE_CATALOG,
    FULL_FRONTEND_TEMPLATE_IDS,
    HOST_COMMAND_CANDIDATES,
    HOST_PATH_PATTERNS,
    HOST_TOOL_CATALOG,
    HOST_TOOL_CATEGORY_MAP,
    HOST_TOOL_IDS,
    LANGUAGE_PREFERENCE_CATALOG,
    PIPELINE_BACKEND_IDS,
    PIPELINE_FRONTEND_TEMPLATE_CATALOG,
    PIPELINE_FRONTEND_TEMPLATE_IDS,
    PLATFORM_CATALOG,
    PLATFORM_IDS,
)
from super_dev.config import ConfigManager
from super_dev.integrations import IntegrationManager
from super_dev.skills import SkillManager


def test_backend_catalog_ids_unique():
    ids = [item["id"] for item in BACKEND_TEMPLATE_CATALOG]
    assert ids == list(PIPELINE_BACKEND_IDS)
    assert len(ids) == len(set(ids))
    assert "none" in ids


def test_language_catalog_ids_unique():
    ids = [item["id"] for item in LANGUAGE_PREFERENCE_CATALOG]
    assert len(ids) == len(set(ids))
    assert {"python", "typescript", "rust", "sql"}.issubset(set(ids))


def test_platform_catalog_ids_unique():
    ids = [item["id"] for item in PLATFORM_CATALOG]
    assert ids == list(PLATFORM_IDS)
    assert len(ids) == len(set(ids))


def test_frontend_catalog_ids_unique():
    pipeline_ids = [item["id"] for item in PIPELINE_FRONTEND_TEMPLATE_CATALOG]
    full_ids = [item["id"] for item in FULL_FRONTEND_TEMPLATE_CATALOG]
    assert pipeline_ids == list(PIPELINE_FRONTEND_TEMPLATE_IDS)
    assert full_ids == list(FULL_FRONTEND_TEMPLATE_IDS)
    assert len(pipeline_ids) == len(set(pipeline_ids))
    assert len(full_ids) == len(set(full_ids))
    assert set(pipeline_ids).issubset(set(full_ids))


def test_domain_catalog_ids_unique():
    ids = [item["id"] for item in DOMAIN_CATALOG]
    assert ids == list(DOMAIN_IDS)
    assert len(ids) == len(set(ids))
    assert "" in ids


def test_cicd_catalog_ids_unique():
    ids = [item["id"] for item in CICD_PLATFORM_CATALOG]
    assert ids == list(CICD_PLATFORM_IDS)
    assert len(ids) == len(set(ids))
    assert ids[0] == "all"
    assert set(CICD_PLATFORM_TARGET_IDS) == {"github", "gitlab", "jenkins", "azure", "bitbucket"}


def test_host_tool_catalog_ids_unique():
    ids = [item["id"] for item in HOST_TOOL_CATALOG]
    assert ids == list(HOST_TOOL_IDS)
    assert len(ids) == len(set(ids))
    assert {
        "claude-code",
        "codex-cli",
        "gemini-cli",
        "kimi-cli",
        "kiro-cli",
        "qoder-cli",
        "qoder",
    }.issubset(set(ids))


def test_host_detection_catalogs_reference_known_hosts():
    host_set = set(HOST_TOOL_IDS)
    assert set(HOST_COMMAND_CANDIDATES).issubset(host_set)
    assert set(HOST_PATH_PATTERNS).issubset(host_set)


def test_host_tool_category_map_is_complete():
    host_set = set(HOST_TOOL_IDS)
    assert set(HOST_TOOL_CATEGORY_MAP) == host_set
    assert set(HOST_TOOL_CATEGORY_MAP.values()).issubset({"cli", "ide"})


def test_host_support_matrix_is_aligned_with_catalogs():
    integration_gaps = IntegrationManager.coverage_gaps()
    assert integration_gaps["missing_in_targets"] == []
    assert integration_gaps["extra_in_targets"] == []
    assert integration_gaps["missing_in_slash"] == []
    assert integration_gaps["extra_in_slash"] == []

    skill_gaps = SkillManager.coverage_gaps()
    assert skill_gaps["missing_in_skill_targets"] == []
    assert skill_gaps["extra_in_skill_targets"] == []


@pytest.mark.parametrize("backend", PIPELINE_BACKEND_IDS)
def test_config_manager_accepts_catalog_backends(temp_project_dir, backend: str):
    manager = ConfigManager(temp_project_dir)
    manager.create(name=f"catalog-{backend}", backend=backend)
    is_valid, errors = manager.validate()
    assert is_valid
    assert errors == []


@pytest.mark.parametrize("platform", PLATFORM_IDS)
def test_config_manager_accepts_catalog_platforms(temp_project_dir, platform: str):
    manager = ConfigManager(temp_project_dir)
    manager.create(name=f"catalog-{platform}", platform=platform)
    is_valid, errors = manager.validate()
    assert is_valid
    assert errors == []


@pytest.mark.parametrize("frontend", FULL_FRONTEND_TEMPLATE_IDS)
def test_config_manager_accepts_catalog_frontends(temp_project_dir, frontend: str):
    manager = ConfigManager(temp_project_dir)
    manager.create(name=f"catalog-{frontend}", frontend=frontend)
    is_valid, errors = manager.validate()
    assert is_valid
    assert errors == []
