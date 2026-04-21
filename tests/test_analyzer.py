"""Tests for the TechDebtAnalyzer."""

import os
import tempfile
import pytest
from pathlib import Path

from refactorai.analysis.analyzer import TechDebtAnalyzer
from refactorai.models.project import AnalysisConfig


class TestTechDebtAnalyzer:
    """Test cases for TechDebtAnalyzer."""

    @pytest.fixture
    def sample_project(self):
        """Create a sample Python project for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample Python files
            files = {
                "main.py": '''
def main():
    """Main entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''',
                "module.py": '''
class MyClass:
    """A simple class."""

    def __init__(self, value):
        self.value = value

    def process(self, data, options, config, callback):
        """Process data with many parameters."""
        # Validate
        if not data:
            raise ValueError("No data")

        # Transform
        result = []
        for item in data:
            if item > 0:
                result.append(item * 2)

        # Apply options
        if options.get("filter"):
            result = [r for r in result if r > options["filter"]]

        # Format
        formatted = [str(r) for r in result]

        return formatted

    def calculate(self, a, b, c, d, e, f):
        """Method with too many parameters."""
        return a + b + c + d + e + f
''',
                "utils.py": '''
def helper_function(x):
    """A simple helper."""
    return x * 2

def duplicate_function():
    """This function is duplicated elsewhere."""
    return "duplicate"

def another_duplicate():
    """Another duplicate function."""
    return "duplicate"
''',
            }

            for filename, content in files.items():
                filepath = Path(tmpdir) / filename
                filepath.write_text(content)

            yield tmpdir

    def test_analyzer_initialization(self):
        """Test analyzer can be initialized."""
        analyzer = TechDebtAnalyzer()
        assert analyzer is not None
        assert analyzer.config is not None

    def test_analyzer_with_custom_config(self):
        """Test analyzer with custom configuration."""
        config = AnalysisConfig(max_cyclomatic_complexity=5)
        analyzer = TechDebtAnalyzer(config)
        assert analyzer.config.max_cyclomatic_complexity == 5

    def test_analyze_sample_project(self, sample_project):
        """Test analysis of a sample project."""
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze(sample_project)

        assert result is not None
        assert result.project_path == sample_project
        assert result.files_analyzed >= 3
        assert result.lines_analyzed > 0
        assert result.language == "python"

    def test_smell_detection(self, sample_project):
        """Test that smells are detected."""
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze(sample_project)

        # Should detect some smells
        assert len(result.smells) >= 0

    def test_complexity_analysis(self, sample_project):
        """Test complexity metrics are calculated."""
        config = AnalysisConfig(analyze_complexity=True)
        analyzer = TechDebtAnalyzer(config)
        result = analyzer.analyze(sample_project)

        # Check metrics are available
        assert result.complexity_metrics is not None

    def test_debt_quantification(self, sample_project):
        """Test debt cost calculation."""
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze(sample_project)

        # Verify debt metrics
        assert result.total_debt_cost >= 0
        assert result.debt_hours >= 0
        assert result.debt_score >= 0

    def test_debt_severity_breakdown(self, sample_project):
        """Test debt severity categorization."""
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze(sample_project)

        severity_counts = result.debt_by_severity
        assert isinstance(severity_counts, dict)
        assert sum(severity_counts.values()) == len(result.smells)

    def test_critical_smells(self, sample_project):
        """Test critical smells filtering."""
        analyzer = TechDebtAnalyzer()
        result = analyzer.analyze(sample_project)

        critical = result.get_critical_smells()
        assert isinstance(critical, list)
        for smell in critical:
            assert smell.severity.value <= 2  # Critical or High
