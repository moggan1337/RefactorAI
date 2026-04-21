#!/usr/bin/env python3
"""
RefactorAI Command-Line Interface.

A comprehensive CLI for technical debt analysis and refactoring assistance.
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from refactorai import __version__
from refactorai.analysis.analyzer import TechDebtAnalyzer
from refactorai.models.project import AnalysisConfig, FileType
from refactorai.models.technical_debt import Severity
from refactorai.utils.formatters import JSONFormatter, TextFormatter, MarkdownFormatter, HTMLFormatter, ConsoleFormatter
from refactorai.utils.visualizer import DebtVisualizer

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="RefactorAI")
def cli():
    """
    RefactorAI - AI-Powered Technical Debt Analyzer

    Identify, quantify, and prioritize technical debt in your codebase.
    """
    pass


@cli.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Choice(["console", "json", "text", "markdown", "html"]),
    default="console",
    help="Output format",
)
@click.option("--output-file", "-f", type=click.Path(), help="Output file path")
@click.option("--format", "-F", "config_format", type=str, help="Custom configuration file (YAML)")
@click.option("--no-ai", is_flag=True, help="Disable AI-powered suggestions")
@click.option("--include-tests", is_flag=True, help="Include test files in analysis")
@click.option("--language", "-l", multiple=True, type=click.Choice(["python", "javascript", "typescript", "java"]), help="Languages to analyze")
@click.option("--max-complexity", type=int, default=10, help="Max cyclomatic complexity threshold")
@click.option("--max-length", type=int, default=50, help="Max method length threshold")
@click.option("--hourly-rate", type=float, default=150.0, help="Hourly rate for cost calculation")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def analyze(
    project_path: str,
    output: str,
    output_file: Optional[str],
    config_format: Optional[str],
    no_ai: bool,
    include_tests: bool,
    language: tuple,
    max_complexity: int,
    max_length: int,
    hourly_rate: float,
    verbose: bool,
):
    """
    Analyze a project for technical debt.

    PROJECT_PATH: Path to the project directory to analyze
    """
    console.print(f"[bold blue]RefactorAI[/bold blue] v{__version__}")
    console.print(f"Analyzing: [cyan]{os.path.abspath(project_path)}[/cyan]\n")

    # Build configuration
    file_types = [FileType(l.upper()) for l in language] if language else None

    config = AnalysisConfig(
        analyze_complexity=True,
        analyze_duplication=True,
        analyze_dependencies=True,
        analyze_dead_code=True,
        analyze_deprecations=True,
        generate_suggestions=not no_ai,
        generate_sprint_impact=True,
        max_cyclomatic_complexity=max_complexity,
        max_method_length=max_length,
        max_class_length=max_length * 10,
        include_tests=include_tests,
        file_types=file_types or [FileType.PYTHON],
        hourly_rate=hourly_rate,
        use_ai_suggestions=not no_ai,
    )

    # Load custom config if provided
    if config_format and os.path.exists(config_format):
        _load_custom_config(config, config_format)

    # Run analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing code...", total=None)

        try:
            analyzer = TechDebtAnalyzer(config)
            result, suggestions = analyzer.analyze_with_suggestions(project_path)

            progress.update(task, completed=100)

            # Format output
            if output == "console":
                formatted = ConsoleFormatter().format(result)
                console.print(formatted)
            elif output == "json":
                formatted = JSONFormatter().format(result)
                _write_output(formatted, output_file)
            elif output == "text":
                formatted = TextFormatter().format(result)
                _write_output(formatted, output_file)
            elif output == "markdown":
                formatted = MarkdownFormatter().format(result)
                _write_output(formatted, output_file)
            elif output == "html":
                formatted = HTMLFormatter().format(result)
                _write_output(formatted, output_file)

            # Show suggestions
            if suggestions and not no_ai:
                _show_suggestions(suggestions)

            # Show sprint impact
            if result.sprint_impact:
                _show_sprint_impact(result.sprint_impact)

            if verbose:
                console.print(f"\n[dim]Files analyzed: {result.files_analyzed}")
                console.print(f"[dim]Lines analyzed: {result.lines_analyzed:,}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output directory for visualizations")
@click.option("--format", "-f", type=click.Choice(["png", "svg", "pdf"]), default="png")
def visualize(project_path: str, output: Optional[str], format: str):
    """
    Generate visualizations of technical debt.
    """
    console.print(f"[bold blue]Generating Visualizations...[/bold blue]\n")

    config = AnalysisConfig()
    analyzer = TechDebtAnalyzer(config)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing...", total=None)
        result = analyzer.analyze(project_path)
        progress.update(task, completed=100)

    visualizer = DebtVisualizer(output_dir=output or "./refactorai_visuals")
    outputs = visualizer.generate_dashboard(result)

    console.print("\n[bold green]Generated Visualizations:[/bold green]")
    for name, path in outputs.items():
        if path:
            console.print(f"  - {name}: [cyan]{path}[/cyan]")


@cli.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["console", "json"]), default="console")
def sprint(project_path: str, format: str):
    """
    Predict sprint velocity impact of technical debt.
    """
    config = AnalysisConfig()
    analyzer = TechDebtAnalyzer(config)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing velocity impact...", total=None)
        result = analyzer.analyze(project_path)
        progress.update(task, completed=100)

    from refactorai.analysis.sprint_impact_predictor import SprintImpactPredictor

    predictor = SprintImpactPredictor(config)
    report = predictor.generate_velocity_report(result)

    if format == "console":
        console.print(report)
    else:
        console.print(json.dumps(result.sprint_impact.__dict__, indent=2))


@cli.command()
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--limit", "-n", type=int, default=10, help="Number of suggestions to show")
def suggest(project_path: str, limit: int):
    """
    Generate refactoring suggestions.
    """
    console.print(f"[bold blue]Generating Refactoring Suggestions...[/bold blue]\n")

    config = AnalysisConfig(generate_suggestions=True)
    analyzer = TechDebtAnalyzer(config)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing and generating suggestions...", total=None)
        result, suggestions = analyzer.analyze_with_suggestions(project_path)
        progress.update(task, completed=100)

    _show_suggestions(suggestions[:limit])


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def lint(file_path: str):
    """
    Quick lint a single file for code smells.
    """
    from refactorai.analysis.smell_detector import SmellDetector
    from refactorai.models.project import AnalysisConfig

    config = AnalysisConfig()
    detector = SmellDetector(config)

    with open(file_path, "r") as f:
        content = f.read()

    smells = detector.detect_in_file(file_path, content)

    if smells:
        table = Table(title=f"Code Smells in {file_path}")
        table.add_column("Line", style="cyan")
        table.add_column("Severity", style="white")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="white")

        for smell in smells:
            table.add_row(
                str(smell.location.line_start),
                smell.severity.label,
                smell.smell_type.value,
                smell.name[:50],
            )

        console.print(table)
        console.print(f"\n[bold red]Found {len(smells)} code smells[/bold red]")
    else:
        console.print(f"[bold green]No code smells found![/bold green]")


@cli.command()
@click.argument("project_path", type=click.Path(exists=True))
def report(project_path: str):
    """
    Generate a comprehensive HTML report.
    """
    output_path = Path(project_path).name + "_tech_debt_report.html"

    console.print(f"[bold blue]Generating HTML Report...[/bold blue]\n")

    config = AnalysisConfig()
    analyzer = TechDebtAnalyzer(config)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing...", total=None)
        result = analyzer.analyze(project_path)
        progress.update(task, completed=100)

    formatted = HTMLFormatter().format(result)

    with open(output_path, "w") as f:
        f.write(formatted)

    console.print(f"[bold green]Report generated:[/bold green] [cyan]{output_path}[/cyan]")


def _load_custom_config(config: AnalysisConfig, config_path: str) -> None:
    """Load custom configuration from YAML file."""
    import yaml

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)

        if data:
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")


def _write_output(content: str, output_file: Optional[str]) -> None:
    """Write output to file or stdout."""
    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        console.print(f"\n[bold green]Output written to:[/bold green] {output_file}")
    else:
        console.print("\n" + content)


def _show_suggestions(suggestions: list) -> None:
    """Display refactoring suggestions."""
    if not suggestions:
        return

    console.print(f"\n[bold cyan]Refactoring Suggestions ({len(suggestions)}):[/bold cyan]\n")

    table = Table()
    table.add_column("Priority", style="white")
    table.add_column("Pattern", style="magenta")
    table.add_column("Title", style="white")
    table.add_column("Effort", style="yellow")

    for suggestion in suggestions[:20]:
        priority_color = "red" if suggestion.priority >= 8 else "yellow" if suggestion.priority >= 5 else "green"
        table.add_row(
            f"[{priority_color}]{suggestion.priority:.0f}[/{priority_color}]",
            suggestion.pattern.value,
            suggestion.title[:40],
            f"${suggestion.priority * 50:.0f}",
        )

    console.print(table)


def _show_sprint_impact(impact) -> None:
    """Display sprint velocity impact."""
    console.print("\n[bold cyan]Sprint Velocity Impact:[/bold cyan]\n")
    console.print(f"  Current Velocity:      {impact.current_velocity:.1f} pts/sprint")
    console.print(f"  Predicted Velocity:    {impact.predicted_velocity_with_debt:.1f} pts/sprint")
    console.print(f"  Velocity Loss:         {impact.velocity_degradation_rate:.1f}%")
    console.print(f"  Risk Score:            {impact.risk_score:.1f}/10")
    console.print(f"  Remediation Cost:      ${impact.prioritized_fix_cost:,.2f}")
    console.print(f"  Recovery Time:         {impact.sprint_weeks_to_recover} weeks")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
