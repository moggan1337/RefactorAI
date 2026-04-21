# RefactorAI - AI-Powered Technical Debt Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version">
  <img src="https://img.shields.io/badge/Technical%20Debt-Analyzer-purple.svg" alt="Category">
</p>

RefactorAI is a comprehensive, AI-powered technical debt analyzer that helps development teams identify, quantify, and prioritize technical debt in their codebases. It combines static analysis, complexity metrics, and intelligent suggestions to provide actionable insights for improving code quality.

## 🎬 Demo
![RefactorAI Demo](demo.gif)

*Technical debt analysis with AI suggestions*

## Screenshots
| Component | Preview |
|-----------|---------|
| Debt Dashboard | ![dashboard](screenshots/debt-dashboard.png) |
| Code Smells | ![smells](screenshots/code-smells.png) |
| Refactor Preview | ![preview](screenshots/refactor-preview.png) |

## Visual Description
Debt dashboard shows technical debt metrics by component. Code smells display issues with severity and location. Refactor preview shows suggested improvements with impact estimates.

---


## Table of Contents

- [Features](#features)
- [Why Technical Debt Matters](#why-technical-debt-matters)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Understanding Technical Debt](#understanding-technical-debt)
  - [What is Technical Debt?](#what-is-technical-debt)
  - [Types of Technical Debt](#types-of-technical-debt)
  - [Measuring Technical Debt](#measuring-technical-debt)
- [Analysis Capabilities](#analysis-capabilities)
  - [Code Smell Detection](#code-smell-detection)
  - [Complexity Analysis](#complexity-analysis)
  - [Duplication Detection](#duplication-detection)
  - [Dependency Analysis](#dependency-analysis)
  - [Dead Code Detection](#dead-code-detection)
  - [Deprecation Tracking](#deprecation-tracking)
- [Refactoring Patterns](#refactoring-patterns)
  - [Extract Method](#extract-method)
  - [Extract Class](#extract-class)
  - [Move Method](#move-method)
  - [Replace Conditional](#replace-conditional)
  - [Introduce Parameter Object](#introduce-parameter-object)
  - [Remove Dead Code](#remove-dead-code)
- [Sprint Velocity Impact](#sprint-velocity-impact)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Analysis Features

- **Code Smell Detection**: Identifies over 30 types of code smells including God Classes, Long Methods, Feature Envy, and more
- **Complexity Analysis**: Calculates cyclomatic complexity, cognitive complexity, and maintainability indices
- **Duplication Finder**: Detects duplicate and near-duplicate code blocks across the codebase
- **Circular Dependency Detection**: Maps module dependencies and identifies circular references
- **Dead Code Elimination**: Finds unused functions, classes, variables, and imports
- **API Deprecation Tracker**: Monitors usage of deprecated APIs and suggests migrations

### Intelligence Features

- **AI-Powered Suggestions**: Uses GPT-4/Claude to generate intelligent refactoring recommendations
- **Tech Debt Quantification**: Translates code quality issues into time and monetary costs
- **Sprint Velocity Prediction**: Estimates the impact of technical debt on team velocity
- **Priority Scoring**: Ranks issues by severity, effort, and business impact

### Output Formats

- **Rich Console Output**: Color-coded terminal output with tables and panels
- **JSON Export**: Machine-readable output for integration with other tools
- **Markdown Reports**: Human-readable documentation format
- **HTML Dashboard**: Visual HTML reports with charts and interactive elements
- **REST API**: FastAPI-based API for programmatic access

---

## Why Technical Debt Matters

Technical debt is a metaphorical representation of the future cost of rework caused by choosing an easy solution now instead of a better approach that would take longer. Like financial debt, technical debt accumulates "interest" over time, making changes increasingly difficult and expensive.

### The Impact of Technical Debt

| Impact Area | Short-term Effect | Long-term Effect |
|-------------|-------------------|------------------|
| **Velocity** | Minor slowdown | 50%+ productivity loss |
| **Quality** | Acceptable bugs | System failures, security issues |
| **Morale** | Mild frustration | Developer burnout, turnover |
| **Business** | Delayed features | Lost competitive advantage |
| **Technical** | Simple fixes | Architectural rot |

### The Debt Snowball Effect

As technical debt accumulates, teams experience:

1. **Slower Feature Delivery**: Each feature takes longer due to navigating complex, debt-laden code
2. **Increased Bugs**: Debt leads to more defects and harder debugging
3. **Reduced Refactoring**: Fear of breaking things prevents necessary improvements
4. **Knowledge Loss**: Original reasoning behind decisions is forgotten
5. **Technical Paralysis**: The codebase becomes too fragile for significant changes

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or poetry package manager

### Using pip

```bash
pip install refactorai
```

### Using poetry

```bash
poetry add refactorai
```

### From Source

```bash
git clone https://github.com/moggan1337/RefactorAI.git
cd RefactorAI
pip install -e .
```

### Optional Dependencies

For full functionality including AI suggestions:

```bash
pip install refactorai[all]
```

---

## Quick Start

### CLI Basic Usage

```bash
# Analyze a project
refactorai analyze ./my-project

# Generate HTML report
refactorai analyze ./my-project --output html -f report.html

# Quick lint a single file
refactorai lint ./my-project/src/module.py

# Generate visualizations
refactorai visualize ./my-project

# Sprint velocity impact analysis
refactorai sprint ./my-project
```

### Python API

```python
from refactorai import TechDebtAnalyzer
from refactorai.models.project import AnalysisConfig

# Configure analysis
config = AnalysisConfig(
    max_cyclomatic_complexity=10,
    max_method_length=50,
    include_tests=False,
)

# Analyze project
analyzer = TechDebtAnalyzer(config)
result, suggestions = analyzer.analyze_with_suggestions("./my-project")

# View results
print(f"Debt Score: {result.debt_score}/100")
print(f"Total Cost: ${result.total_debt_cost:,.2f}")
print(f"Critical Issues: {len(result.get_critical_smells())}")

# Generate report
from refactorai.utils.formatters import MarkdownFormatter
report = MarkdownFormatter().format(result)
print(report)
```

---

## Understanding Technical Debt

### What is Technical Debt?

Technical debt is the implied cost of additional rework caused by choosing an easy solution now instead of a better approach that would take longer. The concept was coined by Ward Cunningham in 1992 to explain to non-technical stakeholders why software degrades over time.

### Categories of Technical Debt

#### 1. Design Debt

Design debt occurs when the overall architecture or design of a system doesn't adequately support its current or future requirements.

**Examples:**
- God Classes that handle too many responsibilities
- Missing abstraction layers
- Tight coupling between components
- Feature Envy where modules are overly dependent on each other

#### 2. Code Debt

Code debt is the result of poor coding practices at the implementation level.

**Examples:**
- Long methods with multiple responsibilities
- Duplicate code blocks
- Magic numbers and hardcoded values
- Poor variable and function naming
- Missing or inadequate comments

#### 3. Testing Debt

Testing debt represents the lack of adequate test coverage.

**Examples:**
- Missing unit tests
- Low test coverage percentages
- Tests that don't catch edge cases
- Brittle tests that break easily

#### 4. Documentation Debt

Documentation debt occurs when code lacks adequate documentation.

**Examples:**
- Missing API documentation
- Outdated documentation
- Undocumented assumptions
- Missing architecture decision records

#### 5. Infrastructure Debt

Infrastructure debt involves outdated or inadequate tooling and deployment processes.

**Examples:**
- Outdated dependencies
- Manual deployment processes
- Missing CI/CD pipelines
- Inadequate monitoring

### Measuring Technical Debt

RefactorAI uses multiple metrics to quantify technical debt:

| Metric | Description | Scale |
|--------|-------------|-------|
| **Debt Score** | Overall health indicator | 0-100 |
| **Debt Hours** | Total effort to fix | Hours |
| **Debt Cost** | Monetary value of debt | Dollars |
| **Complexity Score** | Code complexity measure | 0-∞ |
| **Maintainability Index** | Ease of maintenance | 0-100 |

---

## Analysis Capabilities

### Code Smell Detection

RefactorAI detects over 30 types of code smells organized into categories:

#### Design Smells

| Smell Type | Description | Severity Impact |
|------------|-------------|-----------------|
| God Class | Class with too many responsibilities | High |
| Feature Envy | Method that uses more data from other classes | Medium |
| Data Class | Class that only stores data without behavior | Low |
| Refused Bequest | Class that overrides parent's methods unnecessarily | Medium |
| Cyclic Dependency | Circular imports between modules | Critical |

#### Implementation Smells

| Smell Type | Description | Severity Impact |
|------------|-------------|-----------------|
| Long Method | Method exceeding length threshold | Medium-High |
| Complex Method | High cyclomatic complexity | High |
| Long Parameter List | Too many function parameters | Medium |
| Duplicate Code | Repeated code blocks | Medium |
| Dead Code | Unused functions or classes | Low |
| Magic Numbers | Unnamed constant values | Info |

### Complexity Analysis

#### Cyclomatic Complexity

Cyclomatic Complexity (CC) measures the number of linearly independent paths through a program. It's calculated as:

```
CC = E - N + 2P
```

Where:
- E = Number of edges
- N = Number of nodes
- P = Number of connected components

**Complexity Ratings:**

| Range | Rating | Interpretation |
|-------|--------|----------------|
| 1-10 | Low | Simple, well-structured code |
| 11-20 | Moderate | Moderate complexity, some risk |
| 21-50 | High | Complex, high risk of bugs |
| 51+ | Very High | Extremely complex, hard to test |

#### Cognitive Complexity

Cognitive Complexity measures how difficult code is to understand. Unlike cyclomatic complexity, it considers:

- Nesting depth
- Structural patterns
- Cognitive difficulty of constructs

#### Maintainability Index

The Maintainability Index (MI) is a composite metric:

```
MI = MAX(0, (171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)) * 0.7)
```

Where:
- V = Halstead Volume
- CC = Cyclomatic Complexity
- LOC = Lines of Code

**Maintainability Ratings:**

| Score | Rating | Interpretation |
|-------|--------|----------------|
| 80-100 | Excellent | Highly maintainable |
| 60-79 | Good | Maintainable with attention |
| 40-59 | Fair | Requires maintenance effort |
| 0-39 | Poor | Difficult to maintain |

### Duplication Detection

Duplicate code is one of the most common sources of technical debt. RefactorAI uses multiple strategies:

1. **Exact Matching**: Hash-based detection of identical code blocks
2. **Normalized Matching**: Comparison after removing whitespace and comments
3. **Structural Matching**: AST-based comparison of code structure
4. **Fuzzy Matching**: Similarity detection for near-duplicates (80%+ threshold)

**Impact of Duplications:**

- Maintenance burden: Changes must be made in multiple places
- Bug propagation: Fixes in one location may be missed elsewhere
- Cognitive load: Developers must understand multiple similar implementations
- Test complexity: More test cases needed for equivalent coverage

### Dependency Analysis

RefactorAI builds a complete dependency graph of your codebase:

#### Dependency Metrics

| Metric | Description | Ideal Value |
|--------|-------------|-------------|
| Afferent Coupling (Ca) | Number of classes depending on this | Varies by role |
| Efferent Coupling (Ce) | Number of classes this depends on | Low (< 10) |
| Instability | Ce / (Ca + Ce) | 0 for stable, 1 for unstable |
| Abstractness | Ratio of abstract classes | 0-1 balanced |

#### Circular Dependencies

Circular dependencies are particularly problematic:

```python
# module_a.py
from module_b import something

# module_b.py
from module_a import something_else
```

**Problems with Circular Dependencies:**
- Difficult to test modules independently
- Cannot easily extract modules as libraries
- Complicates understanding of dependencies
- Can cause import errors during module loading

### Dead Code Detection

Dead code includes:

- **Unused Functions**: Defined but never called
- **Unused Classes**: Never instantiated or inherited
- **Unused Variables**: Assigned but never read
- **Unreachable Code**: Code after return/raise statements
- **Unused Imports**: Imported but not referenced

### Deprecation Tracking

RefactorAI tracks usage of deprecated APIs:

```python
# Deprecated pattern
dict.iteritems()  # Use dict.items() instead

# Modern alternative
for key, value in my_dict.items():
    process(key, value)
```

---

## Refactoring Patterns

This section describes common refactoring patterns recommended by RefactorAI to address technical debt.

### Extract Method

**Problem:** A method is too long or has multiple responsibilities.

**Solution:** Break it into smaller, focused methods.

```python
# BEFORE: Long method
def process_order(order):
    # Validate order
    if not order.customer:
        raise ValueError("No customer")
    if not order.items:
        raise ValueError("No items")

    # Calculate totals
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity

    # Apply discounts
    discount = 0
    if subtotal > 100:
        discount = subtotal * 0.1

    # Calculate tax
    tax = (subtotal - discount) * 0.08

    # Final total
    total = subtotal - discount + tax

    # Save order
    order.total = total
    db.save(order)

    return order

# AFTER: Extracted methods
def process_order(order):
    validate_order(order)
    order.total = calculate_total(order)
    db.save(order)
    return order

def validate_order(order):
    if not order.customer:
        raise ValueError("No customer")
    if not order.items:
        raise ValueError("No items")

def calculate_total(order):
    subtotal = calculate_subtotal(order)
    discount = calculate_discount(subtotal)
    tax = calculate_tax(subtotal, discount)
    return subtotal - discount + tax

def calculate_subtotal(order):
    return sum(item.price * item.quantity for item in order.items)

def calculate_discount(subtotal):
    return subtotal * 0.1 if subtotal > 100 else 0

def calculate_tax(subtotal, discount):
    return (subtotal - discount) * 0.08
```

**Benefits:**
- Improved readability
- Easier testing (test each method independently)
- Reusability of extracted methods
- Better adherence to Single Responsibility Principle

### Extract Class

**Problem:** A class has too many responsibilities or too much data.

**Solution:** Create a new class and move related functionality to it.

```python
# BEFORE: God class handling multiple concerns
class Customer:
    def __init__(self, name, email, phone, street, city, state, zip_code):
        self.name = name
        self.email = email
        self.phone = phone
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code

    def validate(self):
        # Validation logic
        pass

    def format_address(self):
        # Address formatting
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

# AFTER: Separated concerns
@dataclass
class ContactInfo:
    name: str
    email: str
    phone: str

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str

    def format(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

class Customer:
    def __init__(self, contact: ContactInfo, address: Address):
        self.contact = contact
        self.address = address

    def validate(self):
        # Validation logic
        pass
```

**Benefits:**
- Clear separation of concerns
- Better reusability
- Improved testability
- Cleaner class interfaces

### Move Method

**Problem:** A method uses more data from another class than its own class.

**Solution:** Move the method to the class where most of the data lives.

```python
# BEFORE: Feature envy
class Order:
    def calculate_discount(self, customer):
        # This method uses more data from Customer than Order
        if customer.loyalty_years > 5:
            return 0.15
        elif customer.total_purchases > 1000:
            return 0.10
        elif customer.is_vip:
            return 0.05
        return 0

# AFTER: Method moved to where it belongs
class Customer:
    def calculate_discount(self):
        if self.loyalty_years > 5:
            return 0.15
        elif self.total_purchases > 1000:
            return 0.10
        elif self.is_vip:
            return 0.05
        return 0

class Order:
    def apply_discount(self, customer):
        return customer.calculate_discount()
```

### Replace Conditional

**Problem:** Complex conditional logic with multiple branches.

**Solution:** Use polymorphism or strategy pattern.

```python
# BEFORE: Complex conditionals
class Order:
    def calculate_shipping(self):
        if self.shipping_method == "standard":
            if self.total < 50:
                return 5.99
            else:
                return 0
        elif self.shipping_method == "express":
            if self.total < 100:
                return 14.99
            else:
                return 9.99
        elif self.shipping_method == "overnight":
            return 29.99

# AFTER: Strategy pattern
class ShippingStrategy:
    def calculate(self, order: Order) -> float:
        raise NotImplementedError

class StandardShipping(ShippingStrategy):
    def calculate(self, order):
        return 0 if order.total >= 50 else 5.99

class ExpressShipping(ShippingStrategy):
    def calculate(self, order):
        return 9.99 if order.total >= 100 else 14.99

class OvernightShipping(ShippingStrategy):
    def calculate(self, order):
        return 29.99

class Order:
    def __init__(self, shipping_strategy: ShippingStrategy):
        self.shipping_strategy = shipping_strategy

    def calculate_shipping(self):
        return self.shipping_strategy.calculate(self)
```

### Introduce Parameter Object

**Problem:** A method has too many parameters.

**Solution:** Group related parameters into a data class.

```python
# BEFORE: Long parameter list
def create_report(
    title,
    author,
    date_from,
    date_to,
    include_charts,
    include_tables,
    format,
    language,
    include_summary,
):
    pass

# AFTER: Parameter object
@dataclass
class ReportRequest:
    title: str
    author: str
    date_from: date
    date_to: date
    include_charts: bool = True
    include_tables: bool = True
    format: str = "pdf"
    language: str = "en"
    include_summary: bool = True

def create_report(request: ReportRequest):
    pass
```

### Remove Dead Code

**Problem:** Unused code clutters the codebase.

**Solution:** Delete it. Use version control to retrieve if needed.

```python
# BEFORE: Dead code
def process():
    def unused_helper(data):
        # No one calls this
        return data

    return do_something()

# AFTER: Clean code
def process():
    return do_something()
```

---

## Sprint Velocity Impact

RefactorAI predicts how technical debt affects sprint velocity using:

### Prediction Model

The model considers:

1. **Severity-weighted debt count**: Critical issues impact velocity more than low ones
2. **Debt density**: Ratio of debt to total code
3. **Dependency complexity**: Circular dependencies and tight coupling
4. **Historical patterns**: Based on industry data from similar projects

### Impact Estimates

| Debt Level | Velocity Impact | Recovery Time |
|------------|-----------------|--------------|
| Low (< 10%) | 0-5% | 1-2 sprints |
| Moderate (10-25%) | 5-15% | 2-4 sprints |
| High (25-50%) | 15-30% | 4-8 sprints |
| Critical (> 50%) | 30%+ | 8+ sprints |

### ROI Calculation

RefactorAI calculates the return on investment for debt remediation:

```
ROI = (Annual Velocity Benefit - Remediation Cost) / Remediation Cost × 100
```

**Example:**
- Annual velocity cost of debt: $50,000
- Remediation investment: $20,000
- ROI: 150%

---

## CLI Reference

### Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `--version` | Show version |
| `-h, --help` | Show help |

### analyze

Analyze a project for technical debt.

```bash
refactorai analyze PROJECT_PATH [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output format | console |
| `-f, --output-file` | Output file path | stdout |
| `--no-ai` | Disable AI suggestions | False |
| `--include-tests` | Include test files | False |
| `-l, --language` | Languages to analyze | python |
| `--max-complexity` | Max CC threshold | 10 |
| `--max-length` | Max method length | 50 |
| `--hourly-rate` | Rate for cost calc | $150 |

**Examples:**

```bash
# Basic analysis
refactorai analyze ./my-project

# JSON output to file
refactorai analyze ./my-project -o json -f debt.json

# Exclude tests, custom thresholds
refactorai analyze ./my-project --include-tests --max-complexity 15
```

### visualize

Generate visualizations of technical debt.

```bash
refactorai visualize PROJECT_PATH [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | ./refactorai_visuals |
| `-f, --format` | Image format | png |

### sprint

Predict sprint velocity impact.

```bash
refactorai sprint PROJECT_PATH [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-f, --format` | Output format | console |

### suggest

Generate refactoring suggestions.

```bash
refactorai suggest PROJECT_PATH [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-n, --limit` | Number of suggestions | 10 |

### lint

Quick lint a single file.

```bash
refactorai lint FILE_PATH
```

### report

Generate comprehensive HTML report.

```bash
refactorai report PROJECT_PATH
```

---

## API Reference

### REST Endpoints

#### POST /analyze

Analyze a project for technical debt.

**Request:**
```json
{
  "project_path": "/path/to/project",
  "analyze_complexity": true,
  "analyze_duplication": true,
  "max_cyclomatic_complexity": 10,
  "max_method_length": 50,
  "include_tests": false,
  "use_ai_suggestions": true
}
```

**Response:**
```json
{
  "status": "completed",
  "analysis_id": "abc123",
  "summary": {
    "debt_score": 45.2,
    "debt_rating": "Fair",
    "total_cost": 15000.00,
    "smells_count": 25
  },
  "smells": [...]
}
```

#### GET /analysis/{analysis_id}

Retrieve a previously run analysis.

#### GET /project-stats/{project_path}

Get project statistics without full analysis.

### Python SDK

```python
from refactorai import TechDebtAnalyzer
from refactorai.models.project import AnalysisConfig

# Initialize
config = AnalysisConfig(max_cyclomatic_complexity=10)
analyzer = TechDebtAnalyzer(config)

# Analyze
result = analyzer.analyze("/path/to/project")

# Access results
print(result.debt_score)
print(result.total_debt_cost)
```

---

## Configuration

### Configuration File

RefactorAI can be configured via YAML:

```yaml
# .refactorai.yaml
analysis:
  max_cyclomatic_complexity: 10
  max_method_length: 50
  max_class_length: 500
  max_nesting_depth: 4
  max_parameters: 5
  min_duplication_lines: 6

scope:
  include_tests: false
  include_venv: false
  languages:
    - python

output:
  format: console
  include_snippets: true

cost:
  hourly_rate: 150.0

ai:
  enabled: true
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
```

---

## Best Practices

### Regular Analysis

- Run RefactorAI on every pull request
- Set up CI/CD integration for automatic checks
- Track debt score over time

### Prioritization

1. **Critical Issues First**: Address security and stability issues immediately
2. **High-Impact Areas**: Focus on frequently changed code
3. **Return on Investment**: Consider the benefit vs. effort of each fix

### Prevention

- Code reviews focused on debt indicators
- Automated quality gates in CI/CD
- Documentation of architectural decisions
- Regular refactoring sprints

### Measurement

- Track debt score as a metric
- Set targets for debt reduction
- Include debt in project planning

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

### Development Setup

```bash
git clone https://github.com/moggan1337/RefactorAI.git
cd RefactorAI
pip install -e ".[dev]"
pytest
```

### Code Style

We use:
- Black for formatting
- isort for imports
- ruff for linting
- mypy for type checking

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by the RefactorAI Team
</p>
