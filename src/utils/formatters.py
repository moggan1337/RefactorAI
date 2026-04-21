"""
Report Formatters Module.

Provides various output formats for analysis results.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from refactorai.models.technical_debt import TechnicalDebt, CodeSmell, Severity
from refactorai.models.project import ProjectAnalysis


class ReportFormatter:
    """Base class for report formatters."""

    def format(self, debt: TechnicalDebt) -> str:
        """Format technical debt analysis as a string."""
        raise NotImplementedError


class JSONFormatter(ReportFormatter):
    """Format results as JSON."""

    def __init__(self, pretty: bool = True):
        self.pretty = pretty

    def format(self, debt: TechnicalDebt) -> str:
        """Format as JSON."""
        data = debt.to_dict()

        # Add smells
        data["smells"] = [
            {
                "id": s.id,
                "type": s.smell_type.value,
                "severity": s.severity.label,
                "name": s.name,
                "description": s.description,
                "location": str(s.location),
                "effort_hours": s.effort_hours,
                "cost": s.technical_debt_cost,
                "tags": s.tags,
            }
            for s in debt.smells
        ]

        # Add duplications
        data["duplications"] = [
            {
                "lines": d.lines,
                "locations": [str(loc) for loc in d.locations],
            }
            for d in debt.duplications
        ]

        if self.pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)


class TextFormatter(ReportFormatter):
    """Format results as plain text."""

    def format(self, debt: TechnicalDebt) -> str:
        """Format as plain text."""
        lines = []
        lines.append("=" * 80)
        lines.append("TECHNICAL DEBT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Project: {debt.project_path}")
        lines.append(f"Analyzed: {debt.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Files Analyzed: {debt.files_analyzed}")
        lines.append(f"Lines Analyzed: {debt.lines_analyzed}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Debt Score: {debt.debt_score:.1f}/100 ({debt.debt_rating})")
        lines.append(f"Total Debt Cost: ${debt.total_debt_cost:,.2f}")
        lines.append(f"Total Debt Hours: {debt.debt_hours:.1f}")
        lines.append("")

        # By Severity
        lines.append("Debt by Severity:")
        for severity in Severity:
            count = debt.debt_by_severity.get(severity, 0)
            if count > 0:
                lines.append(f"  {severity.label}: {count}")
        lines.append("")

        # By Category
        lines.append("Debt by Category:")
        for category, cost in debt.debt_by_category.items():
            lines.append(f"  {category}: ${cost:,.2f}")
        lines.append("")

        # Critical Issues
        critical = debt.get_critical_smells()
        if critical:
            lines.append("-" * 80)
            lines.append(f"CRITICAL/HIGH ISSUES ({len(critical)})")
            lines.append("-" * 80)
            for smell in critical[:20]:  # Limit to 20
                lines.append(f"\n[{smell.severity.label}] {smell.name}")
                lines.append(f"  Location: {smell.location}")
                lines.append(f"  Cost: ${smell.technical_debt_cost:,.2f}")
                lines.append(f"  Effort: {smell.effort_hours:.1f} hours")
            if len(critical) > 20:
                lines.append(f"\n... and {len(critical) - 20} more critical issues")

        return "\n".join(lines)


class MarkdownFormatter(ReportFormatter):
    """Format results as Markdown."""

    def format(self, debt: TechnicalDebt) -> str:
        """Format as Markdown."""
        lines = []
        lines.append("# Technical Debt Analysis Report")
        lines.append("")
        lines.append(f"**Project:** `{debt.project_path}`  ")
        lines.append(f"**Analyzed:** {debt.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}  ")
        lines.append(f"**Language:** {debt.language}  ")
        lines.append("")
        lines.append("## Summary")
        lines.append("")

        # Summary cards
        lines.append(f"| Metric | Value |")
        lines.append(f"|---------|-------|")
        lines.append(f"| Debt Score | {debt.debt_score:.1f}/100 ({debt.debt_rating}) |")
        lines.append(f"| Total Cost | ${debt.total_debt_cost:,.2f} |")
        lines.append(f"| Total Hours | {debt.debt_hours:.1f} |")
        lines.append(f"| Files Analyzed | {debt.files_analyzed} |")
        lines.append(f"| Lines Analyzed | {debt.lines_analyzed:,} |")
        lines.append("")

        # By Severity
        lines.append("## Debt by Severity")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity in Severity:
            count = debt.debt_by_severity.get(severity, 0)
            if count > 0:
                emoji = {
                    Severity.CRITICAL: "🔴",
                    Severity.HIGH: "🟠",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🔵",
                    Severity.INFO: "⚪",
                }.get(severity, "")
                lines.append(f"| {emoji} {severity.label} | {count} |")
        lines.append("")

        # By Category
        lines.append("## Debt by Category")
        lines.append("")
        lines.append("| Category | Cost |")
        lines.append("|----------|------|")
        for category, cost in debt.debt_by_category.items():
            lines.append(f"| {category} | ${cost:,.2f} |")
        lines.append("")

        # Code Smells
        if debt.smells:
            lines.append("## Code Smells")
            lines.append("")

            for smell in debt.smells[:50]:  # Limit to 50
                lines.append(f"### {smell.name}")
                lines.append("")
                lines.append(f"- **Severity:** {smell.severity.label}")
                lines.append(f"- **Type:** {smell.smell_type.value}")
                lines.append(f"- **Location:** `{smell.location}`")
                lines.append(f"- **Effort:** {smell.effort_hours:.1f} hours")
                lines.append(f"- **Cost:** ${smell.technical_debt_cost:,.2f}")
                if smell.description:
                    lines.append(f"- **Description:** {smell.description}")
                if smell.tags:
                    lines.append(f"- **Tags:** {', '.join(smell.tags)}")
                lines.append("")

        # Duplications
        if debt.duplications:
            lines.append("## Code Duplications")
            lines.append("")
            lines.append(f"Found **{len(debt.duplications)}** duplicated code blocks.")
            lines.append("")

            for i, dup in enumerate(debt.duplications[:10], 1):
                lines.append(f"### Duplication #{i}")
                lines.append(f"- **Lines:** {dup.lines}")
                lines.append(f"- **Locations:**")
                for loc in dup.locations:
                    lines.append(f"  - `{loc}`")
                lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        critical = debt.get_critical_smells()
        if critical:
            lines.append(f"Address the {len(critical)} critical/high severity issues first.")
            lines.append("")
            lines.append("### Priority Actions")
            for smell in critical[:5]:
                lines.append(f"1. **{smell.name}** - ${smell.technical_debt_cost:,.2f}")
        else:
            lines.append("No critical issues found. Maintain code quality to prevent debt accumulation.")

        return "\n".join(lines)


class HTMLFormatter(ReportFormatter):
    """Format results as HTML."""

    def format(self, debt: TechnicalDebt) -> str:
        """Format as HTML."""
        severity_colors = {
            Severity.CRITICAL: "#dc3545",
            Severity.HIGH: "#fd7e14",
            Severity.MEDIUM: "#ffc107",
            Severity.LOW: "#0d6efd",
            Severity.INFO: "#6c757d",
        }

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Technical Debt Report - {debt.project_path}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .header .meta {{ opacity: 0.9; }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .metric {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .metric .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .severity-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .smell {{
            border-left: 4px solid;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }}
        .smell h4 {{ margin: 0 0 10px 0; }}
        .smell .meta {{
            font-size: 0.9em;
            color: #666;
        }}
        .chart-placeholder {{
            height: 300px;
            background: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Technical Debt Analysis Report</h1>
        <div class="meta">
            <p><strong>Project:</strong> {debt.project_path}</p>
            <p><strong>Analyzed:</strong> {debt.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Language:</strong> {debt.language}</p>
        </div>
    </div>

    <div class="card">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="metric">
                <div class="value" style="color: {'#dc3545' if debt.debt_score > 50 else '#ffc107' if debt.debt_score > 25 else '#28a745'}">{debt.debt_score:.1f}</div>
                <div class="label">Debt Score</div>
            </div>
            <div class="metric">
                <div class="value">${debt.total_debt_cost:,.0f}</div>
                <div class="label">Total Cost</div>
            </div>
            <div class="metric">
                <div class="value">{debt.debt_hours:.0f}h</div>
                <div class="label">Effort Required</div>
            </div>
            <div class="metric">
                <div class="value">{len(debt.smells)}</div>
                <div class="label">Issues Found</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Debt by Severity</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #eee;">
                <th style="text-align: left; padding: 10px;">Severity</th>
                <th style="text-align: right; padding: 10px;">Count</th>
                <th style="text-align: right; padding: 10px;">Cost</th>
            </tr>
"""

        for severity in Severity:
            count = debt.debt_by_severity.get(severity, 0)
            cost = sum(s.technical_debt_cost for s in debt.smells if s.severity == severity)
            if count > 0:
                color = severity_colors.get(severity, "#666")
                html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;"><span class="severity-badge" style="background: {color}">{severity.label}</span></td>
                <td style="text-align: right; padding: 10px;">{count}</td>
                <td style="text-align: right; padding: 10px;">${cost:,.2f}</td>
            </tr>
"""

        html += """
        </table>
    </div>
"""

        # Code Smells
        critical = debt.get_critical_smells()
        if critical:
            html += """
    <div class="card">
        <h2>🔴 Critical & High Priority Issues</h2>
"""
            for smell in critical[:20]:
                color = severity_colors.get(smell.severity, "#666")
                html += f"""
        <div class="smell" style="border-color: {color}">
            <h4>{smell.name}</h4>
            <p>{smell.description}</p>
            <div class="meta">
                <strong>Location:</strong> {smell.location} |
                <strong>Effort:</strong> {smell.effort_hours:.1f}h |
                <strong>Cost:</strong> ${smell.technical_debt_cost:,.2f}
            </div>
        </div>
"""

            html += """
    </div>
"""

        html += """
</body>
</html>
"""
        return html


class ConsoleFormatter(ReportFormatter):
    """Format results for console output with colors."""

    def format(self, debt: TechnicalDebt) -> str:
        """Format for console with ANSI colors."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text

            console = Console()
            output = []

            # Summary panel
            score_color = "red" if debt.debt_score > 50 else "yellow" if debt.debt_score > 25 else "green"

            summary = f"""
[bold]Project:[/bold] {debt.project_path}
[bold]Debt Score:[/bold] [{score_color}]{debt.debt_score:.1f}[/{score_color}]/100 ({debt.debt_rating})
[bold]Total Cost:[/bold] ${debt.total_debt_cost:,.2f}
[bold]Total Hours:[/bold] {debt.debt_hours:.1f}
[bold]Issues:[/bold] {len(debt.smells)} code smells, {len(debt.duplications)} duplications
"""
            output.append(Panel(summary, title="[bold]Technical Debt Summary[/bold]", border_style="blue"))

            # Smells table
            if debt.smells:
                table = Table(title="Code Smells by Severity")
                table.add_column("Severity", style="white")
                table.add_column("Count", justify="right")

                for severity in Severity:
                    count = debt.debt_by_severity.get(severity, 0)
                    if count > 0:
                        color = {
                            Severity.CRITICAL: "red",
                            Severity.HIGH: "orange1",
                            Severity.MEDIUM: "yellow",
                            Severity.LOW: "blue",
                            Severity.INFO: "white",
                        }.get(severity, "white")
                        table.add_row(f"[{color}]{severity.label}[/{color}]", str(count))

                output.append(table)

            return "\n".join(str(p) for p in output)

        except ImportError:
            # Fallback to text formatter
            return TextFormatter().format(debt)
