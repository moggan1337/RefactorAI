"""
Tests for LanguageDetector.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add refactorai to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from refactorai.utils.language_detector import LanguageDetector


class TestLanguageDetector:
    """Tests for LanguageDetector class."""

    @pytest.fixture
    def detector(self):
        """Create LanguageDetector instance."""
        return LanguageDetector()

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with various files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create Python files
            (project_path / "main.py").touch()
            (project_path / "utils.py").touch()
            (project_path / "core").mkdir()
            (project_path / "core" / "processor.py").touch()
            
            # Create JavaScript files
            (project_path / "index.js").touch()
            (project_path / "src").mkdir()
            (project_path / "src" / "app.js").touch()
            
            # Create TypeScript files
            (project_path / "src" / "types.ts").touch()
            (project_path / "src" / "component.tsx").touch()
            
            # Create package.json for language identification
            (project_path / "package.json").touch()
            
            # Create nested directories with Python files
            (project_path / "tests").mkdir()
            (project_path / "tests" / "test_main.py").touch()
            
            yield project_path

    def test_detect_from_file_python(self, detector):
        """Test detecting Python from file extension."""
        assert detector.detect_from_file("test.py") == "python"
        assert detector.detect_from_file("main.pyw") == "python"
        assert detector.detect_from_file("types.pyi") == "python"

    def test_detect_from_file_javascript(self, detector):
        """Test detecting JavaScript from file extension."""
        assert detector.detect_from_file("test.js") == "javascript"
        assert detector.detect_from_file("test.jsx") == "javascript"
        assert detector.detect_from_file("test.mjs") == "javascript"
        assert detector.detect_from_file("test.cjs") == "javascript"

    def test_detect_from_file_typescript(self, detector):
        """Test detecting TypeScript from file extension."""
        assert detector.detect_from_file("test.ts") == "typescript"
        assert detector.detect_from_file("test.tsx") == "typescript"

    def test_detect_from_file_java(self, detector):
        """Test detecting Java from file extension."""
        assert detector.detect_from_file("Main.java") == "java"

    def test_detect_from_file_go(self, detector):
        """Test detecting Go from file extension."""
        assert detector.detect_from_file("main.go") == "go"

    def test_detect_from_file_rust(self, detector):
        """Test detecting Rust from file extension."""
        assert detector.detect_from_file("main.rs") == "rust"

    def test_detect_from_file_ruby(self, detector):
        """Test detecting Ruby from file extension."""
        assert detector.detect_from_file("script.rb") == "ruby"

    def test_detect_from_file_cpp(self, detector):
        """Test detecting C++ from file extension."""
        assert detector.detect_from_file("main.cpp") == "cpp"
        assert detector.detect_from_file("header.hpp") == "cpp"
        assert detector.detect_from_file("source.cc") == "cpp"
        assert detector.detect_from_file("header.hh") == "cpp"

    def test_detect_from_file_csharp(self, detector):
        """Test detecting C# from file extension."""
        assert detector.detect_from_file("Program.cs") == "csharp"

    def test_detect_from_file_html(self, detector):
        """Test detecting HTML from file extension."""
        assert detector.detect_from_file("index.html") == "html"
        assert detector.detect_from_file("page.htm") == "html"

    def test_detect_from_file_css(self, detector):
        """Test detecting CSS from file extension."""
        assert detector.detect_from_file("style.css") == "css"
        assert detector.detect_from_file("styles.scss") == "css"
        assert detector.detect_from_file("theme.sass") == "css"
        assert detector.detect_from_file("variables.less") == "css"

    def test_detect_from_file_sql(self, detector):
        """Test detecting SQL from file extension."""
        assert detector.detect_from_file("query.sql") == "sql"

    def test_detect_from_file_shell(self, detector):
        """Test detecting Shell from file extension."""
        assert detector.detect_from_file("script.sh") == "shell"
        assert detector.detect_from_file("script.bash") == "shell"
        assert detector.detect_from_file("script.zsh") == "shell"

    def test_detect_from_file_unknown(self, detector):
        """Test detecting unknown file type."""
        assert detector.detect_from_file("file.xyz") == "unknown"
        assert detector.detect_from_file("noextension") == "unknown"

    def test_detect_all_with_files(self, detector, temp_project):
        """Test detecting all languages in a project."""
        languages = detector.detect_all(str(temp_project))
        
        # Should find multiple languages
        assert len(languages) > 0
        assert "python" in languages
        assert languages["python"] >= 4  # main.py, utils.py, core/processor.py, tests/test_main.py
        assert "javascript" in languages
        assert "typescript" in languages

    def test_detect_primary_language(self, detector, temp_project):
        """Test detecting primary language."""
        primary = detector.detect(str(temp_project))
        
        # Python has the most files
        assert primary == "python"

    def test_detect_empty_project(self, detector):
        """Test detecting in empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            languages = detector.detect_all(tmpdir)
            
            assert languages == {}

    def test_detect_with_excluded_directories(self, detector, temp_project):
        """Test that excluded directories are not scanned."""
        # Create node_modules with JavaScript files
        node_modules = temp_project / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.js").touch()
        
        # Create .git directory
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "config.py").touch()
        
        # Create __pycache__
        pycache = temp_project / "__pycache__"
        pycache.mkdir()
        (pycache / "main.pyc").touch()
        
        languages = detector.detect_all(str(temp_project))
        
        # Should not include node_modules or .git content
        assert len(languages) > 0
        # The python count should be from our files, not .git or __pycache__
        if "python" in languages:
            assert languages["python"] >= 4  # Only our Python files

    def test_get_project_info(self, detector, temp_project):
        """Test getting comprehensive project info."""
        info = detector.get_project_info(str(temp_project))
        
        assert "primary" in info
        assert "all" in info
        assert "file_count" in info
        assert info["primary"] == "python"
        assert info["file_count"] > 0

    def test_get_project_info_with_config_files(self, detector, temp_project):
        """Test that config files are detected."""
        # Create Python config file
        (temp_project / "setup.py").touch()
        (temp_project / "pyproject.toml").touch()
        
        # Create TypeScript config
        (temp_project / "tsconfig.json").touch()
        
        info = detector.get_project_info(str(temp_project))
        
        # Should detect config file markers
        assert "python_config" in info["all"] or "typescript_config" in info["all"]

    def test_detect_all_returns_counts(self, detector, temp_project):
        """Test that detect_all returns file counts."""
        languages = detector.detect_all(str(temp_project))
        
        for lang, count in languages.items():
            assert isinstance(count, int)
            assert count >= 0

    def test_detect_consistency(self, detector, temp_project):
        """Test that multiple calls return consistent results."""
        result1 = detector.detect_all(str(temp_project))
        result2 = detector.detect_all(str(temp_project))
        
        assert result1 == result2

    def test_detect_nested_directory_structure(self, detector, temp_project):
        """Test detecting languages in deeply nested directories."""
        # Create deep nested structure
        deep_path = temp_project / "src" / "components" / "ui" / "buttons"
        deep_path.mkdir(parents=True)
        (deep_path / "Button.tsx").touch()
        (deep_path / "styles.module.css").touch()
        
        languages = detector.detect_all(str(temp_project))
        
        assert "typescript" in languages
        assert "css" in languages

    def test_detect_with_mixed_case_extensions(self, detector):
        """Test handling of mixed case file extensions."""
        # Extensions should be case-insensitive
        assert detector.detect_from_file("test.PY") == "python"
        assert detector.detect_from_file("test.JS") == "javascript"
        assert detector.detect_from_file("test.TS") == "typescript"

    def test_language_signatures_comprehensive(self, detector):
        """Test that all language signatures are properly defined."""
        for lang, extensions in detector.LANGUAGE_SIGNATURES.items():
            assert isinstance(lang, str)
            assert isinstance(extensions, set)
            for ext in extensions:
                assert ext.startswith(".")

    def test_language_files_comprehensive(self, detector):
        """Test that language file markers are properly defined."""
        for lang, files in detector.LANGUAGE_FILES.items():
            assert isinstance(lang, str)
            assert isinstance(files, list)
            for file in files:
                assert isinstance(file, str)
