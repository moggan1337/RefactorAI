"""Tests for data models."""

import pytest
from datetime import datetime

from refactorai.models.technical_debt import (
    TechnicalDebt,
    CodeSmell,
    CodeSmellType,
    Severity,
    Location,
    RefactoringSuggestion,
    RefactoringPattern,
    ComplexityMetrics,
    Duplication,
    SprintImpact,
)
from refactorai.models.project import AnalysisConfig, FileType


class TestCodeSmell:
    """Test cases for CodeSmell model."""

    def test_create_code_smell(self):
        """Test creating a code smell."""
        location = Location(file_path="test.py", line_start=10, line_end=20)
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_METHOD,
            severity=Severity.MEDIUM,
            location=location,
            name="Test Smell",
            description="A test code smell",
        )

        assert smell.smell_type == CodeSmellType.LONG_METHOD
        assert smell.severity == Severity.MEDIUM
        assert smell.name == "Test Smell"
        assert smell.category == "Implementation"

    def test_technical_debt_cost_calculation(self):
        """Test automatic debt cost calculation."""
        location = Location(file_path="test.py", line_start=1, line_end=10)
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_METHOD,
            severity=Severity.MEDIUM,
            location=location,
            name="Test",
            description="Test",
            effort_hours=10.0,
        )

        # Default rate is $150/hour
        assert smell.technical_debt_cost == 1500.0


class TestTechnicalDebt:
    """Test cases for TechnicalDebt model."""

    def test_create_technical_debt(self):
        """Test creating a technical debt object."""
        debt = TechnicalDebt(project_path="/test/project")

        assert debt.project_path == "/test/project"
        assert debt.smells == []
        assert debt.total_debt_cost == 0.0

    def test_debt_score_calculation(self):
        """Test debt score calculation."""
        debt = TechnicalDebt(project_path="/test/project")

        # Add some smells
        location = Location(file_path="test.py", line_start=1, line_end=10)
        debt.smells.append(
            CodeSmell(
                smell_type=CodeSmellType.LONG_METHOD,
                severity=Severity.CRITICAL,
                location=location,
                name="Test",
                description="Test",
            )
        )

        assert debt.debt_score > 0
        assert debt.debt_rating in ["Excellent", "Good", "Fair", "Poor", "Critical"]

    def test_debt_by_severity(self):
        """Test debt categorization by severity."""
        debt = TechnicalDebt(project_path="/test/project")

        location = Location(file_path="test.py", line_start=1, line_end=10)
        debt.smells.append(
            CodeSmell(
                smell_type=CodeSmellType.LONG_METHOD,
                severity=Severity.CRITICAL,
                location=location,
                name="Critical",
                description="Critical",
            )
        )
        debt.smells.append(
            CodeSmell(
                smell_type=CodeSmellType.LONG_METHOD,
                severity=Severity.LOW,
                location=location,
                name="Low",
                description="Low",
            )
        )

        assert debt.debt_by_severity[Severity.CRITICAL] == 1
        assert debt.debt_by_severity[Severity.LOW] == 1


class TestComplexityMetrics:
    """Test cases for ComplexityMetrics."""

    def test_create_metrics(self):
        """Test creating complexity metrics."""
        metrics = ComplexityMetrics(
            cyclomatic_complexity=15,
            cognitive_complexity=10,
            lines_of_code=100,
        )

        assert metrics.cyclomatic_complexity == 15
        assert metrics.complexity_rating == "Moderate"
        assert metrics.maintainability_rating == "Good"

    def test_complexity_ratings(self):
        """Test complexity rating thresholds."""
        low = ComplexityMetrics(cyclomatic_complexity=5)
        assert low.complexity_rating == "Low"

        moderate = ComplexityMetrics(cyclomatic_complexity=15)
        assert moderate.complexity_rating == "Moderate"

        high = ComplexityMetrics(cyclomatic_complexity=25)
        assert high.complexity_rating == "High"

        very_high = ComplexityMetrics(cyclomatic_complexity=60)
        assert very_high.complexity_rating == "Very High"


class TestRefactoringSuggestion:
    """Test cases for RefactoringSuggestion."""

    def test_create_suggestion(self):
        """Test creating a refactoring suggestion."""
        suggestion = RefactoringSuggestion(
            smell_id="test123",
            pattern=RefactoringPattern.EXTRACT_METHOD,
            title="Extract Method",
            description="Extract long method into smaller parts",
            original_code="def long_method(): pass",
            suggested_code="def short_method(): pass",
        )

        assert suggestion.pattern == RefactoringPattern.EXTRACT_METHOD
        assert suggestion.priority_label == "Low"  # Default priority is 5.0

    def test_priority_label(self):
        """Test priority label calculation."""
        low_priority = RefactoringSuggestion(
            smell_id="test",
            pattern=RefactoringPattern.RENAMING,
            title="Test",
            description="Test",
            original_code="x",
            suggested_code="y",
            priority=3.0,
        )
        assert low_priority.priority_label == "Low"

        high_priority = RefactoringSuggestion(
            smell_id="test",
            pattern=RefactoringPattern.EXTRACT_METHOD,
            title="Test",
            description="Test",
            original_code="x",
            suggested_code="y",
            priority=9.0,
        )
        assert high_priority.priority_label == "Critical"


class TestSprintImpact:
    """Test cases for SprintImpact."""

    def test_create_impact(self):
        """Test creating sprint impact prediction."""
        impact = SprintImpact(
            current_velocity=20.0,
            predicted_velocity_with_debt=18.0,
            debt_remediation_cost=10000.0,
        )

        assert impact.current_velocity == 20.0
        assert impact.velocity_degradation_rate == 10.0  # 10% degradation

    def test_roi_calculation(self):
        """Test ROI calculation."""
        impact = SprintImpact(
            current_velocity=20.0,
            predicted_velocity_with_debt=15.0,
            debt_remediation_cost=10000.0,
            prioritized_fix_cost=8000.0,
            estimated_velocity_improvement=33.3,
        )

        assert impact.roi > 0


class TestAnalysisConfig:
    """Test cases for AnalysisConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = AnalysisConfig()

        assert config.analyze_complexity is True
        assert config.max_cyclomatic_complexity == 10
        assert config.max_method_length == 50

    def test_custom_config(self):
        """Test custom configuration."""
        config = AnalysisConfig(
            max_cyclomatic_complexity=5,
            max_method_length=30,
            hourly_rate=200.0,
        )

        assert config.max_cyclomatic_complexity == 5
        assert config.max_method_length == 30
        assert config.hourly_rate == 200.0

    def test_config_validation(self):
        """Test configuration validation."""
        config = AnalysisConfig(max_method_length=0)

        # Should be corrected to minimum value
        assert config.max_method_length == 1
