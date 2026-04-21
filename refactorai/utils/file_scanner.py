"""
File Scanner Module.

Scans directories for source code files to analyze.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from refactorai.models.project import AnalysisConfig, FileType


class FileScanner:
    """
    Scans project directories for source files.

    Handles various file types and respects configuration
    for including/excluding certain paths.
    """

    # Default exclusions
    DEFAULT_EXCLUDES = {
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "build",
        "dist",
        "*.egg-info",
        ".eggs",
        "htmlcov",
        ".coverage",
    }

    # File type mappings
    EXTENSION_MAP = {
        ".py": FileType.PYTHON,
        ".js": FileType.JAVASCRIPT,
        ".jsx": FileType.JAVASCRIPT,
        ".ts": FileType.TYPESCRIPT,
        ".tsx": FileType.TYPESCRIPT,
        ".java": FileType.JAVA,
        ".cpp": FileType.CPP,
        ".c": FileType.CPP,
        ".h": FileType.CPP,
        ".hpp": FileType.CPP,
        ".cs": FileType.CSHARP,
        ".go": FileType.GO,
        ".rs": FileType.RUST,
        ".rb": FileType.RUBY,
        ".php": FileType.PHP,
        ".swift": FileType.SWIFT,
        ".kt": FileType.KOTLIN,
        ".kts": FileType.KOTLIN,
    }

    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.excludes = set(self.DEFAULT_EXCLUDES)

    def scan(self, project_path: str) -> list[str]:
        """
        Scan a project directory for source files.

        Args:
            project_path: Path to the project root

        Returns:
            List of absolute file paths to analyze
        """
        files = []
        project_path = os.path.abspath(project_path)

        for root, dirs, filenames in os.walk(project_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d, os.path.join(root, d))]

            # Process files
            for filename in filenames:
                file_path = os.path.join(root, filename)

                if self._should_include(file_path):
                    files.append(file_path)

        return sorted(files)

    def _should_exclude(self, name: str, full_path: str) -> bool:
        """Check if a path should be excluded."""
        # Check exclusions
        if name in self.excludes:
            return True

        # Check for hidden files/directories
        if name.startswith("."):
            # But allow some
            if name in {".github", ".gitignore", ".dockerignore"}:
                return False
            return True

        # Check against config
        if not self.config.include_venv and any(
            v in full_path for v in ["venv", ".venv", "env", ".env"]
        ):
            return True

        if not self.config.include_tests and "test" in name.lower():
            # But still include test files unless explicitly excluded
            pass

        return False

    def _should_include(self, file_path: str) -> bool:
        """Check if a file should be included in analysis."""
        # Check extension
        ext = Path(file_path).suffix.lower()
        file_type = self.EXTENSION_MAP.get(ext)

        if not file_type:
            return False

        # Check against config file types
        if self.config.file_types and file_type not in self.config.file_types:
            return False

        # Exclude non-test files if include_tests is False
        if not self.config.include_tests:
            if "test" in file_path.lower() and not any(
                s in file_path.lower() for s in ["tests/", "/tests", "test_", "_test."]
            ):
                pass  # This is actually a non-test file
            elif any(s in file_path.lower() for s in ["tests/", "/tests", "test_", "_test.", "/test"]):
                return False

        # Check file size (skip very large files)
        try:
            size = os.path.getsize(file_path)
            if size > 10_000_000:  # 10MB
                return False
        except OSError:
            return False

        return True

    def get_project_stats(self, project_path: str) -> dict:
        """
        Get statistics about the project structure.

        Args:
            project_path: Path to the project

        Returns:
            Dictionary with project statistics
        """
        files = self.scan(project_path)

        stats = {
            "total_files": len(files),
            "by_language": {},
            "total_lines": 0,
            "total_size_bytes": 0,
        }

        for file_path in files:
            ext = Path(file_path).suffix.lower()
            lang = self.EXTENSION_MAP.get(ext, "other")

            if lang not in stats["by_language"]:
                stats["by_language"][lang] = {"files": 0, "lines": 0}

            stats["by_language"][lang]["files"] += 1

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = len(content.split("\n"))
                    stats["by_language"][lang]["lines"] += lines
                    stats["total_lines"] += lines
            except Exception:
                pass

            try:
                stats["total_size_bytes"] += os.path.getsize(file_path)
            except OSError:
                pass

        return stats

    def find_entry_points(self, project_path: str) -> list[str]:
        """Find potential entry point files."""
        entry_points = []
        files = self.scan(project_path)

        for file_path in files:
            name = Path(file_path).stem.lower()
            if name in ["main", "app", "application", "run", "cli", "__main__"]:
                entry_points.append(file_path)

            # Check for __main__.py files
            if file_path.endswith("__main__.py"):
                entry_points.append(file_path)

        return entry_points
