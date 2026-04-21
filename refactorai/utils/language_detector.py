"""
Language Detection Module.

Detects programming languages used in a project.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


class LanguageDetector:
    """
    Detects programming languages used in a project.

    Uses file extensions and language-specific files to determine
    the primary languages in use.
    """

    # Language signatures
    LANGUAGE_SIGNATURES = {
        "python": {".py", ".pyw", ".pyi"},
        "javascript": {".js", ".jsx", ".mjs", ".cjs"},
        "typescript": {".ts", ".tsx"},
        "java": {".java"},
        "cpp": {".cpp", ".c", ".cc", ".cxx", ".h", ".hpp", ".hh"},
        "csharp": {".cs"},
        "go": {".go"},
        "rust": {".rs"},
        "ruby": {".rb"},
        "php": {".php"},
        "swift": {".swift"},
        "kotlin": {".kt", ".kts"},
        "scala": {".scala"},
        "html": {".html", ".htm"},
        "css": {".css", ".scss", ".sass", ".less"},
        "sql": {".sql"},
        "shell": {".sh", ".bash", ".zsh"},
    }

    # Language-specific files
    LANGUAGE_FILES = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"],
        "javascript": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
        "typescript": ["tsconfig.json"],
        "java": ["pom.xml", "build.gradle", "gradlew"],
        "go": ["go.mod", "go.sum"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "ruby": ["Gemfile", "Gemfile.lock"],
        "php": ["composer.json"],
        "swift": ["Package.swift"],
        "kotlin": ["build.gradle.kts"],
    }

    def detect(self, project_path: str) -> str:
        """
        Detect the primary language of a project.

        Args:
            project_path: Path to the project

        Returns:
            Detected language name, or "unknown"
        """
        languages = self.detect_all(project_path)
        if not languages:
            return "unknown"

        # Return the most prevalent language
        return max(languages.items(), key=lambda x: x[1])[0]

    def detect_all(self, project_path: str) -> dict[str, int]:
        """
        Detect all languages and their prevalence.

        Args:
            project_path: Path to the project

        Returns:
            Dictionary mapping language names to file counts
        """
        project_path = os.path.abspath(project_path)
        languages: dict[str, int] = {}

        for root, _, files in os.walk(project_path):
            # Skip excluded directories
            if any(
                excluded in root
                for excluded in [
                    ".git",
                    "node_modules",
                    "__pycache__",
                    ".venv",
                    "venv",
                ]
            ):
                continue

            for filename in files:
                ext = Path(filename).suffix.lower()

                for lang, extensions in self.LANGUAGE_SIGNATURES.items():
                    if ext in extensions:
                        languages[lang] = languages.get(lang, 0) + 1
                        break

        return languages

    def detect_from_file(self, file_path: str) -> str:
        """
        Detect language from a single file.

        Args:
            file_path: Path to the file

        Returns:
            Detected language name
        """
        ext = Path(file_path).suffix.lower()

        for lang, extensions in self.LANGUAGE_SIGNATURES.items():
            if ext in extensions:
                return lang

        return "unknown"

    def get_project_info(self, project_path: str) -> dict:
        """
        Get comprehensive language information for a project.

        Returns:
            Dictionary with language details
        """
        languages = self.detect_all(project_path)

        # Check for language-specific files
        project_path = os.path.abspath(project_path)
        for lang, files in self.LANGUAGE_FILES.items():
            for filename in files:
                filepath = os.path.join(project_path, filename)
                if os.path.exists(filepath):
                    languages[f"{lang}_config"] = 1

        return {
            "primary": self.detect(project_path),
            "all": languages,
            "file_count": sum(languages.values()),
        }
