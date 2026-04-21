"""
Data models for technical debt analysis results.

This module defines all the core data structures used to represent
technical debt findings, code smells, complexity metrics, and
refactoring suggestions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class CodeSmellType(Enum):
    """Enumeration of all code smell types that can be detected."""

    # Design Smells
    GOD_CLASS = "god_class"
    FEATURE_ENVY = "feature_envy"
    DATA_CLASS = "data_class"
    REFUSED_BEQUEST = "refused_bequest"
    SWISS_ARMY_KNIFE = "swiss_army_knife"
    SPRINKLE = "sprinkle"
    AMBIGUOUS_VIEWPOINT = "ambiguous_viewpoint"
    BROKEN_MODULARIZATION = "broken_modularization"
    CYCLIC_DEPENDENCY = "cyclic_dependency"
    HUB_LIKE_MODULARIZATION = "hub_like_modularization"
    INCOMPLETE_ABSTRACT_CLASS = "incomplete_abstract_class"
    MULTIPLE_NAMES = "multiple_names"
    REBEL_WUM = "rebel_wum"
    FAT_INTERFACES = "fat_interfaces"
    DEPENDENCY_CYCLE = "dependency_cycle"

    # Implementation Smells
    COMPLEX_METHOD = "complex_method"
    LONG_METHOD = "long_method"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DUPLICATE_CODE = "duplicate_code"
    DEAD_CODE = "dead_code"
    SPEculative_GENERALITY = "speculative_generality"
    PARALLEL_INHERITANCE = "parallel_inheritance"
    LAZY_CLASS = "lazy_class"
    MESSAGE_CHAIN = "message_chain"
    MIDDLE_MAN = "middle_man"
    INSIDER_TEMPORARY = "insider_temporary"
    OBSCURE_TEMPORARY = "obscure_temporary"
    VARIABLE_NAME_HINTS = "variable_name_hints"
    ADAPTER_DEPENDENCY = "adapter_dependency"
    UNNECESSARY_ABSTRACTION = "unnecessary_abstraction"
    WIDE_HIERARCHY = "wide_hierarchy"

    # Architecture Smells
    AMBIGUOUS_INTERFACE = "ambiguous_interface"
    ARDENT_PUPPET = "ardent_puppet"
    DRIVEN_BY_QUERIES = "driven_by_queries"
    EXCESSIVE_DIRECTION = "excessive_direction"
    JUNCTIONS_OVER_PROTECTED = "junctions_over_protected"
    MULTIPATH_INHERITANCE = "multipath_inheritance"
    REACHING_DEFINITION = "reaching_definition"
    SCATTERING = "scattering"
    STUFFED_INTERFACES = "stuffed_interfaces"
    TANGLED_INTERFACES = "tangled_interfaces"

    # Other
    MAGIC_NUMBERS = "magic_numbers"
    SHOTGUN_SURGERY = "shotgun_surgery"
    DIVergent_CHANGE = "divergent_change"
    ENVIRONMENT_VULNERABILITY = "environment_vulnerability"


class Severity(Enum):
    """Severity levels for code smells."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

    @property
    def label(self) -> str:
        """Human-readable label for the severity."""
        labels = {
            Severity.CRITICAL: "Critical",
            Severity.HIGH: "High",
            Severity.MEDIUM: "Medium",
            Severity.LOW: "Low",
            Severity.INFO: "Info",
        }
        return labels[self]

    @property
    def color(self) -> str:
        """Color code for display."""
        colors = {
            Severity.CRITICAL: "red",
            Severity.HIGH: "orange",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "blue",
            Severity.INFO: "gray",
        }
        return colors[self]


@dataclass
class Location:
    """Represents a location in source code."""

    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    snippet: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_start}-{self.line_end}"


@dataclass
class CodeSmell:
    """
    Represents a detected code smell in the codebase.

    Attributes:
        id: Unique identifier for the smell
        smell_type: Type of code smell from CodeSmellType enum
        severity: Severity level of the smell
        location: Where the smell is located
        name: Human-readable name of the smell
        description: Detailed description of the issue
        pattern: The problematic code pattern
        context: Surrounding context that may be relevant
        effort_hours: Estimated effort to fix (in hours)
        technical_debt_cost: Estimated cost to fix in dollars
        tags: Associated tags for categorization
        detected_at: When the smell was detected
    """

    smell_type: CodeSmellType
    severity: Severity
    location: Location
    name: str
    description: str
    pattern: Optional[str] = None
    context: Optional[str] = None
    effort_hours: float = 0.0
    technical_debt_cost: float = 0.0
    tags: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        """Calculate technical debt cost if not provided."""
        if self.technical_debt_cost == 0.0 and self.effort_hours > 0:
            # Default rate: $150/hour
            self.technical_debt_cost = self.effort_hours * 150.0

    @property
    def category(self) -> str:
        """Get the category of this smell."""
        design_smells = {
            CodeSmellType.GOD_CLASS,
            CodeSmellType.FEATURE_ENVY,
            CodeSmellType.DATA_CLASS,
            CodeSmellType.REFUSED_BEQUEST,
        }
        if self.smell_type in design_smells:
            return "Design"
        implementation_smells = {
            CodeSmellType.COMPLEX_METHOD,
            CodeSmellType.LONG_METHOD,
            CodeSmellType.LONG_PARAMETER_LIST,
            CodeSmellType.DUPLICATE_CODE,
            CodeSmellType.DEAD_CODE,
        }
        if self.smell_type in implementation_smells:
            return "Implementation"
        return "Other"


@dataclass
class ComplexityMetrics:
    """
    Complexity metrics for a code entity (function, class, module).

    Attributes:
        cyclomatic_complexity: McCabe's cyclomatic complexity
        cognitive_complexity: Cognitive complexity score
        halstead_volume: Halstead volume measure
        maintainability_index: Composite maintainability index (0-100)
        lines_of_code: Total lines of code
        lines_of_comments: Lines of comments
        parameter_count: Number of parameters
        nesting_depth: Maximum nesting depth
    """

    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    halstead_volume: float = 0.0
    maintainability_index: float = 100.0
    lines_of_code: int = 0
    lines_of_comments: int = 0
    parameter_count: int = 0
    nesting_depth: int = 0

    @property
    def complexity_rating(self) -> str:
        """Get a text rating for cyclomatic complexity."""
        if self.cyclomatic_complexity <= 10:
            return "Low"
        elif self.cyclomatic_complexity <= 20:
            return "Moderate"
        elif self.cyclomatic_complexity <= 50:
            return "High"
        else:
            return "Very High"

    @property
    def maintainability_rating(self) -> str:
        """Get a text rating for maintainability index."""
        if self.maintainability_index >= 80:
            return "Excellent"
        elif self.maintainability_index >= 60:
            return "Good"
        elif self.maintainability_index >= 40:
            return "Fair"
        else:
            return "Poor"


@dataclass
class DependencyNode:
    """Represents a node in a dependency graph."""

    name: str
    path: str
    node_type: str  # 'file', 'module', 'class', 'function'
    imports: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    is_external: bool = False


@dataclass
class DependencyGraph:
    """
    Represents the dependency graph of a codebase.

    Used for detecting circular dependencies, analyzing coupling,
    and identifying architectural issues.
    """

    nodes: dict[str, DependencyNode] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)  # (from, to)

    def add_node(self, node: DependencyNode) -> None:
        """Add a node to the dependency graph."""
        self.nodes[node.name] = node

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add a directed edge between nodes."""
        if from_node not in self.nodes:
            self.add_node(DependencyNode(name=from_node, path=from_node, node_type="unknown"))
        if to_node not in self.nodes:
            self.add_node(DependencyNode(name=to_node, path=to_node, node_type="unknown"))

        self.edges.append((from_node, to_node))
        if to_node not in self.nodes[from_node].imports:
            self.nodes[from_node].imports.append(to_node)
        if from_node not in self.nodes[to_node].imported_by:
            self.nodes[to_node].imported_by.append(from_node)

    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the dependency graph using Tarjan's algorithm."""
        import networkx as nx

        G = nx.DiGraph()
        for from_node, to_node in self.edges:
            G.add_edge(from_node, to_node)

        cycles = []
        try:
            for cycle in nx.simple_cycles(G):
                if len(cycle) > 1:
                    cycles.append(cycle)
        except Exception:
            pass

        return cycles

    def find_dead_code(self) -> list[str]:
        """Find potentially dead code (not imported by anything else)."""
        dead_code = []
        for name, node in self.nodes.items():
            if not node.imported_by and not node.is_external and node.node_type != "entry":
                # Check if it's a main module
                if not name.startswith("__"):
                    dead_code.append(name)
        return dead_code


@dataclass
class Duplication:
    """
    Represents a code duplication finding.

    Attributes:
        id: Unique identifier
        code_fragment: The duplicated code
        locations: Where the duplication occurs
        lines: Number of lines affected
        hash: Hash of the duplicated code for comparison
        refactoring_effort_hours: Estimated effort to deduplicate
    """

    code_fragment: str
    locations: list[Location]
    lines: int
    hash: str
    refactoring_effort_hours: float = 0.0

    def __post_init__(self):
        if self.refactoring_effort_hours == 0.0:
            # Rough estimate: 1 hour per 10 lines of duplication
            self.refactoring_effort_hours = max(0.5, self.lines / 10)


@dataclass
class DeprecationWarning:
    """
    Represents a detected API deprecation.

    Attributes:
        api_name: Name of the deprecated API
        deprecation_type: Type of deprecation
        alternative: Recommended alternative
        version_deprecated: Version when deprecated
        version_removal: Version when it will be removed
        severity: Impact severity
        locations: Where the deprecated API is used
    """

    api_name: str
    deprecation_type: str  # 'function', 'class', 'module', 'parameter', 'attribute'
    alternative: str
    version_deprecated: Optional[str] = None
    version_removal: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    locations: list[Location] = field(default_factory=list)


class RefactoringPattern(Enum):
    """Common refactoring patterns for addressing technical debt."""

    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    EXTRACT_SUPERCLASS = "extract_superclass"
    MOVE_METHOD = "move_method"
    MOVE_FIELD = "move_field"
    INLINE_METHOD = "inline_method"
    REPLACE_CONDITIONAL = "replace_conditional"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_TEMP_WITH_QUERY = "replace_temp_with_query"
    REPLACE_PRIMITIVE = "replace_primitive"
    INTRODUCE_NULL_OBJECT = "introduce_null_object"
    INTRODUCE_PYTHON_DICT = "introduce_python_dict"
    REPLACE_ERROR_NONE = "replace_error_none"
    EXTRACT_WIDGET = "extract_widget"
    RENAMING = "renaming"
    ADD_COMMENTS = "add_comments"
    REMOVE_DEAD_CODE = "remove_dead_code"
    CONSOLIDATE_CONDITIONAL = "consolidate_conditional"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"


@dataclass
class RefactoringSuggestion:
    """
    An AI-powered refactoring suggestion for addressing a code smell.

    Attributes:
        id: Unique identifier
        smell_id: The code smell this addresses
        pattern: Recommended refactoring pattern
        title: Brief title of the suggestion
        description: Detailed explanation
        original_code: The problematic code
        suggested_code: The refactored code
        confidence: Confidence score (0-1)
        priority: Priority score (higher = more urgent)
        estimated_benefit: Estimated improvement percentage
        risks: Potential risks of the refactoring
        automated: Whether this can be automated
        before_code: Code before refactoring
        after_code: Code after refactoring
        explanation: Why this refactoring helps
    """

    smell_id: str
    pattern: RefactoringPattern
    title: str
    description: str
    original_code: str
    suggested_code: str
    confidence: float = 0.8
    priority: float = 5.0
    estimated_benefit: float = 0.0
    risks: list[str] = field(default_factory=list)
    automated: bool = False
    before_code: Optional[str] = None
    after_code: Optional[str] = None
    explanation: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def priority_label(self) -> str:
        """Get human-readable priority."""
        if self.priority >= 8:
            return "Critical"
        elif self.priority >= 6:
            return "High"
        elif self.priority >= 4:
            return "Medium"
        else:
            return "Low"


@dataclass
class SprintImpact:
    """
    Predicted impact of technical debt on sprint velocity.

    Attributes:
        current_velocity: Current story points per sprint
        predicted_velocity_with_debt: Velocity if debt is not addressed
        debt_remediation_cost: Total cost to fix all debt
        prioritized_fix_cost: Cost to fix critical/high priority items only
        estimated_velocity_improvement: Expected velocity improvement %
        sprint_weeks_to_recover: Weeks needed to see improvement
        risk_score: Risk of delivery issues (0-10)
    """

    current_velocity: float = 0.0
    predicted_velocity_with_debt: float = 0.0
    debt_remediation_cost: float = 0.0
    prioritized_fix_cost: float = 0.0
    estimated_velocity_improvement: float = 0.0
    sprint_weeks_to_recover: int = 0
    risk_score: float = 0.0

    @property
    def velocity_degradation_rate(self) -> float:
        """Calculate percentage velocity degradation."""
        if self.current_velocity == 0:
            return 0.0
        return ((self.current_velocity - self.predicted_velocity_with_debt) / self.current_velocity) * 100

    @property
    def roi(self) -> float:
        """Calculate return on investment for debt remediation."""
        if self.debt_remediation_cost == 0:
            return 0.0
        return (self.prioritized_fix_cost * self.estimated_velocity_improvement / 100) / self.prioritized_fix_cost if self.prioritized_fix_cost > 0 else 0.0


@dataclass
class TechnicalDebt:
    """
    Comprehensive technical debt analysis result.

    This is the main output of the analyzer containing all findings.

    Attributes:
        id: Unique identifier for this analysis
        project_path: Path to the analyzed project
        analyzed_at: When the analysis was performed
        total_debt_cost: Total estimated cost to fix all debt
        debt_hours: Total hours needed to fix all debt
        smells: List of all detected code smells
        duplications: List of detected code duplications
        deprecations: List of deprecated API usages
        dependency_cycles: List of circular dependencies
        dead_code: List of potentially dead code files/functions
        complexity_metrics: Aggregated complexity metrics
        sprint_impact: Predicted sprint velocity impact
        language: Programming language detected
        files_analyzed: Number of files analyzed
        lines_analyzed: Total lines of code analyzed
    """

    project_path: str
    smells: list[CodeSmell] = field(default_factory=list)
    duplications: list[Duplication] = field(default_factory=list)
    deprecations: list[DeprecationWarning] = field(default_factory=list)
    dependency_cycles: list[list[str]] = field(default_factory=list)
    dead_code: list[str] = field(default_factory=list)
    complexity_metrics: dict[str, ComplexityMetrics] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    language: str = "python"
    files_analyzed: int = 0
    lines_analyzed: int = 0

    @property
    def total_debt_cost(self) -> float:
        """Calculate total technical debt cost."""
        smell_cost = sum(smell.technical_debt_cost for smell in self.smells)
        duplication_cost = sum(dup.refactoring_effort_hours * 150 for dup in self.duplications)
        return smell_cost + duplication_cost

    @property
    def debt_hours(self) -> float:
        """Calculate total hours needed to fix debt."""
        smell_hours = sum(smell.effort_hours for smell in self.smells)
        duplication_hours = sum(dup.refactoring_effort_hours for dup in self.duplications)
        return smell_hours + duplication_hours

    @property
    def debt_by_severity(self) -> dict[Severity, int]:
        """Count smells by severity level."""
        counts = {severity: 0 for severity in Severity}
        for smell in self.smells:
            counts[smell.severity] += 1
        return counts

    @property
    def debt_by_category(self) -> dict[str, float]:
        """Calculate debt cost by category."""
        categories: dict[str, float] = {}
        for smell in self.smells:
            category = smell.category
            if category not in categories:
                categories[category] = 0.0
            categories[category] += smell.technical_debt_cost
        return categories

    @property
    def debt_score(self) -> float:
        """
        Calculate overall debt score (0-100).

        A score of 0 means no debt, 100 means critical debt.
        """
        # Weighted by severity
        severity_weights = {
            Severity.CRITICAL: 10.0,
            Severity.HIGH: 5.0,
            Severity.MEDIUM: 2.0,
            Severity.LOW: 0.5,
            Severity.INFO: 0.1,
        }

        total_weight = sum(severity_weights[s] for s in self.debt_by_severity.values())
        # Normalize to 0-100 scale
        return min(100.0, total_weight / 10)

    @property
    def debt_rating(self) -> str:
        """Get text rating for debt score."""
        if self.debt_score <= 10:
            return "Excellent"
        elif self.debt_score <= 25:
            return "Good"
        elif self.debt_score <= 50:
            return "Fair"
        elif self.debt_score <= 75:
            return "Poor"
        else:
            return "Critical"

    def get_critical_smells(self) -> list[CodeSmell]:
        """Get all critical and high severity smells."""
        return [s for s in self.smells if s.severity in (Severity.CRITICAL, Severity.HIGH)]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "project_path": self.project_path,
            "analyzed_at": self.analyzed_at.isoformat(),
            "total_debt_cost": self.total_debt_cost,
            "debt_hours": self.debt_hours,
            "debt_score": self.debt_score,
            "debt_rating": self.debt_rating,
            "language": self.language,
            "files_analyzed": self.files_analyzed,
            "lines_analyzed": self.lines_analyzed,
            "smells_count": len(self.smells),
            "duplications_count": len(self.duplications),
            "deprecations_count": len(self.deprecations),
            "dependency_cycles_count": len(self.dependency_cycles),
            "dead_code_count": len(self.dead_code),
            "debt_by_severity": {k.label: v for k, v in self.debt_by_severity.items()},
            "debt_by_category": self.debt_by_category,
        }
