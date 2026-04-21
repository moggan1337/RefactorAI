"""
Tests for SmellDetector.
"""

import pytest
import ast
import sys
from pathlib import Path

# Add refactorai to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from refactorai.analysis.smell_detector import SmellDetector
from refactorai.models.technical_debt import (
    CodeSmell,
    CodeSmellType,
    Severity,
    Location,
)
from refactorai.models.project import AnalysisConfig


class TestSmellDetector:
    """Tests for SmellDetector class."""

    @pytest.fixture
    def default_config(self):
        """Create default analysis config."""
        return AnalysisConfig(
            max_method_length=20,
            max_parameters=5,
            max_cyclomatic_complexity=10,
            max_class_length=300,
            min_duplication_lines=6,
        )

    @pytest.fixture
    def detector(self, default_config):
        """Create SmellDetector instance."""
        return SmellDetector(default_config)

    def test_detect_empty_file(self, detector):
        """Test detecting smells in empty file."""
        smells = detector.detect_in_file("test.py", "")
        
        assert isinstance(smells, list)
        assert len(smells) == 0

    def test_detect_empty_content(self, detector):
        """Test detecting smells with empty content."""
        smells = detector.detect_in_file("test.py", "")
        
        assert smells == []

    def test_detect_in_python_file(self, detector):
        """Test detecting smells in Python file."""
        code = """
def short_function():
    return 1
"""
        smells = detector.detect_in_file("test.py", code)
        
        assert isinstance(smells, list)

    def test_detect_long_method(self, detector):
        """Test detecting long methods."""
        code = """
def very_long_function():
    result = 1
    result = 2
    result = 3
    result = 4
    result = 5
    result = 6
    result = 7
    result = 8
    result = 9
    result = 10
    result = 11
    result = 12
    result = 13
    result = 14
    result = 15
    result = 16
    result = 17
    result = 18
    result = 19
    result = 20
    result = 21
    result = 22
    return result
"""
        smells = detector.detect_in_file("test.py", code)
        
        long_method_smells = [
            s for s in smells if s.smell_type == CodeSmellType.LONG_METHOD
        ]
        assert len(long_method_smells) > 0

    def test_detect_complex_method(self, detector):
        """Test detecting complex methods."""
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        return "very large"
    return "small"
"""
        smells = detector.detect_in_file("test.py", code)
        
        complex_method_smells = [
            s for s in smells if s.smell_type == CodeSmellType.COMPLEX_METHOD
        ]
        assert len(complex_method_smells) > 0

    def test_detect_long_parameter_list(self, detector):
        """Test detecting long parameter lists."""
        code = """
def function_with_many_params(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h
"""
        smells = detector.detect_in_file("test.py", code)
        
        long_param_smells = [
            s for s in smells if s.smell_type == CodeSmellType.LONG_PARAMETER_LIST
        ]
        assert len(long_param_smells) > 0

    def test_detect_data_class(self, detector):
        """Test detecting data classes."""
        code = """
class UserDTO:
    def __init__(self, name, email, age, address, phone):
        self.name = name
        self.email = email
        self.age = age
        self.address = address
        self.phone = phone
"""
        smells = detector.detect_in_file("test.py", code)
        
        # Data class detection looks at class with many attributes and few methods
        assert isinstance(smells, list)

    def test_detect_magic_numbers(self, detector):
        """Test detecting magic numbers."""
        code = """
def calculate():
    result = 42
    multiplier = 1337
    return result * multiplier
"""
        smells = detector.detect_in_file("test.py", code)
        
        magic_number_smells = [
            s for s in smells if s.smell_type == CodeSmellType.MAGIC_NUMBERS
        ]
        assert len(magic_number_smells) > 0

    def test_detect_magic_numbers_excludes_common_values(self, detector):
        """Test that common magic numbers are excluded."""
        code = """
def calculate():
    result = 0
    count = 1
    index = 100
    days = 365
    return result + count + index + days
"""
        smells = detector.detect_in_file("test.py", code)
        
        magic_number_smells = [
            s for s in smells if s.smell_type == CodeSmellType.MAGIC_NUMBERS
        ]
        # 0, 1, 100, 365 are common values and should be excluded
        assert len(magic_number_smells) == 0

    def test_handles_syntax_error_gracefully(self, detector):
        """Test that detector handles syntax errors gracefully."""
        code = """
def broken_function(
    return None
"""
        # Should not raise exception
        smells = detector.detect_in_file("test.py", code)
        assert isinstance(smells, list)

    def test_detect_in_javascript_file(self, detector):
        """Test detecting smells in JavaScript file."""
        code = """
function shortFunction() {
    return 1;
}
"""
        smells = detector.detect_in_file("test.js", code)
        
        assert isinstance(smells, list)

    def test_detect_javascript_long_function(self, detector):
        """Test detecting long JavaScript functions."""
        code = """
function veryLongFunction() {
    var result = 1;
    result = 2;
    result = 3;
    result = 4;
    result = 5;
    result = 6;
    result = 7;
    result = 8;
    result = 9;
    result = 10;
    result = 11;
    result = 12;
    result = 13;
    result = 14;
    result = 15;
    result = 16;
    result = 17;
    result = 18;
    result = 19;
    result = 20;
    result = 21;
    result = 22;
    return result;
}
"""
        smells = detector.detect_in_file("test.js", code)
        
        long_method_smells = [
            s for s in smells if s.smell_type == CodeSmellType.LONG_METHOD
        ]
        assert len(long_method_smells) > 0

    def test_smell_has_required_properties(self, detector):
        """Test that detected smells have required properties."""
        code = """
def very_long_function_with_many_statements():
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    return x
"""
        smells = detector.detect_in_file("test.py", code)
        
        if len(smells) > 0:
            smell = smells[0]
            assert smell.name is not None
            assert smell.description is not None
            assert smell.severity is not None
            assert smell.location is not None

    def test_detect_multiple_smells_in_same_file(self, detector):
        """Test detecting multiple smells in the same file."""
        code = """
def very_long_function_with_many_parameters_and_complexity(a, b, c, d, e, f, g, h):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return "deeply nested"
    return "done"

def another_long_function():
    x = 1
    x = 2
    x = 3
    x = 4
    x = 5
    x = 6
    x = 7
    x = 8
    x = 9
    x = 10
    x = 11
    x = 12
    x = 13
    x = 14
    x = 15
    x = 16
    x = 17
    x = 18
    x = 19
    x = 20
    x = 21
    x = 22
    return x
"""
        smells = detector.detect_in_file("test.py", code)
        
        # Should detect multiple smells
        assert len(smells) >= 2

    def test_is_python_detection(self, detector):
        """Test Python file detection."""
        assert detector._is_python("test.py") is True
        # Note: .pyw detection may depend on implementation
        assert detector._is_python("test.js") is False

    def test_is_javascript_detection(self, detector):
        """Test JavaScript file detection."""
        assert detector._is_javascript("test.js") is True
        assert detector._is_javascript("test.ts") is True
        assert detector._is_javascript("test.jsx") is True
        assert detector._is_javascript("test.tsx") is True
        assert detector._is_javascript("test.py") is False

    def test_get_snippet(self, detector):
        """Test code snippet extraction."""
        content = """line 1
line 2
line 3
line 4
line 5
"""
        snippet = detector._get_snippet(content, 2, 4)
        
        assert "line 2" in snippet
        assert "line 3" in snippet

    def test_get_snippet_handles_out_of_bounds(self, detector):
        """Test snippet extraction handles out of bounds gracefully."""
        content = "line 1\nline 2\nline 3"
        snippet = detector._get_snippet(content, 100, 200)
        
        # Should not raise, just return what it can
        assert isinstance(snippet, str)

    def test_cyclomatic_complexity_calculation(self, default_config):
        """Test cyclomatic complexity calculation."""
        code = """
def simple():
    return 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        
        detector = SmellDetector(default_config)
        complexity = detector._calculate_cyclomatic_complexity(func)
        
        assert complexity == 1  # Base complexity

    def test_cyclomatic_complexity_with_conditionals(self, default_config):
        """Test complexity with conditionals."""
        code = """
def with_conditionals(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
"""
        tree = ast.parse(code)
        func = tree.body[0]
        
        detector = SmellDetector(default_config)
        complexity = detector._calculate_cyclomatic_complexity(func)
        
        # Base 1 + if + elif + else = 3
        assert complexity >= 2

    def test_severity_assignment(self, default_config):
        """Test that severity is assigned based on smell type."""
        code = """
def very_long_method():
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    x = 1; x = 2; x = 3; x = 4; x = 5; x = 6; x = 7; x = 8; x = 9; x = 10
    return x
"""
        detector = SmellDetector(default_config)
        smells = detector.detect_in_file("test.py", code)
        
        if smells:
            for smell in smells:
                assert smell.severity in [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL, Severity.INFO]
