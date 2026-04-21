"""
Complexity Analysis Module.

Analyzes code complexity including cyclomatic complexity,
cognitive complexity, and maintainability metrics.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Optional

try:
    import radon
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import h_visit, mi_visit
    HAS_RADON = True
except ImportError:
    HAS_RADON = False

from refactorai.models.project import AnalysisConfig, EntityMetrics
from refactorai.models.technical_debt import (
    CodeSmell,
    CodeSmellType,
    Severity,
    Location,
    ComplexityMetrics,
)


class ComplexityAnalyzer:
    """
    Analyzes code complexity metrics.

    Calculates cyclomatic complexity, cognitive complexity,
    Halstead metrics, and maintainability index.
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self._metrics: dict[str, ComplexityMetrics] = {}

    def analyze_file(self, file_path: str, content: str) -> list[EntityMetrics]:
        """
        Analyze complexity metrics for a single file.

        Args:
            file_path: Path to the source file
            content: Source code content

        Returns:
            List of EntityMetrics for each entity in the file
        """
        metrics: list[EntityMetrics] = []

        if not file_path.endswith(".py"):
            return metrics

        try:
            tree = ast.parse(content)

            if HAS_RADON:
                # Use Radon for comprehensive metrics
                try:
                    cc_results = cc_visit(content)
                    halstead = h_visit(content)
                    maintainability = mi_visit(content)

                    for result in cc_results:
                        entity_metrics = self._create_entity_metrics(
                            file_path=file_path,
                            name=result.name,
                            entity_type=result.type,
                            lineno=result.lineno,
                            end_lineno=result.endline if hasattr(result, "endline") else None,
                            cyclomatic=result.complexity,
                            content=content,
                        )
                        metrics.append(entity_metrics)
                except Exception:
                    # Fallback to manual analysis
                    metrics.extend(self._analyze_with_ast(file_path, content, tree))
            else:
                # Manual analysis using AST
                metrics.extend(self._analyze_with_ast(file_path, content, tree))

        except SyntaxError:
            pass

        return metrics

    def analyze_files(self, file_paths: list[str]) -> list[CodeSmell]:
        """
        Analyze complexity across multiple files.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            List of code smells related to complexity issues
        """
        smells = []

        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                file_smells = self._detect_complexity_smells(file_path, content)
                smells.extend(file_smells)

                # Store metrics
                metrics = self.analyze_file(file_path, content)
                for entity in metrics:
                    key = f"{file_path}:{entity.name}"
                    self._metrics[key] = ComplexityMetrics(
                        cyclomatic_complexity=entity.cyclomatic_complexity,
                        cognitive_complexity=entity.cognitive_complexity,
                        lines_of_code=entity.lines_of_code,
                        maintainability_index=entity.maintainability_score,
                    )

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        return smells

    def _analyze_with_ast(self, file_path: str, content: str, tree: ast.AST) -> list[EntityMetrics]:
        """Analyze complexity using AST."""
        metrics = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                entity = self._create_entity_metrics(
                    file_path=file_path,
                    name=node.name,
                    entity_type="function" if not any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)) else "method",
                    lineno=node.lineno,
                    end_lineno=node.end_lineno,
                    cyclomatic=self._calc_cyclomatic(node),
                    content=content,
                )
                metrics.append(entity)

            elif isinstance(node, ast.ClassDef):
                entity = self._create_entity_metrics(
                    file_path=file_path,
                    name=node.name,
                    entity_type="class",
                    lineno=node.lineno,
                    end_lineno=node.end_lineno,
                    cyclomatic=0,
                    content=content,
                )
                metrics.append(entity)

        return metrics

    def _create_entity_metrics(
        self,
        file_path: str,
        name: str,
        entity_type: str,
        lineno: int,
        end_lineno: Optional[int],
        cyclomatic: int,
        content: str,
    ) -> EntityMetrics:
        """Create EntityMetrics from analysis results."""
        lines = content.split("\n")
        start_idx = max(0, lineno - 1)
        end_idx = min(len(lines), end_lineno or lineno + 50)

        code_lines = [l for l in lines[start_idx:end_idx] if l.strip()]

        # Count statements
        try:
            subtree = ast.parse("\n".join(lines[start_idx:end_idx]))
            statements = sum(1 for _ in ast.walk(subtree) if isinstance(_, ast.stmt))
        except Exception:
            statements = len(code_lines)

        # Calculate cognitive complexity (simplified)
        cognitive = self._calculate_cognitive_complexity(content, lineno, end_lineno)

        # Calculate maintainability index
        maintainability = self._calculate_maintainability_index(
            len(code_lines),
            cyclomatic,
            statements,
        )

        return EntityMetrics(
            name=name,
            entity_type=entity_type,
            file_path=file_path,
            line_start=lineno,
            line_end=end_lineno or lineno + len(code_lines),
            lines_of_code=len(code_lines),
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            maintainability_score=maintainability,
            statements=statements,
        )

    def _detect_complexity_smells(self, file_path: str, content: str) -> list[CodeSmell]:
        """Detect code smells related to complexity."""
        smells = []

        try:
            tree = ast.parse(content)
            lines = content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cyclomatic = self._calc_cyclomatic(node)
                    func_lines = (node.end_lineno or node.lineno) - node.lineno

                    # High cyclomatic complexity
                    if cyclomatic > self.config.max_cyclomatic_complexity:
                        severity = self._severity_from_complexity(cyclomatic, self.config.max_cyclomatic_complexity)
                        smells.append(
                            CodeSmell(
                                smell_type=CodeSmellType.COMPLEX_METHOD,
                                severity=severity,
                                location=Location(
                                    file_path=file_path,
                                    line_start=node.lineno,
                                    line_end=node.end_lineno or node.lineno + func_lines,
                                    snippet="\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno + 20]),
                                ),
                                name=f"High Cyclomatic Complexity: {node.name}",
                                description=f"Cyclomatic complexity is {cyclomatic} (threshold: {self.config.max_cyclomatic_complexity})",
                                effort_hours=max(4.0, cyclomatic / 2),
                                tags=["complexity", "maintainability"],
                            )
                        )

                    # Deep nesting
                    max_nesting = self._max_nesting_depth(node)
                    if max_nesting > self.config.max_nesting_depth:
                        smells.append(
                            CodeSmell(
                                smell_type=CodeSmellType.COMPLEX_METHOD,
                                severity=Severity.MEDIUM,
                                location=Location(
                                    file_path=file_path,
                                    line_start=node.lineno,
                                    line_end=node.end_lineno or node.lineno + func_lines,
                                ),
                                name=f"Deep Nesting: {node.name}",
                                description=f"Maximum nesting depth is {max_nesting} (threshold: {self.config.max_nesting_depth})",
                                effort_hours=2.0,
                                tags=["complexity", "readability"],
                            )
                        )

        except SyntaxError:
            pass

        return smells

    def _calc_cyclomatic(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def _calculate_cognitive_complexity(self, content: str, start: int, end: Optional[int]) -> int:
        """Calculate cognitive complexity (simplified version)."""
        lines = content.split("\n")
        snippet = "\n".join(lines[start - 1 : end or start + 20])

        cognitive = 0
        indent_level = 0

        for line in snippet.split("\n"):
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            current_indent = len(line) - len(stripped)
            indent_level = current_indent // 4  # Assume 4-space indent

            if any(kw in stripped for kw in ["if ", "elif ", "for ", "while ", "except ", "with "]):
                cognitive += 1 + indent_level
            elif "try:" in stripped:
                cognitive += 1 + indent_level
            elif "else:" in stripped and "elif" not in stripped:
                cognitive += 1 + indent_level

        return cognitive

    def _calculate_maintainability_index(
        self,
        lines_of_code: int,
        cyclomatic: int,
        statements: int,
    ) -> float:
        """
        Calculate maintainability index (0-100).

        Based on Microsoft's maintainability index formula.
        """
        import math

        if lines_of_code == 0:
            return 100.0

        # Halstead volume (simplified)
        volume = statements * math.log2(max(1, cyclomatic + 1))

        # Calculate MI
        mi = 171 - 5.2 * math.log(max(1, volume)) - 0.23 * cyclomatic - 16.2 * math.log(max(1, lines_of_code))

        # Normalize to 0-100
        mi = max(0, min(100, mi * 0.7))

        return mi

    def _max_nesting_depth(self, node: ast.FunctionDef) -> int:
        """Calculate maximum nesting depth in a function."""
        max_depth = [0]

        def visit(node: ast.AST, depth: int = 0) -> None:
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With)):
                max_depth[0] = max(max_depth[0], depth + 1)
            for child in ast.iter_child_nodes(node):
                visit(child, depth)

        visit(node)
        return max_depth[0]

    def _severity_from_complexity(self, complexity: int, threshold: int) -> Severity:
        """Determine severity based on complexity relative to threshold."""
        ratio = complexity / threshold
        if ratio >= 5:
            return Severity.CRITICAL
        elif ratio >= 3:
            return Severity.HIGH
        elif ratio >= 2:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def get_summary_metrics(self) -> dict[str, ComplexityMetrics]:
        """Get all collected metrics."""
        return self._metrics.copy()

    def get_average_complexity(self) -> float:
        """Get average cyclomatic complexity across all analyzed code."""
        if not self._metrics:
            return 0.0
        complexities = [m.cyclomatic_complexity for m in self._metrics.values()]
        return sum(complexities) / len(complexities) if complexities else 0.0

    def get_average_maintainability(self) -> float:
        """Get average maintainability index."""
        if not self._metrics:
            return 100.0
        scores = [m.maintainability_index for m in self._metrics.values()]
        return sum(scores) / len(scores) if scores else 100.0
