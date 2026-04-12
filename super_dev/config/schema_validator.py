"""Schema validator for super-dev.yaml configuration files."""

import re

VALID_PLATFORMS = {"web", "mobile", "desktop", "api"}
VALID_PHASES = {"discovery", "intelligence", "drafting", "redteam", "qa", "delivery", "deployment"}
VALID_EXPERTS = {"PM", "ARCHITECT", "UI", "UX", "SECURITY", "CODE"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KNOWN_FIELDS = {
    "name",
    "version",
    "platform",
    "frontend",
    "backend",
    "description",
    "domain",
    "quality_gate",
    "phases",
    "experts",
    "output_dir",
    "license",
    "cli",
    "host_compatibility_min_score",
    "host_compatibility_min_ready_hosts",
    "host_profile_enforce_selected",
    "host_profile_targets",
    "knowledge_allowed_domains",
    "knowledge_cache_ttl_seconds",
    "language_preferences",
    "state_management",
    "testing_frameworks",
    "database",
    "author",
}


def validate_config(config: dict) -> list[str]:
    """Validate a super-dev.yaml configuration dict.

    Args:
        config: Parsed YAML configuration dictionary.

    Returns:
        List of validation error messages. Empty if the config is valid.
    """
    if not isinstance(config, dict):
        return ["Configuration must be a dictionary"]

    errors: list[str] = []

    # Unknown fields warning
    unknown = set(config.keys()) - KNOWN_FIELDS
    if unknown:
        errors.append(f"Unknown configuration fields (possible typos): {sorted(unknown)}")

    # Required string fields
    for field in ("name", "frontend", "backend"):
        val = config.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"'{field}' is required and must be a non-empty string")

    # version — semver
    version = config.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append("'version' must match semver pattern (x.y.z)")

    # platform
    platform = config.get("platform")
    if platform not in VALID_PLATFORMS:
        errors.append(f"'platform' must be one of {sorted(VALID_PLATFORMS)}")

    # quality_gate
    qg = config.get("quality_gate")
    if not isinstance(qg, int) or not (0 <= qg <= 100):
        errors.append("'quality_gate' must be an integer between 0 and 100")

    # phases
    phases = config.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append("'phases' must be a non-empty list")
    elif isinstance(phases, list):
        invalid = [p for p in phases if p not in VALID_PHASES]
        if invalid:
            errors.append(f"'phases' contains invalid entries: {invalid}")

    # experts
    experts = config.get("experts")
    if not isinstance(experts, list) or not experts:
        errors.append("'experts' must be a list with at least one expert")
    elif isinstance(experts, list):
        invalid = [e for e in experts if e not in VALID_EXPERTS]
        if invalid:
            errors.append(f"'experts' contains invalid entries: {invalid}")

    # Optional fields
    host_score = config.get("host_compatibility_min_score")
    if host_score is not None and (not isinstance(host_score, int) or not (0 <= host_score <= 100)):
        errors.append(
            "'host_compatibility_min_score' must be an integer between 0 and 100 if present"
        )

    ttl = config.get("knowledge_cache_ttl_seconds")
    if ttl is not None and (not isinstance(ttl, int) or ttl <= 0):
        errors.append("'knowledge_cache_ttl_seconds' must be a positive integer if present")

    return errors


class ConfigSchemaValidator:
    """Validates super-dev.yaml configuration against the expected schema."""

    def validate(self, config: dict) -> list[str]:
        """Validate config and return a list of error messages."""
        return validate_config(config)

    def validate_and_raise(self, config: dict) -> None:
        """Validate config and raise ValueError if any errors are found.

        Args:
            config: Parsed YAML configuration dictionary.

        Raises:
            ValueError: With all validation errors joined by '; '.
        """
        errors = self.validate(config)
        if errors:
            raise ValueError("; ".join(errors))

    def get_defaults(self) -> dict:
        """Return sensible default values for all configuration fields."""
        return {
            "name": "my-project",
            "version": "0.1.0",
            "platform": "web",
            "frontend": "react",
            "backend": "python",
            "quality_gate": 90,
            "phases": [
                "discovery",
                "intelligence",
                "drafting",
                "redteam",
                "qa",
                "delivery",
                "deployment",
            ],
            "experts": ["PM", "ARCHITECT", "CODE"],
            "host_compatibility_min_score": 70,
            "knowledge_cache_ttl_seconds": 3600,
        }
