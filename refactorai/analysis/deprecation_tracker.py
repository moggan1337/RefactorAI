"""
API Deprecation Tracking Module.

Tracks usage of deprecated APIs and provides migration guidance.
"""

from __future__ import annotations

import ast
import re
from typing import Optional

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import DeprecationWarning, Location, Severity


class DeprecationTracker:
    """
    Tracks usage of deprecated APIs.

    Maintains a database of known deprecations and scans
    code for their usage.
    """

    # Database of common deprecations (can be extended)
    DEPRECATIONS = {
        # Python standard library
        "collections.Callable": {
            "alternative": "typing.Callable",
            "version_deprecated": "3.10",
            "version_removal": "3.14",
        },
        "collections.abc.Callable": {
            "alternative": "typing.Callable",
            "version_deprecated": "3.10",
            "version_removal": "3.14",
        },
        "asyncio.coroutines.coroutine": {
            "alternative": "async def",
            "version_deprecated": "3.8",
            "version_removal": "3.12",
        },
        "np.int": {
            "alternative": "int",
            "version_deprecated": "1.20",
            "version_removal": "2.0",
        },
        "np.float": {
            "alternative": "float",
            "version_deprecated": "1.20",
            "version_removal": "2.0",
        },
        "typing.Pattern": {
            "alternative": "typing.re.Pattern",
            "version_deprecated": "3.9",
            "version_removal": "3.12",
        },
        # Django
        "django.conf.urls.url": {
            "alternative": "django.urls.path or django.urls.re_path",
            "version_deprecated": "3.1",
            "version_removal": "4.0",
        },
        "django.utils.encoding.force_text": {
            "alternative": "str",
            "version_deprecated": "3.0",
            "version_removal": "4.0",
        },
        # Flask
        "flask.Flask.errorhandler": {
            "alternative": "flask.Flask.register_error_handler",
            "version_deprecated": "2.2",
            "version_removal": "3.0",
        },
        # Pandas
        "pandas.isnull": {
            "alternative": "pd.isna",
            "version_deprecated": "1.0",
            "version_removal": "2.0",
        },
        "pandas.notnull": {
            "alternative": "pd.notna",
            "version_deprecated": "1.0",
            "version_removal": "2.0",
        },
        # Requests
        "requests.models.Response.json": {
            "alternative": "response.json()",
            "version_deprecated": "2.0",
            "version_removal": "3.0",
        },
    }

    # Patterns for detecting deprecated patterns
    DEPRECATION_PATTERNS = [
        (r"getattr\s*\(\s*\w+\s*,\s*['\"]__class__['\"]", "Accessing __class__ via getattr", Severity.LOW),
        (r"\.iteritems\s*\(", "dict.iteritems()", Severity.MEDIUM),
        (r"\.itervalues\s*\(", "dict.itervalues()", Severity.MEDIUM),
        (r"\.iterkeys\s*\(", "dict.iterkeys()", Severity.MEDIUM),
        (r"\bexec\s*\(.*\)", "exec() function", Severity.MEDIUM),
        (r"\bapply\s*\(", "apply() function", Severity.MEDIUM),
        (r"from\s+\w+\s+import\s+\*\s*;", "Wildcard import", Severity.LOW),
    ]

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def track_deprecations(self, file_paths: list[str]) -> list[DeprecationWarning]:
        """
        Track all deprecated API usage in the given files.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            List of DeprecationWarning objects
        """
        warnings = []

        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                file_warnings = self._analyze_file(file_path)
                warnings.extend(file_warnings)
            except Exception as e:
                print(f"Error tracking deprecations in {file_path}: {e}")

        return warnings

    def _analyze_file(self, file_path: str) -> list[DeprecationWarning]:
        """Analyze a single file for deprecated API usage."""
        warnings = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lines = content.split("\n")

        # Check for known deprecations
        for name, info in self.DEPRECATIONS.items():
            # Simple string matching (can be enhanced with AST)
            for i, line in enumerate(lines):
                if name in line and not line.strip().startswith("#"):
                    warnings.append(
                        DeprecationWarning(
                            api_name=name,
                            deprecation_type="symbol",
                            alternative=info["alternative"],
                            version_deprecated=info.get("version_deprecated"),
                            version_removal=info.get("version_removal"),
                            severity=Severity.HIGH,
                            locations=[
                                Location(
                                    file_path=file_path,
                                    line_start=i + 1,
                                    line_end=i + 1,
                                    snippet=line.strip(),
                                )
                            ],
                        )
                    )

        # Check for pattern-based deprecations
        for pattern, description, severity in self.DEPRECATION_PATTERNS:
            for i, line in enumerate(lines):
                if re.search(pattern, line) and not line.strip().startswith("#"):
                    warnings.append(
                        DeprecationWarning(
                            api_name=description,
                            deprecation_type="pattern",
                            alternative=self._get_alternative_for_pattern(description),
                            severity=severity,
                            locations=[
                                Location(
                                    file_path=file_path,
                                    line_start=i + 1,
                                    line_end=i + 1,
                                    snippet=line.strip(),
                                )
                            ],
                        )
                    )

        return warnings

    def _get_alternative_for_pattern(self, description: str) -> str:
        """Get the recommended alternative for a pattern."""
        alternatives = {
            "dict.iteritems()": "dict.items()",
            "dict.itervalues()": "dict.values()",
            "dict.iterkeys()": "dict.keys()",
            "exec() function": "Use exec() with care or refactor",
            "apply() function": "Direct function call",
            "Wildcard import": "Explicit imports",
        }
        return alternatives.get(description, "Refactor to use current best practices")

    def add_custom_deprecation(
        self,
        api_name: str,
        alternative: str,
        deprecation_type: str = "symbol",
        version_deprecated: Optional[str] = None,
        version_removal: Optional[str] = None,
    ) -> None:
        """
        Add a custom deprecation to track.

        Args:
            api_name: Name of the deprecated API
            alternative: Recommended alternative
            deprecation_type: Type of deprecation
            version_deprecated: Version when deprecated
            version_removal: Version when it will be removed
        """
        self.DEPRECATIONS[api_name] = {
            "alternative": alternative,
            "version_deprecated": version_deprecated,
            "version_removal": version_removal,
        }

    def load_deprecations_from_file(self, file_path: str) -> None:
        """
        Load additional deprecations from a YAML or JSON file.

        Args:
            file_path: Path to deprecations file
        """
        import json
        import yaml

        try:
            with open(file_path, "r") as f:
                if file_path.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            if isinstance(data, dict):
                self.DEPRECATIONS.update(data)

        except Exception as e:
            print(f"Error loading deprecations from {file_path}: {e}")

    def get_migration_guide(self, deprecation: DeprecationWarning) -> str:
        """
        Generate a migration guide for a deprecation.

        Args:
            deprecation: The deprecation to migrate

        Returns:
            Migration guide as a string
        """
        guide = f"# Migration Guide: {deprecation.api_name}\n\n"

        if deprecation.version_deprecated:
            guide += f"**Deprecated in:** Version {deprecation.version_deprecated}\n"
        if deprecation.version_removal:
            guide += f"**Will be removed in:** Version {deprecation.version_removal}\n"
        guide += f"\n**Recommended Alternative:**\n```\n{deprecation.alternative}\n```\n\n"

        if deprecation.locations:
            guide += "**Affected Locations:**\n"
            for loc in deprecation.locations:
                guide += f"- {loc.file_path}:{loc.line_start}\n"
            guide += "\n"

        return guide
