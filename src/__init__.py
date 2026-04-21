"""
RefactorAI - AI-Powered Technical Debt Analyzer and Refactoring Assistant

A comprehensive tool for identifying, quantifying, and prioritizing technical debt
in software projects. Features include code smell detection, complexity analysis,
duplication finding, circular dependency detection, and AI-powered refactoring suggestions.
"""

__version__ = "1.0.0"
__author__ = "RefactorAI Team"

from refactorai.models.technical_debt import TechnicalDebt, CodeSmell, RefactoringSuggestion
from refactorai.models.project import ProjectAnalysis
from refactorai.analysis.analyzer import TechDebtAnalyzer

__all__ = [
    "TechnicalDebt",
    "CodeSmell",
    "RefactoringSuggestion",
    "ProjectAnalysis",
    "TechDebtAnalyzer",
]
