"""
Dependency Analysis Module.

Analyzes import/dependency relationships between modules
to detect circular dependencies and architectural issues.
"""

from __future__ import annotations

import ast
import os
from collections import defaultdict
from pathlib import Path
from typing import Optional

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import DependencyGraph, DependencyNode


class DependencyAnalyzer:
    """
    Analyzes dependencies between modules.

    Detects circular dependencies, analyzes coupling,
    and identifies architectural problems.
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.external_modules = self._get_external_modules()

    def _get_external_modules(self) -> set[str]:
        """Get set of known external modules."""
        return {
            # Standard library
            "os",
            "sys",
            "re",
            "json",
            "datetime",
            "time",
            "math",
            "random",
            "collections",
            "itertools",
            "functools",
            "operator",
            "pathlib",
            "typing",
            "abc",
            "ast",
            "argparse",
            "csv",
            "io",
            "logging",
            "pickle",
            "shutil",
            "subprocess",
            "threading",
            "unittest",
            "urllib",
            "xml",
            "zipfile",
            # Common third-party
            "numpy",
            "pandas",
            "django",
            "flask",
            "requests",
            "pytest",
            "unittest",
            "setuptools",
            "pip",
            "click",
            "rich",
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "tensorflow",
            "torch",
            "sklearn",
        }

    def analyze_project(self, file_paths: list[str]) -> DependencyGraph:
        """
        Analyze dependencies across all files.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            DependencyGraph with all nodes and edges
        """
        graph = DependencyGraph()

        # Build module map
        modules: dict[str, str] = {}  # module_name -> file_path

        for file_path in file_paths:
            if file_path.endswith(".py"):
                module_name = self._file_to_module(file_path)
                modules[module_name] = file_path

                # Create node for each module
                graph.add_node(
                    DependencyNode(
                        name=module_name,
                        path=file_path,
                        node_type="module" if "__init__" not in file_path else "package",
                    )
                )

        # Analyze imports in each file
        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                imports = self._extract_imports(file_path)
                module_name = self._file_to_module(file_path)

                for imported in imports:
                    # Check if it's an internal module
                    if imported in modules:
                        graph.add_edge(module_name, imported)
                    elif imported not in self.external_modules:
                        # Unknown module - might be third-party
                        node = DependencyNode(
                            name=imported,
                            path=imported,
                            node_type="external",
                            is_external=True,
                        )
                        graph.add_node(node)
                        graph.add_edge(module_name, imported)

            except Exception as e:
                print(f"Error analyzing imports in {file_path}: {e}")

        return graph

    def _extract_imports(self, file_path: str) -> list[str]:
        """Extract all imports from a Python file."""
        imports = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])

        except SyntaxError:
            pass

        return imports

    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        # Remove common prefixes and extensions
        path = Path(file_path)

        # Handle __init__.py
        if path.name == "__init__.py":
            module_path = path.parent
        else:
            module_path = path.with_suffix("")

        # Get relative path from project root
        parts = []
        for part in module_path.parts:
            if part.startswith("."):
                continue
            if part in ["src", "lib", "app"]:
                break
            parts.append(part)

        return ".".join(parts) if parts else module_path.name

    def find_circular_dependencies(self, graph: DependencyGraph) -> list[list[str]]:
        """
        Find all circular dependencies in the graph.

        Args:
            graph: DependencyGraph to analyze

        Returns:
            List of cycles, where each cycle is a list of module names
        """
        return graph.find_cycles()

    def calculate_coupling(self, graph: DependencyGraph) -> dict[str, float]:
        """
        Calculate coupling metrics for each module.

        Args:
            graph: DependencyGraph to analyze

        Returns:
            Dictionary mapping module names to coupling scores
        """
        coupling_scores = {}

        for name, node in graph.nodes.items():
            if node.is_external:
                continue

            # Afferent coupling (incoming dependencies)
            afferent = len(node.imported_by)

            # Efferent coupling (outgoing dependencies)
            efferent = len(node.imports)

            # Coupling score (higher = more coupled)
            total_coupling = afferent + efferent
            instability = efferent / (total_coupling + 1)  # Instability index

            coupling_scores[name] = {
                "afferent": afferent,
                "efferent": efferent,
                "instability": instability,
                "score": total_coupling,
            }

        return coupling_scores

    def find_hub_modules(self, graph: DependencyGraph) -> list[str]:
        """
        Find hub modules (high fan-in/fan-out).

        These are modules that many other modules depend on,
        making them critical points in the architecture.
        """
        hubs = []

        for name, node in graph.nodes.items():
            fan_in = len(node.imported_by)
            fan_out = len(node.imports)

            # A module is a hub if it has both high fan-in and fan-out
            if fan_in >= 3 and fan_out >= 3:
                hubs.append(name)

        return hubs

    def find_unstable_modules(self, graph: DependencyGraph) -> list[str]:
        """
        Find unstable modules with high efferent coupling.

        These modules depend on many others and are difficult to test
        and maintain independently.
        """
        unstable = []

        for name, node in graph.nodes.items():
            if node.is_external:
                continue

            efferent = len(node.imports)
            if efferent >= 5:
                unstable.append(name)

        return unstable

    def analyze_package_structure(self, file_paths: list[str]) -> dict:
        """
        Analyze the package structure and provide recommendations.

        Returns a dictionary with analysis results and recommendations.
        """
        graph = self.analyze_project(file_paths)

        cycles = graph.find_cycles()
        hubs = self.find_hub_modules(graph)
        unstable = self.find_unstable_modules(graph)
        dead_code = graph.find_dead_code()

        return {
            "cycles": cycles,
            "hub_modules": hubs,
            "unstable_modules": unstable,
            "dead_code": dead_code,
            "total_modules": len([n for n in graph.nodes.values() if not n.is_external]),
            "total_dependencies": len(graph.edges),
            "coupling_scores": self.calculate_coupling(graph),
        }
