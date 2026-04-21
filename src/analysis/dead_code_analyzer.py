"""
Dead Code Detection Module.

Identifies potentially dead code including:
- Unused functions and classes
- Unreachable code
- Unused imports
- Unused variables
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Optional, Set


class DeadCodeAnalyzer:
    """
    Detects dead code patterns in source code.

    Uses static analysis to identify code that is likely
    unused or unreachable.
    """

    def __init__(self, config):
        self.config = config
        self._entry_points = {"main", "__main__", "app", "application", "run"}

    def find_dead_code(self, file_paths: list[str]) -> list[str]:
        """
        Find all dead code across the project.

        Args:
            file_paths: List of Python file paths

        Returns:
            List of dead code locations (file paths or function names)
        """
        # Collect all defined symbols and all references
        all_definitions: dict[str, dict] = {}
        all_references: dict[str, Set[str]] = {}

        # First pass: collect all definitions
        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                definitions = self._collect_definitions(file_path)
                for name, info in definitions.items():
                    all_definitions[name] = {**info, "file": file_path}
            except Exception as e:
                print(f"Error collecting definitions from {file_path}: {e}")

        # Second pass: collect all references
        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                references = self._collect_references(file_path)
                for name in references:
                    if name not in all_references:
                        all_references[name] = set()
                    all_references[name].add(file_path)
            except Exception as e:
                print(f"Error collecting references from {file_path}: {e}")

        # Find unused definitions
        dead_code = []

        for name, info in all_definitions.items():
            # Skip entry points and special names
            if name in self._entry_points or name.startswith("_"):
                continue

            # Check if it's referenced anywhere
            if name not in all_references or not all_references[name]:
                # Double-check: maybe it's defined but never used
                is_used = False

                # Check if it's a public API (exported)
                if info.get("is_exported"):
                    continue

                # Check if it's a test file
                if "test" in info["file"].lower():
                    continue

                dead_code.append(f"{info['file']}:{name}")

        return dead_code

    def _collect_definitions(self, file_path: str) -> dict:
        """Collect all symbol definitions from a file."""
        definitions = {}

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            # Check if file has __all__ exports
            is_exported = self._has_exports(tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    definitions[node.name] = {
                        "type": "function",
                        "lineno": node.lineno,
                        "is_exported": node.name in is_exported,
                    }

                elif isinstance(node, ast.AsyncFunctionDef):
                    definitions[node.name] = {
                        "type": "async_function",
                        "lineno": node.lineno,
                        "is_exported": node.name in is_exported,
                    }

                elif isinstance(node, ast.ClassDef):
                    definitions[node.name] = {
                        "type": "class",
                        "lineno": node.lineno,
                        "is_exported": node.name in is_exported,
                    }

                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Skip module-level constants (usually UPPER_CASE)
                            if not target.id.isupper():
                                definitions[target.id] = {
                                    "type": "variable",
                                    "lineno": node.lineno,
                                    "is_exported": target.id in is_exported,
                                }

        except SyntaxError:
            pass

        return definitions

    def _collect_references(self, file_path: str) -> Set[str]:
        """Collect all symbol references from a file."""
        references = set()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    references.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        references.add(node.value.id)

        except SyntaxError:
            pass

        return references

    def _has_exports(self, tree: ast.AST) -> Set[str]:
        """Check for __all__ export list."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            return {
                                elt.s if isinstance(elt, ast.Constant) else elt.value
                                for elt in node.value.elts
                                if isinstance(elt, (ast.Str, ast.Constant))
                            }
        return set()

    def find_unreachable_code(self, file_path: str) -> list[dict]:
        """
        Find unreachable code in a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of unreachable code locations
        """
        unreachable = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    unreachable.extend(self._check_function_unreachable(node))

        except SyntaxError:
            pass

        return unreachable

    def _check_function_unreachable(self, func: ast.FunctionDef) -> list[dict]:
        """Check for unreachable code within a function."""
        unreachable = []

        # Check for empty functions (likely placeholders)
        if len(func.body) == 1 and isinstance(func.body[0], ast.Pass):
            unreachable.append(
                {
                    "type": "empty_function",
                    "name": func.name,
                    "line": func.lineno,
                    "suggestion": "Remove empty function or implement it",
                }
            )

        # Check for TODO/FIXME comments
        for i, stmt in enumerate(func.body):
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if isinstance(stmt.value.value, str):
                    comment = stmt.value.value.lower()
                    if "todo" in comment or "fixme" in comment or "xxx" in comment:
                        unreachable.append(
                            {
                                "type": "unresolved_todo",
                                "name": func.name,
                                "line": stmt.lineno,
                                "comment": comment,
                            }
                        )

        return unreachable

    def find_unused_imports(self, file_path: str) -> list[str]:
        """
        Find unused imports in a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of unused import names
        """
        unused_imports = []
        imports = {}
        references: Set[str] = set()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            # Collect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name.split(".")[0]
                        imports[name] = {"line": node.lineno, "full_name": alias.name}

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            name = alias.asname if alias.asname else alias.name
                            imports[name] = {"line": node.lineno, "full_name": f"{node.module}.{alias.name}"}

            # Collect references
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    references.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        references.add(node.value.id)

            # Find unused
            for name, info in imports.items():
                if name not in references and name not in ("*",):
                    unused_imports.append(f"{info['full_name']} (line {info['line']})")

        except SyntaxError:
            pass

        return unused_imports

    def find_speculative_generality(self, file_paths: list[str]) -> list[dict]:
        """
        Find code written for speculative future use.

        These are classes/functions that exist "just in case"
        but are not currently used.
        """
        speculative = []

        dead_code = self.find_dead_code(file_paths)

        # Additional heuristics for speculative generality
        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Check for abstract classes with few concrete implementations
                    if isinstance(node, ast.ClassDef):
                        if self._is_base_class(node) and self._has_few_implementations(node, tree):
                            speculative.append(
                                {
                                    "file": file_path,
                                    "type": "abstract_base_class",
                                    "name": node.name,
                                    "line": node.lineno,
                                    "reason": "Abstract class with few implementations may be over-engineered",
                                }
                            )

            except SyntaxError:
                pass

        return speculative
