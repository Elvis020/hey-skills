#!/usr/bin/env python3
"""
Sentinel-Scan Pattern Prioritizer
Analyzes project shape to prioritize detector categories.
"""

import json
import sys
from pathlib import Path


def detect_project_type(project_path: str) -> list[str]:
    categories: list[str] = []
    path = Path(project_path)

    if (path / "package.json").exists():
        categories.append("node")
    if (path / "requirements.txt").exists() or (path / "setup.py").exists() or (path / "pyproject.toml").exists():
        categories.append("python")
    if (path / "Cargo.toml").exists():
        categories.append("rust")
    if (path / "go.mod").exists():
        categories.append("go")
    if (path / "pom.xml").exists() or (path / "build.gradle").exists() or (path / "build.gradle.kts").exists():
        categories.append("java")

    if any((path / f).exists() for f in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]):
        categories.append("docker")

    if (path / "terraform").is_dir() or any(path.glob("*.tf")):
        categories.append("terraform")

    if any((path / f).exists() for f in [".env", ".env.local", ".env.production", ".env.development"]):
        categories.append("env")

    return sorted(set(categories)) if categories else ["generic"]


def prioritize_patterns(categories: list[str]) -> dict:
    priority_map = {
        "node": {"critical": ["openai", "github", "aws", "stripe"], "high": ["database", "slack", "sendgrid"]},
        "python": {"critical": ["openai", "github", "aws", "stripe"], "high": ["database", "slack", "sendgrid"]},
        "go": {"critical": ["github", "aws", "stripe"], "high": ["database", "docker", "kubernetes"]},
        "rust": {"critical": ["github", "aws"], "high": ["database", "env"]},
        "java": {"critical": ["github", "aws", "azure"], "high": ["database", "docker"]},
        "docker": {"critical": ["aws", "gcp", "dockerhub"], "high": ["private_key", "registry_auth"]},
        "terraform": {"critical": ["aws", "azure", "gcp"], "high": ["digitalocean", "cloudflare"]},
        "env": {"critical": ["openai", "github", "aws", "stripe", "database"], "high": ["generic_assignment"]},
        "generic": {"critical": ["openai", "github", "aws", "stripe"], "high": ["database", "generic_assignment"]},
    }

    critical: set[str] = set()
    high: set[str] = set()

    for category in categories:
        config = priority_map.get(category)
        if not config:
            continue
        critical.update(config.get("critical", []))
        high.update(config.get("high", []))

    if not critical and not high:
        base = priority_map["generic"]
        critical.update(base["critical"])
        high.update(base["high"])

    return {
        "critical": sorted(critical),
        "high": sorted(high),
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pattern-prioritizer.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    categories = detect_project_type(project_path)
    priorities = prioritize_patterns(categories)

    result = {
        "project_path": project_path,
        "detected_categories": categories,
        "priorities": priorities,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
