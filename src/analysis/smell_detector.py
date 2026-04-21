"""
Code Smell Detection Module.

Detects various types of code smells using static analysis
and pattern matching techniques.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Optional

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import (
    CodeSmell,
    CodeSmellType,
    Severity,
    Location,
    ComplexityMetrics,
)


class SmellDetector:
    """
    Detects code smells in source code.

    Uses AST parsing and pattern matching to identify common
    code quality issues.
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def detect_in_file(self, file_path: str, content: str) -> list[CodeSmell]:
        """
        Detect all code smells in a file.

        Args:
            file_path: Path to the source file
            content: Source code content

        Returns:
            List of detected code smells
        """
        smells = []

        try:
            if self._is_python(file_path):
                smells.extend(self._detect_python_smells(file_path, content))
            elif self._is_javascript(file_path):
                smells.extend(self._detect_javascript_smells(file_path, content))
        except Exception as e:
            print(f"Error detecting smells in {file_path}: {e}")

        return smells

    def _is_python(self, file_path: str) -> bool:
        """Check if file is Python."""
        return file_path.endswith(".py")

    def _is_javascript(self, file_path: str) -> bool:
        """Check if file is JavaScript/TypeScript."""
        return file_path.endswith((".js", ".jsx", ".ts", ".tsx"))

    def _detect_python_smells(self, file_path: str, content: str) -> list[CodeSmell]:
        """Detect code smells in Python code."""
        smells = []

        try:
            tree = ast.parse(content)

            # Collect all classes and functions
            classes = self._get_classes(tree)
            functions = self._get_functions(tree)

            # Detect God Class
            for cls in classes:
                if self._is_god_class(cls, tree):
                    smells.append(
                        CodeSmell(
                            smell_type=CodeSmellType.GOD_CLASS,
                            severity=Severity.HIGH,
                            location=Location(
                                file_path=file_path,
                                line_start=cls.lineno,
                                line_end=cls.end_lineno or cls.lineno + 50,
                                snippet=self._get_snippet(content, cls.lineno, cls.end_lineno),
                            ),
                            name="God Class",
                            description=f"Class '{cls.name}' is too large with too many responsibilities",
                            effort_hours=16.0,
                            tags=["design", "oop", "large-class"],
                        )
                    )

            # Detect Long Methods
            for func in functions:
                func_lines = (func.end_lineno or func.lineno) - func.lineno
                if func_lines > self.config.max_method_length:
                    severity = Severity.CRITICAL if func_lines > self.config.max_method_length * 2 else Severity.MEDIUM
                    smells.append(
                        CodeSmell(
                            smell_type=CodeSmellType.LONG_METHOD,
                            severity=severity,
                            location=Location(
                                file_path=file_path,
                                line_start=func.lineno,
                                line_end=func.end_lineno or func.lineno + func_lines,
                                snippet=self._get_snippet(content, func.lineno, func.end_lineno),
                            ),
                            name=f"Long Method: {func.name}",
                            description=f"Method has {func_lines} lines (threshold: {self.config.max_method_length})",
                            effort_hours=max(2.0, func_lines / 10),
                            tags=["implementation", "length"],
                        )
                    )

            # Detect Complex Methods
            complexity = self._calculate_cyclomatic_complexity(func)
            if complexity > self.config.max_cyclomatic_complexity:
                severity = Severity.CRITICAL if complexity > self.config.max_cyclomatic_complexity * 2 else Severity.HIGH
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.COMPLEX_METHOD,
                        severity=severity,
                        location=Location(
                            file_path=file_path,
                            line_start=func.lineno,
                            line_end=func.end_lineno or func.lineno + 20,
                            snippet=self._get_snippet(content, func.lineno, func.end_lineno),
                        ),
                        name=f"Complex Method: {func.name}",
                        description=f"Method has cyclomatic complexity of {complexity} (threshold: {self.config.max_cyclomatic_complexity})",
                        effort_hours=max(4.0, complexity),
                        tags=["complexity", "maintainability"],
                    )
                )

            # Detect Long Parameter Lists
            param_count = len(func.args.args)
            if param_count > self.config.max_parameters:
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.LONG_PARAMETER_LIST,
                        severity=Severity.MEDIUM,
                        location=Location(
                            file_path=file_path,
                            line_start=func.lineno,
                            line_end=func.end_lineno or func.lineno + 10,
                            snippet=self._get_snippet(content, func.lineno, func.end_lineno),
                        ),
                        name=f"Long Parameter List: {func.name}",
                        description=f"Function has {param_count} parameters (threshold: {self.config.max_parameters})",
                        effort_hours=2.0,
                        tags=["implementation", "parameters"],
                    )
                )

            # Detect Feature Envy
            for func in functions:
                if self._has_feature_envy(func, classes):
                    smells.append(
                        CodeSmell(
                            smell_type=CodeSmellType.FEATURE_ENVY,
                            severity=Severity.MEDIUM,
                            location=Location(
                                file_path=file_path,
                                line_start=func.lineno,
                                line_end=func.end_lineno or func.lineno + 20,
                                snippet=self._get_snippet(content, func.lineno, func.end_lineno),
                            ),
                            name=f"Feature Envy: {func.name}",
                            description=f"Method seems more interested in other classes than the one it lives in",
                            effort_hours=4.0,
                            tags=["design", "coupling"],
                        )
                    )

            # Detect Data Classes
            for cls in classes:
                if self._is_data_class(cls):
                    smells.append(
                        CodeSmell(
                            smell_type=CodeSmellType.DATA_CLASS,
                            severity=Severity.LOW,
                            location=Location(
                                file_path=file_path,
                                line_start=cls.lineno,
                                line_end=cls.end_lineno or cls.lineno + 30,
                                snippet=self._get_snippet(content, cls.lineno, cls.end_lineno),
                            ),
                            name=f"Data Class: {cls.name}",
                            description="Class that only holds data without behavior",
                            effort_hours=4.0,
                            tags=["design", "oop"],
                        )
                    )

            # Detect Magic Numbers
            magic_numbers = self._find_magic_numbers(content)
            for line_no, number in magic_numbers:
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.MAGIC_NUMBERS,
                        severity=Severity.INFO,
                        location=Location(
                            file_path=file_path,
                            line_start=line_no,
                            line_end=line_no,
                            snippet=self._get_snippet(content, line_no, line_no),
                        ),
                        name="Magic Number",
                        description=f"Magic number '{number}' should be a named constant",
                        effort_hours=0.5,
                        tags=["implementation", "readability"],
                    )
                )

        except SyntaxError:
            pass

        return smells

    def _detect_javascript_smells(self, file_path: str, content: str) -> list[CodeSmell]:
        """Detect code smells in JavaScript/TypeScript code."""
        smells = []

        # Simple line-based detection for JavaScript
        lines = content.split("\n")

        # Detect long functions (heuristic: blank lines rarely appear inside functions)
        function_starts = [i for i, line in enumerate(lines) if re.match(r"\s*(function\s+\w+|const\s+\w+\s*=|class\s+\w+)", line)]

        for start_line in function_starts:
            # Count lines until next function or significant indentation change
            func_lines = 1
            base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

            for i in range(start_line + 1, min(start_line + 200, len(lines))):
                line = lines[i]
                if line.strip() and not line.strip().startswith("//"):
                    indent = len(line) - len(line.lstrip())
                    if indent <= base_indent and line.strip():
                        break
                func_lines += 1

            if func_lines > self.config.max_method_length:
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.LONG_METHOD,
                        severity=Severity.MEDIUM,
                        location=Location(
                            file_path=file_path,
                            line_start=start_line + 1,
                            line_end=start_line + func_lines,
                            snippet="\n".join(lines[start_line : start_line + func_lines]),
                        ),
                        name=f"Long Function (line {start_line + 1})",
                        description=f"Function has {func_lines} lines (threshold: {self.config.max_method_length})",
                        effort_hours=max(2.0, func_lines / 10),
                        tags=["implementation", "length"],
                    )
                )

        return smells

    def _get_classes(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Get all class definitions from AST."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node)

        return classes

    def _get_functions(self, tree: ast.AST) -> list[ast.FunctionDef]:
        """Get all function definitions from AST (excluding nested)."""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Only top-level or directly inside class methods
                functions.append(node)

        return functions

    def _is_god_class(self, cls: ast.ClassDef, tree: ast.AST) -> bool:
        """Check if a class is a God Class."""
        # Count methods
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        # Count lines
        cls_lines = (cls.end_lineno or cls.lineno) - cls.lineno

        # Heuristics for God Class
        return len(methods) > 20 or cls_lines > self.config.max_class_length

    def _is_data_class(self, cls: ast.ClassDef) -> bool:
        """Check if a class is primarily a data container."""
        # A data class has mostly attribute assignments and simple methods
        methods = [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        attrs = [n for n in cls.body if isinstance(n, ast.AnnAssign)]

        # If it has more attribute declarations than meaningful methods
        return len(attrs) > 3 and len(methods) <= 3

    def _has_feature_envy(self, func: ast.FunctionDef, classes: list[ast.ClassDef]) -> bool:
        """Detect if a function has Feature Envy."""
        if not classes:
            return False

        # Count attribute accesses in the function
        attr_accesses = 0
        for node in ast.walk(func):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                attr_accesses += 1

        # If many attribute accesses and function is long, might have feature envy
        func_lines = (func.end_lineno or func.lineno) - func.lineno
        return attr_accesses > 5 and func_lines > 20

    def _calculate_cyclomatic_complexity(self, func: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for node in ast.walk(func):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1  # AND/OR operators
            elif isinstance(node, (ast.Compare, ast.IfExp)):
                complexity += 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += len(node.handlers)

        return complexity

    def _find_magic_numbers(self, content: str) -> list[tuple[int, str]]:
        """Find magic numbers in Python code."""
        magic_numbers = []
        lines = content.split("\n")

        # Pattern to match numbers that aren't in strings or comments
        number_pattern = re.compile(r"(?<![a-zA-Z_])(-?\d+\.?\d*)(?![a-zA-Z_\"'])")

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"') or stripped.startswith("'"):
                continue

            # Skip common magic numbers
            common_numbers = {"0", "1", "2", "-1", "100", "365", "360"}
            for match in number_pattern.findall(line):
                if match not in common_numbers:
                    magic_numbers.append((i + 1, match))

        return magic_numbers

    def _get_snippet(self, content: str, start: int, end: Optional[int] = None) -> str:
        """Get a code snippet from the content."""
        lines = content.split("\n")
        start_idx = max(0, start - 1)
        end_idx = min(len(lines), end or (start + 10))
        return "\n".join(lines[start_idx:end_idx])
