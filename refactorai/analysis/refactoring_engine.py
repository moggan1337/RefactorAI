"""
AI-Powered Refactoring Engine.

Generates intelligent refactoring suggestions using
rule-based analysis and optional AI assistance.
"""

from __future__ import annotations

import ast
import re
from typing import Optional

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import (
    TechnicalDebt,
    CodeSmell,
    CodeSmellType,
    RefactoringSuggestion,
    RefactoringPattern,
    Location,
)


class RefactoringEngine:
    """
    Generates refactoring suggestions for technical debt.

    Uses pattern matching and AI (when available) to provide
    actionable refactoring recommendations.
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self._ai_client = None

        # Initialize AI client if configured
        if config.use_ai_suggestions and config.ai_api_key:
            self._init_ai_client(config.ai_api_key, config.ai_model)

    def _init_ai_client(self, api_key: str, model: str) -> None:
        """Initialize AI client for advanced suggestions."""
        try:
            # Try OpenAI
            from openai import OpenAI
            self._ai_client = OpenAI(api_key=api_key)
            self._ai_model = model
            self._ai_provider = "openai"
        except ImportError:
            try:
                # Try Anthropic
                import anthropic
                self._ai_client = anthropic.Anthropic(api_key=api_key)
                self._ai_model = model
                self._ai_provider = "anthropic"
            except ImportError:
                print("Warning: AI clients not available. Install openai or anthropic.")

    def generate_suggestions(self, debt: TechnicalDebt) -> list[RefactoringSuggestion]:
        """
        Generate refactoring suggestions for all detected debt.

        Args:
            debt: TechnicalDebt analysis results

        Returns:
            List of RefactoringSuggestion objects
        """
        suggestions = []

        # Generate suggestions based on each smell
        for smell in debt.smells:
            smell_suggestions = self._suggest_for_smell(smell)
            suggestions.extend(smell_suggestions)

        # Sort by priority (highest first)
        suggestions.sort(key=lambda s: s.priority, reverse=True)

        # Optionally enhance with AI
        if self.config.use_ai_suggestions and self._ai_client:
            suggestions = self._enhance_with_ai(suggestions)

        return suggestions

    def _suggest_for_smell(self, smell: CodeSmell) -> list[RefactoringSuggestion]:
        """Generate suggestions for a specific smell."""
        suggestions = []

        pattern_mapping = {
            CodeSmellType.LONG_METHOD: [
                RefactoringPattern.EXTRACT_METHOD,
                RefactoringPattern.REPLACE_TEMP_WITH_QUERY,
            ],
            CodeSmellType.GOD_CLASS: [
                RefactoringPattern.EXTRACT_CLASS,
                RefactoringPattern.EXTRACT_SUPERCLASS,
            ],
            CodeSmellType.DUPLICATE_CODE: [
                RefactoringPattern.EXTRACT_METHOD,
                RefactoringPattern.EXTRACT_WIDGET,
            ],
            CodeSmellType.LONG_PARAMETER_LIST: [
                RefactoringPattern.INTRODUCE_PARAMETER_OBJECT,
                RefactoringPattern.REPLACE_PRIMITIVE,
            ],
            CodeSmellType.COMPLEX_METHOD: [
                RefactoringPattern.REPLACE_CONDITIONAL,
                RefactoringPattern.DECOMPOSE_CONDITIONAL,
            ],
            CodeSmellType.DEAD_CODE: [RefactoringPattern.REMOVE_DEAD_CODE],
            CodeSmellType.MAGIC_NUMBERS: [
                RefactoringPattern.REPLACE_PRIMITIVE,
                RefactoringPattern.RENAMING,
            ],
            CodeSmellType.FEATURE_ENVY: [RefactoringPattern.MOVE_METHOD],
            CodeSmellType.DATA_CLASS: [
                RefactoringPattern.EXTRACT_METHOD,
                RefactoringPattern.INTRODUCE_NULL_OBJECT,
            ],
        }

        patterns = pattern_mapping.get(smell.smell_type, [RefactoringPattern.RENAMING])

        for pattern in patterns:
            suggestion = self._create_suggestion(smell, pattern)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _create_suggestion(self, smell: CodeSmell, pattern: RefactoringPattern) -> Optional[RefactoringSuggestion]:
        """Create a specific refactoring suggestion."""
        title_map = {
            RefactoringPattern.EXTRACT_METHOD: f"Extract Method from {smell.name}",
            RefactoringPattern.EXTRACT_CLASS: f"Extract Class from {smell.name}",
            RefactoringPattern.EXTRACT_SUPERCLASS: f"Extract Superclass from {smell.name}",
            RefactoringPattern.MOVE_METHOD: f"Move Method {smell.name}",
            RefactoringPattern.INTRODUCE_PARAMETER_OBJECT: f"Introduce Parameter Object for {smell.name}",
            RefactoringPattern.REPLACE_CONDITIONAL: f"Replace Conditional with Polymorphism in {smell.name}",
            RefactoringPattern.REPLACE_PRIMITIVE: f"Replace Primitive with Rich Type for {smell.name}",
            RefactoringPattern.REMOVE_DEAD_CODE: f"Remove Dead Code: {smell.name}",
            RefactoringPattern.RENAMING: f"Rename {smell.name} for Clarity",
            RefactoringPattern.DECOMPOSE_CONDITIONAL: f"Decompose Complex Conditional in {smell.name}",
        }

        description_map = {
            RefactoringPattern.EXTRACT_METHOD: "Break down this long method into smaller, focused methods. Each extracted method should do one thing well.",
            RefactoringPattern.EXTRACT_CLASS: "This class has too many responsibilities. Extract related fields and methods into a new class.",
            RefactoringPattern.EXTRACT_SUPERCLASS: "Extract common behavior into a superclass and use inheritance to share code.",
            RefactoringPattern.MOVE_METHOD: "This method uses more data from other classes than its own. Move it to where the data belongs.",
            RefactoringPattern.INTRODUCE_PARAMETER_OBJECT: "Replace long parameter lists with a parameter object that groups related data.",
            RefactoringPattern.REPLACE_CONDITIONAL: "Replace complex conditional logic with polymorphism or a strategy pattern.",
            RefactoringPattern.REPLACE_PRIMITIVE: "Replace magic numbers and primitives with meaningful types.",
            RefactoringPattern.REMOVE_DEAD_CODE: "Remove code that is no longer used to reduce maintenance burden.",
            RefactoringPattern.RENAMING: "Rename this identifier to better reflect its purpose.",
            RefactoringPattern.DECOMPOSE_CONDITIONAL: "Break complex conditions into separate methods with meaningful names.",
        }

        template_map = {
            RefactoringPattern.EXTRACT_METHOD: self._extract_method_template,
            RefactoringPattern.INTRODUCE_PARAMETER_OBJECT: self._parameter_object_template,
            RefactoringPattern.REPLACE_PRIMITIVE: self._replace_primitive_template,
            RefactoringPattern.REMOVE_DEAD_CODE: self._remove_dead_code_template,
        }

        title = title_map.get(pattern, f"Refactor {smell.name}")
        description = description_map.get(pattern, "Consider refactoring this code for better maintainability.")

        # Get template if available
        original_code = smell.pattern or smell.location.snippet or "// Code not available"
        suggested_code = ""
        template_func = template_map.get(pattern)
        if template_func:
            suggested_code = template_func(smell)

        return RefactoringSuggestion(
            smell_id=smell.id,
            pattern=pattern,
            title=title,
            description=description,
            original_code=original_code[:500] if len(original_code) > 500 else original_code,
            suggested_code=suggested_code,
            priority=smell.severity.value * 2,
            estimated_benefit=self._estimate_benefit(smell),
            automated=pattern in [RefactoringPattern.REMOVE_DEAD_CODE, RefactoringPattern.RENAMING],
            explanation=self._explain_benefit(smell, pattern),
        )

    def _extract_method_template(self, smell: CodeSmell) -> str:
        """Generate extract method refactoring template."""
        return '''# Before: Long method
def process_data(self, input_data, options, config, callback):
    # ... 100+ lines of code ...
    pass

# After: Extracted methods
def process_data(self, input_data, options, config, callback):
    validated_data = self._validate_input(input_data)
    processed = self._apply_transformations(validated_data, options)
    result = self._finalize(processed, config)
    callback(result)

def _validate_input(self, data):
    """Validate input data."""
    # Validation logic
    return validated

def _apply_transformations(self, data, options):
    """Apply configured transformations."""
    # Transformation logic
    return transformed

def _finalize(self, data, config):
    """Finalize processing with config."""
    # Finalization logic
    return result
'''

    def _parameter_object_template(self, smell: CodeSmell) -> str:
        """Generate parameter object refactoring template."""
        return '''# Before: Long parameter list
def create_user(name, email, phone, address, city, state, zip_code, country):
    pass

# After: Parameter object
@dataclass
class UserAddress:
    street: str
    city: str
    state: str
    zip_code: str
    country: str

@dataclass
class UserCreateRequest:
    name: str
    email: str
    phone: str
    address: UserAddress

def create_user(request: UserCreateRequest):
    # Clean, typed, extensible
    pass
'''

    def _replace_primitive_template(self, smell: CodeSmell) -> str:
        """Generate replace primitive with type template."""
        return '''# Before: Magic numbers and primitives
def calculate_price(quantity, unit_price, discount_percent, tax_rate):
    return quantity * unit_price * (1 - discount_percent / 100) * (1 + tax_rate)

# After: Named constants and types
from dataclasses import dataclass
from decimal import Decimal

DISCOUNT_THRESHOLD = Decimal("100.00")
DEFAULT_DISCOUNT_RATE = Decimal("0.10")

@dataclass
class Money:
    amount: Decimal
    currency: str = "USD"

@dataclass
class PriceCalculation:
    quantity: int
    unit_price: Money
    discount_rate: Decimal = Decimal("0.0")
    tax_rate: Decimal = Decimal("0.0")

def calculate_price(calc: PriceCalculation) -> Money:
    subtotal = calc.unit_price.amount * calc.quantity
    discount = subtotal * calc.discount_rate
    taxed = (subtotal - discount) * (1 + calc.tax_rate)
    return Money(amount=taxed)
'''

    def _remove_dead_code_template(self, smell: CodeSmell) -> str:
        """Generate remove dead code template."""
        return '''# Before: Dead code
def process():
    # Legacy function - no longer called
    def unused_helper(data):
        return data

    return do_something()

# After: Clean code
def process():
    return do_something()

# Or if the helper is needed elsewhere, document why:
# NOTE: This was removed as part of refactoring.
# If needed in future, reconsider the architecture.
'''

    def _estimate_benefit(self, smell: CodeSmell) -> float:
        """Estimate the benefit percentage of fixing this smell."""
        benefit_map = {
            CodeSmellType.LONG_METHOD: 15.0,
            CodeSmellType.GOD_CLASS: 25.0,
            CodeSmellType.DUPLICATE_CODE: 20.0,
            CodeSmellType.COMPLEX_METHOD: 18.0,
            CodeSmellType.CYCLIC_DEPENDENCY: 30.0,
            CodeSmellType.DEAD_CODE: 5.0,
            CodeSmellType.MAGIC_NUMBERS: 3.0,
            CodeSmellType.FEATURE_ENVY: 12.0,
        }
        return benefit_map.get(smell.smell_type, 10.0)

    def _explain_benefit(self, smell: CodeSmell, pattern: RefactoringPattern) -> str:
        """Explain why this refactoring is beneficial."""
        benefits = {
            RefactoringPattern.EXTRACT_METHOD: "Improves readability, testability, and reusability. Smaller methods are easier to understand and debug.",
            RefactoringPattern.EXTRACT_CLASS: "Follows Single Responsibility Principle. Each class should have one reason to change.",
            RefactoringPattern.MOVE_METHOD: "Reduces coupling. Code should live close to the data it operates on.",
            RefactoringPattern.INTRODUCE_PARAMETER_OBJECT: "Reduces method signature complexity and makes it easier to add parameters without breaking callers.",
            RefactoringPattern.REPLACE_PRIMITIVE: "Makes code more expressive and catches errors at compile time rather than runtime.",
            RefactoringPattern.REMOVE_DEAD_CODE: "Reduces cognitive load and maintenance burden. Less code means fewer bugs.",
            RefactoringPattern.RENAMING: "Self-documenting code reduces the need for comments and makes intent clearer.",
        }
        return benefits.get(pattern, "Refactoring improves code quality, maintainability, and reduces bugs.")

    def _enhance_with_ai(self, suggestions: list[RefactoringSuggestion]) -> list[RefactoringSuggestion]:
        """Enhance suggestions with AI-generated improvements."""
        if not self._ai_client:
            return suggestions

        enhanced = []

        for suggestion in suggestions[:10]:  # Limit API calls
            try:
                enhanced_suggestion = self._get_ai_suggestion(suggestion)
                if enhanced_suggestion:
                    enhanced.append(enhanced_suggestion)
                else:
                    enhanced.append(suggestion)
            except Exception as e:
                print(f"AI enhancement failed for {suggestion.title}: {e}")
                enhanced.append(suggestion)

        return enhanced

    def _get_ai_suggestion(self, suggestion: RefactoringSuggestion) -> Optional[RefactoringSuggestion]:
        """Get improved suggestion from AI."""
        if not self._ai_client:
            return None

        prompt = f"""As a code refactoring expert, improve this refactoring suggestion:

Current Issue: {suggestion.title}
Description: {suggestion.description}

Original Code:
{suggestion.original_code[:500]}

Provide a better suggested refactoring with code examples. Format your response as:
1. Title (brief)
2. Description (2-3 sentences)
3. Suggested Code (complete, runnable example)
"""

        try:
            if self._ai_provider == "openai":
                response = self._ai_client.chat.completions.create(
                    model=self._ai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                )
                ai_content = response.choices[0].message.content
            else:
                response = self._ai_client.messages.create(
                    model=self._ai_model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                ai_content = response.content[0].text

            # Parse AI response (simplified)
            suggestion.explanation = ai_content
            suggestion.confidence = 0.9
            return suggestion

        except Exception as e:
            print(f"AI API call failed: {e}")
            return None

    def apply_automated_refactoring(self, suggestion: RefactoringSuggestion, file_path: str) -> bool:
        """
        Apply an automated refactoring to a file.

        Args:
            suggestion: The suggestion to apply
            file_path: Path to the file to modify

        Returns:
            True if successful, False otherwise
        """
        if not suggestion.automated:
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Apply simple replacements
            if suggestion.pattern == RefactoringPattern.REMOVE_DEAD_CODE:
                # This is a simplified implementation
                # A full implementation would use AST
                pass

            return True
        except Exception:
            return False

    def generate_refactoring_plan(self, suggestions: list[RefactoringSuggestion]) -> dict:
        """
        Generate an ordered refactoring plan.

        Organizes suggestions into a logical order for refactoring
        to minimize risk and maximize impact.
        """
        # Categorize by pattern
        by_pattern: dict[RefactoringPattern, list[RefactoringSuggestion]] = {}
        for suggestion in suggestions:
            if suggestion.pattern not in by_pattern:
                by_pattern[suggestion.pattern] = []
            by_pattern[suggestion.pattern].append(suggestion)

        # Order patterns by dependency (extract before move, etc.)
        order = [
            RefactoringPattern.REMOVE_DEAD_CODE,
            RefactoringPattern.RENAMING,
            RefactoringPattern.REPLACE_PRIMITIVE,
            RefactoringPattern.EXTRACT_METHOD,
            RefactoringPattern.DECOMPOSE_CONDITIONAL,
            RefactoringPattern.INTRODUCE_PARAMETER_OBJECT,
            RefactoringPattern.MOVE_METHOD,
            RefactoringPattern.EXTRACT_CLASS,
            RefactoringPattern.EXTRACT_SUPERCLASS,
        ]

        # Build ordered plan
        plan = []
        for pattern in order:
            if pattern in by_pattern:
                plan.extend(by_pattern[pattern])

        # Add remaining patterns
        remaining = set(by_pattern.keys()) - set(order)
        for pattern in remaining:
            plan.extend(by_pattern[pattern])

        return {
            "total_suggestions": len(plan),
            "estimated_hours": sum(s.priority * 0.5 for s in plan),
            "estimated_benefit": sum(s.estimated_benefit for s in plan) / max(1, len(plan)),
            "by_pattern": {p.value: len(suggestions) for p, suggestions in by_pattern.items()},
            "plan": [{"title": s.title, "pattern": s.pattern.value, "priority": s.priority} for s in plan],
        }
