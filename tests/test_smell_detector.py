"""Tests for the SmellDetector."""

import pytest
from refactorai.analysis.smell_detector import SmellDetector
from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import CodeSmellType, Severity


class TestSmellDetector:
    """Test cases for SmellDetector."""

    @pytest.fixture
    def detector(self):
        """Create a smell detector instance."""
        config = AnalysisConfig(max_method_length=20, max_cyclomatic_complexity=10)
        return SmellDetector(config)

    def test_long_method_detection(self, detector):
        """Test detection of long methods."""
        code = '''
def very_long_method():
    """This is a very long method."""
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
    x = 23
    x = 24
    x = 25
    return x
'''
        smells = detector._detect_python_smells("test.py", code)
        long_methods = [s for s in smells if s.smell_type == CodeSmellType.LONG_METHOD]
        assert len(long_methods) >= 1

    def test_complex_method_detection(self, detector):
        """Test detection of complex methods."""
        code = '''
def complex_method(a, b, c, d, e):
    """This method has high cyclomatic complexity."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return True
    return False
'''
        smells = detector._detect_python_smells("test.py", code)
        complex_methods = [s for s in smells if s.smell_type == CodeSmellType.COMPLEX_METHOD]
        assert len(complex_methods) >= 1

    def test_magic_number_detection(self, detector):
        """Test detection of magic numbers."""
        code = '''
def calculate(value):
    """Calculate something with magic numbers."""
    return value * 3.14159 * 42 + 1000000
'''
        smells = detector._detect_python_smells("test.py", code)
        magic_numbers = [s for s in smells if s.smell_type == CodeSmellType.MAGIC_NUMBERS]
        assert len(magic_numbers) >= 1

    def test_no_false_positives_for_clean_code(self, detector):
        """Test that clean code doesn't trigger false positives."""
        code = '''
def simple_add(a, b):
    """Simple addition function."""
    return a + b

class SimpleClass:
    """A simple class."""

    def __init__(self):
        self.value = 0

    def get_value(self):
        """Get the value."""
        return self.value
'''
        smells = detector._detect_python_smells("test.py", code)
        # Should have minimal or no smells
        assert len(smells) <= 2

    def test_data_class_detection(self, detector):
        """Test detection of data classes."""
        code = '''
class UserData:
    """A data class with no behavior."""

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone
'''
        smells = detector._detect_python_smells("test.py", code)
        data_classes = [s for s in smells if s.smell_type == CodeSmellType.DATA_CLASS]
        assert len(data_classes) >= 1

    def test_god_class_detection(self, detector):
        """Test detection of god classes."""
        code = '''
class GodClass:
    """A class with too many methods and responsibilities."""

    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass
    def method22(self): pass
'''
        smells = detector._detect_python_smells("test.py", code)
        god_classes = [s for s in smells if s.smell_type == CodeSmellType.GOD_CLASS]
        assert len(god_classes) >= 1
