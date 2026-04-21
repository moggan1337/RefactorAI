"""
Main Technical Debt Analyzer.

This is the main entry point for conducting a comprehensive
technical debt analysis of a codebase.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

from refactorai.models.project import AnalysisConfig, FileType, FileAnalysis, ModuleAnalysis, ProjectAnalysis
from refactorai.models.technical_debt import TechnicalDebt, Location, CodeSmell, CodeSmellType, Severity
from refactorai.analysis.smell_detector import SmellDetector
from refactorai.analysis.complexity_analyzer import ComplexityAnalyzer
from refactorai.analysis.duplication_finder import DuplicationFinder
from refactorai.analysis.dependency_analyzer import DependencyAnalyzer
from refactorai.analysis.dead_code_analyzer import DeadCodeAnalyzer
from refactorai.analysis.deprecation_tracker import DeprecationTracker
from refactorai.analysis.refactoring_engine import RefactoringEngine
from refactorai.analysis.sprint_impact_predictor import SprintImpactPredictor
from refactorai.utils.file_scanner import FileScanner
from refactorai.utils.language_detector import LanguageDetector


class TechDebtAnalyzer:
    """
    Main analyzer for comprehensive technical debt analysis.

    This class orchestrates all analysis modules and produces
    a complete TechnicalDebt report for a project.

    Example:
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze("/path/to/project")
        print(f"Total debt: ${result.total_debt_cost}")
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize the analyzer with optional configuration.

        Args:
            config: Analysis configuration. Uses defaults if not provided.
        """
        self.config = config or AnalysisConfig()
        self._initialize_analyzers()

    def _initialize_analyzers(self) -> None:
        """Initialize all analysis modules."""
        self.smell_detector = SmellDetector(self.config)
        self.complexity_analyzer = ComplexityAnalyzer(self.config)
        self.duplication_finder = DuplicationFinder(self.config)
        self.dependency_analyzer = DependencyAnalyzer(self.config)
        self.dead_code_analyzer = DeadCodeAnalyzer(self.config)
        self.deprecation_tracker = DeprecationTracker(self.config)
        self.refactoring_engine = RefactoringEngine(self.config)
        self.sprint_impact_predictor = SprintImpactPredictor(self.config)
        self.file_scanner = FileScanner(self.config)
        self.language_detector = LanguageDetector()

    def analyze(self, project_path: str) -> TechnicalDebt:
        """
        Perform a comprehensive technical debt analysis.

        Args:
            project_path: Path to the project directory

        Returns:
            TechnicalDebt object containing all findings
        """
        start_time = time.time()
        project_path = os.path.abspath(project_path)

        # Initialize result object
        result = TechnicalDebt(project_path=project_path)

        # Detect language
        result.language = self.language_detector.detect(project_path)

        # Scan for files to analyze
        files = self.file_scanner.scan(project_path)
        result.files_analyzed = len(files)
        result.lines_analyzed = sum(self._count_lines(f) for f in files)

        # Run all analyzers
        analyzers = []
        if self.config.analyze_complexity:
            analyzers.append(self._run_complexity_analysis)
        if self.config.analyze_duplication:
            analyzers.append(self._run_duplication_analysis)
        if self.config.analyze_dependencies:
            analyzers.append(self._run_dependency_analysis)
        if self.config.analyze_dead_code:
            analyzers.append(self._run_dead_code_analysis)
        if self.config.analyze_deprecations:
            analyzers.append(self._run_deprecation_analysis)

        for analyzer in analyzers:
            try:
                analyzer(files, result)
            except Exception as e:
                print(f"Warning: Analyzer failed: {e}")

        # Calculate complexity metrics
        if self.config.analyze_complexity:
            result.complexity_metrics = self.complexity_analyzer.get_summary_metrics()

        # Generate sprint impact if requested
        if self.config.generate_sprint_impact:
            result.sprint_impact = self.sprint_impact_predictor.predict(result)

        return result

    def analyze_with_suggestions(self, project_path: str) -> tuple[TechnicalDebt, list]:
        """
        Analyze and generate refactoring suggestions.

        Args:
            project_path: Path to the project directory

        Returns:
            Tuple of (TechnicalDebt, list of RefactoringSuggestion)
        """
        result = self.analyze(project_path)

        suggestions = []
        if self.config.generate_suggestions:
            suggestions = self.refactoring_engine.generate_suggestions(result)

        return result, suggestions

    def analyze_to_project(self, project_path: str) -> ProjectAnalysis:
        """
        Analyze and return structured ProjectAnalysis.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectAnalysis with structured results
        """
        start_time = time.time()
        project_path = os.path.abspath(project_path)

        # Create project analysis
        project_name = os.path.basename(project_path)
        analysis = ProjectAnalysis(
            project_path=project_path,
            project_name=project_name,
            config=self.config,
        )

        # Scan files
        files = self.file_scanner.scan(project_path)
        analysis.total_files = len(files)

        # Analyze each file
        for file_path in files:
            try:
                file_analysis = self._analyze_file(file_path)
                analysis.modules[0].files.append(file_analysis) if analysis.modules else None
                analysis.total_lines += file_analysis.total_lines
            except Exception as e:
                print(f"Warning: Failed to analyze {file_path}: {e}")

        analysis.analysis_duration_seconds = time.time() - start_time

        return analysis

    def _analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single file."""
        file_type = self._detect_file_type(file_path)

        # Get basic stats
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lines = content.split("\n")
        loc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        comments = sum(1 for line in lines if line.strip().startswith("#"))
        blanks = sum(1 for line in lines if not line.strip())

        file_analysis = FileAnalysis(
            file_path=file_path,
            file_type=file_type,
            lines_of_code=loc,
            lines_of_comments=comments,
            blank_lines=blanks,
        )

        # Run complexity analysis
        if self.config.analyze_complexity:
            metrics = self.complexity_analyzer.analyze_file(file_path, content)
            file_analysis.entities = metrics

        return file_analysis

    def _detect_file_type(self, file_path: str) -> FileType:
        """Detect the type of a file based on extension."""
        ext = Path(file_path).suffix.lower()
        type_map = {
            ".py": FileType.PYTHON,
            ".js": FileType.JAVASCRIPT,
            ".ts": FileType.TYPESCRIPT,
            ".java": FileType.JAVA,
            ".cpp": FileType.CPP,
            ".c": FileType.CPP,
            ".cs": FileType.CSHARP,
            ".go": FileType.GO,
            ".rs": FileType.RUST,
            ".rb": FileType.RUBY,
            ".php": FileType.PHP,
            ".swift": FileType.SWIFT,
            ".kt": FileType.KOTLIN,
        }
        return type_map.get(ext, FileType.UNKNOWN)

    def _count_lines(self, file_path: str) -> int:
        """Count non-empty lines in a file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0

    def _run_complexity_analysis(self, files: list[str], result: TechnicalDebt) -> None:
        """Run complexity analysis on files."""
        smells = self.complexity_analyzer.analyze_files(files)
        result.smells.extend(smells)

    def _run_duplication_analysis(self, files: list[str], result: TechnicalDebt) -> None:
        """Run duplication analysis on files."""
        duplications = self.duplication_finder.find_duplications(files)
        result.duplications.extend(duplications)

    def _run_dependency_analysis(self, files: list[str], result: TechnicalDebt) -> None:
        """Run dependency analysis on files."""
        dep_graph = self.dependency_analyzer.analyze_project(files)
        result.dependency_cycles = dep_graph.find_cycles()

        # Add cycle-related smells
        for cycle in result.dependency_cycles:
            for node_name in cycle:
                result.smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.CYCLIC_DEPENDENCY,
                        severity=Severity.HIGH,
                        location=Location(file_path=node_name, line_start=0, line_end=0),
                        name="Circular Dependency",
                        description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        effort_hours=4.0,
                    )
                )

    def _run_dead_code_analysis(self, files: list[str], result: TechnicalDebt) -> None:
        """Run dead code analysis on files."""
        dead_code = self.dead_code_analyzer.find_dead_code(files)
        result.dead_code.extend(dead_code)

        # Add dead code smells
        for code_path in dead_code:
            result.smells.append(
                CodeSmell(
                    smell_type=CodeSmellType.DEAD_CODE,
                    severity=Severity.LOW,
                    location=Location(file_path=code_path, line_start=0, line_end=0),
                    name="Dead Code",
                    description=f"Potentially dead code detected: {code_path}",
                    effort_hours=1.0,
                )
            )

    def _run_deprecation_analysis(self, files: list[str], result: TechnicalDebt) -> None:
        """Run deprecation analysis on files."""
        deprecations = self.deprecation_tracker.track_deprecations(files)
        result.deprecations.extend(deprecations)

    def get_supported_languages(self) -> list[str]:
        """Get list of supported programming languages."""
        return ["python", "javascript", "typescript", "java", "cpp", "csharp", "go", "rust", "ruby"]

    def get_analysis_options(self) -> dict:
        """Get available analysis options."""
        return {
            "analyze_complexity": self.config.analyze_complexity,
            "analyze_duplication": self.config.analyze_duplication,
            "analyze_dependencies": self.config.analyze_dependencies,
            "analyze_dead_code": self.config.analyze_dead_code,
            "analyze_deprecations": self.config.analyze_deprecations,
            "generate_suggestions": self.config.generate_suggestions,
            "generate_sprint_impact": self.config.generate_sprint_impact,
        }
