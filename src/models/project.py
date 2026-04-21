"""
Project-level analysis models.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class FileType(Enum):
    """Supported file types for analysis."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    UNKNOWN = "unknown"


@dataclass
class AnalysisConfig:
    """Configuration for technical debt analysis."""

    # Analysis options
    analyze_complexity: bool = True
    analyze_duplication: bool = True
    analyze_dependencies: bool = True
    analyze_dead_code: bool = True
    analyze_deprecations: bool = True
    generate_suggestions: bool = True
    generate_sprint_impact: bool = True

    # Thresholds
    max_method_length: int = 50
    max_function_length: int = 50
    max_class_length: int = 500
    max_cyclomatic_complexity: int = 10
    max_cognitive_complexity: int = 15
    max_parameters: int = 5
    max_nesting_depth: int = 4
    min_duplication_lines: int = 6

    # Analysis scope
    include_tests: bool = True
    include_venv: bool = False
    include_docs: bool = False
    file_types: list[FileType] = field(
        default_factory=lambda: [FileType.PYTHON]
    )

    # Output options
    output_format: str = "json"  # json, html, markdown
    output_path: Optional[str] = None
    include_snippets: bool = True

    # AI options
    use_ai_suggestions: bool = True
    ai_model: str = "gpt-4"
    ai_api_key: Optional[str] = None

    # Cost estimation
    hourly_rate: float = 150.0  # $ per hour

    def __post_init__(self):
        """Validate configuration."""
        if self.max_method_length < 1:
            self.max_method_length = 1
        if self.max_cyclomatic_complexity < 1:
            self.max_cyclomatic_complexity = 1


@dataclass
class EntityMetrics:
    """Metrics for a single code entity (function, class, etc.)."""

    name: str
    entity_type: str  # 'function', 'class', 'method'
    file_path: str
    line_start: int
    line_end: int
    lines_of_code: int
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    parameter_count: int = 0
    local_variables: int = 0
    statements: int = 0
    maintainability_index: float = 100.0


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: str
    file_type: FileType
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    entities: list[EntityMetrics] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    complexity_score: float = 0.0
    maintainability_score: float = 100.0
    smells: list[str] = field(default_factory=list)  # IDs of smells in this file

    @property
    def total_lines(self) -> int:
        """Get total lines including comments and blanks."""
        return self.lines_of_code + self.lines_of_comments + self.blank_lines

    @property
    def comment_ratio(self) -> float:
        """Get ratio of comment lines to total lines."""
        if self.total_lines == 0:
            return 0.0
        return self.lines_of_comments / self.total_lines


@dataclass
class ModuleAnalysis:
    """Analysis results for a Python module or JavaScript package."""

    name: str
    path: str
    files: list[FileAnalysis] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    total_lines: int = 0
    total_smells: int = 0
    complexity_score: float = 0.0
    maintainability_score: float = 100.0


@dataclass
class ProjectAnalysis:
    """
    Complete project analysis results.

    This is the top-level container for all analysis results.
    """

    project_path: str
    project_name: str
    config: AnalysisConfig
    modules: list[ModuleAnalysis] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    analysis_duration_seconds: float = 0.0
    analyzed_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Summary statistics
    total_smells: int = 0
    total_duplications: int = 0
    total_dependency_cycles: int = 0
    total_dead_code: int = 0
    total_deprecations: int = 0

    # Aggregated metrics
    average_complexity: float = 0.0
    average_maintainability: float = 100.0
    total_technical_debt_hours: float = 0.0
    total_technical_debt_cost: float = 0.0

    @property
    def health_score(self) -> float:
        """
        Calculate overall project health score (0-100).

        Based on maintainability, complexity, and debt metrics.
        """
        # Start with maintainability
        score = self.average_maintainability

        # Penalize for smells
        smell_penalty = min(30, self.total_smells * 0.5)
        score -= smell_penalty

        # Penalize for complexity
        if self.average_complexity > 10:
            complexity_penalty = (self.average_complexity - 10) * 2
            score -= complexity_penalty

        # Penalize for cycles and dead code
        score -= min(10, self.total_dependency_cycles * 2)
        score -= min(5, self.total_dead_code * 0.5)

        return max(0.0, min(100.0, score))

    @property
    def health_rating(self) -> str:
        """Get text rating for project health."""
        score = self.health_score
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"

    def to_summary_dict(self) -> dict:
        """Get summary dictionary for reporting."""
        return {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "analyzed_at": self.analyzed_at.isoformat(),
            "analysis_duration_seconds": self.analysis_duration_seconds,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_smells": self.total_smells,
            "total_duplications": self.total_duplications,
            "total_dependency_cycles": self.total_dependency_cycles,
            "total_dead_code": self.total_dead_code,
            "total_deprecations": self.total_deprecations,
            "total_technical_debt_hours": self.total_technical_debt_hours,
            "total_technical_debt_cost": self.total_technical_debt_cost,
            "average_complexity": self.average_complexity,
            "average_maintainability": self.average_maintainability,
            "health_score": self.health_score,
            "health_rating": self.health_rating,
        }
