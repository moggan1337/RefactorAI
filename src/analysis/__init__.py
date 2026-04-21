"""Analysis modules for technical debt detection."""

from refactorai.analysis.analyzer import TechDebtAnalyzer
from refactorai.analysis.smell_detector import SmellDetector
from refactorai.analysis.complexity_analyzer import ComplexityAnalyzer
from refactorai.analysis.duplication_finder import DuplicationFinder
from refactorai.analysis.dependency_analyzer import DependencyAnalyzer
from refactorai.analysis.dead_code_analyzer import DeadCodeAnalyzer
from refactorai.analysis.deprecation_tracker import DeprecationTracker
from refactorai.analysis.refactoring_engine import RefactoringEngine
from refactorai.analysis.sprint_impact_predictor import SprintImpactPredictor

__all__ = [
    "TechDebtAnalyzer",
    "SmellDetector",
    "ComplexityAnalyzer",
    "DuplicationFinder",
    "DependencyAnalyzer",
    "DeadCodeAnalyzer",
    "DeprecationTracker",
    "RefactoringEngine",
    "SprintImpactPredictor",
]
