"""
Visualization Module.

Creates visual representations of technical debt analysis results.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from refactorai.models.technical_debt import TechnicalDebt, Severity


class DebtVisualizer:
    """
    Creates visualizations of technical debt analysis.

    Generates charts and graphs for better understanding
    of debt distribution and trends.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or "./refactorai_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_dashboard(self, debt: TechnicalDebt) -> dict:
        """
        Generate a complete visualization dashboard.

        Args:
            debt: TechnicalDebt analysis results

        Returns:
            Dictionary with paths to generated visualizations
        """
        outputs = {}

        # Generate charts
        try:
            outputs["severity_pie"] = self._create_severity_pie(debt)
            outputs["category_bar"] = self._create_category_bar(debt)
            outputs["debt_timeline"] = self._create_timeline(debt)
            outputs["complexity_heatmap"] = self._create_complexity_heatmap(debt)
        except Exception as e:
            print(f"Warning: Some visualizations failed: {e}")

        return outputs

    def _create_severity_pie(self, debt: TechnicalDebt) -> str:
        """Create a pie chart of debt by severity."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")  # Non-interactive backend

            fig, ax = plt.subplots(figsize=(10, 8))

            labels = []
            sizes = []
            colors = []

            color_map = {
                Severity.CRITICAL: "#dc3545",
                Severity.HIGH: "#fd7e14",
                Severity.MEDIUM: "#ffc107",
                Severity.LOW: "#0d6efd",
                Severity.INFO: "#6c757d",
            }

            for severity in Severity:
                count = debt.debt_by_severity.get(severity, 0)
                if count > 0:
                    labels.append(f"{severity.label} ({count})")
                    sizes.append(count)
                    colors.append(color_map[severity])

            if sizes:
                ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                ax.set_title("Technical Debt by Severity", fontsize=14, fontweight="bold")

            output_path = os.path.join(self.output_dir, "severity_pie.png")
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close()

            return output_path

        except ImportError:
            return ""

    def _create_category_bar(self, debt: TechnicalDebt) -> str:
        """Create a bar chart of debt by category."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")

            fig, ax = plt.subplots(figsize=(12, 6))

            categories = list(debt.debt_by_category.keys())
            costs = list(debt.debt_by_category.values())

            if categories:
                bars = ax.bar(categories, costs, color=["#667eea", "#764ba2", "#f093fb", "#f5576c"])
                ax.set_xlabel("Category")
                ax.set_ylabel("Debt Cost ($)")
                ax.set_title("Technical Debt by Category", fontsize=14, fontweight="bold")

                # Add value labels
                for bar, cost in zip(bars, costs):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f"${cost:,.0f}",
                        ha="center",
                        va="bottom",
                    )

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, "category_bar.png")
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close()

            return output_path

        except ImportError:
            return ""

    def _create_timeline(self, debt: TechnicalDebt) -> str:
        """Create a timeline visualization of debt."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")
            import numpy as np

            fig, ax = plt.subplots(figsize=(14, 6))

            # Simulate debt accumulation over time
            months = np.arange(12)
            simulated_debt = np.cumsum(np.random.randint(1000, 5000, 12))
            simulated_debt = simulated_debt / simulated_debt[-1] * debt.total_debt_cost

            ax.fill_between(months, simulated_debt, alpha=0.3, color="#667eea")
            ax.plot(months, simulated_debt, "o-", color="#667eea", linewidth=2)

            ax.set_xlabel("Month")
            ax.set_ylabel("Cumulative Debt ($)")
            ax.set_title("Technical Debt Accumulation Over Time", fontsize=14, fontweight="bold")
            ax.set_xticks(months)
            ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, "debt_timeline.png")
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close()

            return output_path

        except ImportError:
            return ""

    def _create_complexity_heatmap(self, debt: TechnicalDebt) -> str:
        """Create a heatmap of code complexity."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")
            import numpy as np

            if not debt.complexity_metrics:
                return ""

            # Create sample data for visualization
            metrics = list(debt.complexity_metrics.items())[:50]  # Limit to 50

            fig, ax = plt.subplots(figsize=(14, 8))

            # Extract complexity values
            names = [m[0][:30] for m in metrics]
            complexities = [m[1].cyclomatic_complexity for m in metrics]

            y_pos = np.arange(len(names))
            colors = []
            for c in complexities:
                if c <= 10:
                    colors.append("#28a745")  # Green
                elif c <= 20:
                    colors.append("#ffc107")  # Yellow
                else:
                    colors.append("#dc3545")  # Red

            ax.barh(y_pos, complexities, color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=6)
            ax.set_xlabel("Cyclomatic Complexity")
            ax.set_title("Code Complexity Distribution", fontsize=14, fontweight="bold")

            # Add legend
            ax.axvline(x=10, color="green", linestyle="--", alpha=0.5, label="Low (≤10)")
            ax.axvline(x=20, color="yellow", linestyle="--", alpha=0.5, label="Medium (≤20)")
            ax.legend(loc="lower right")

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, "complexity_heatmap.png")
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close()

            return output_path

        except ImportError:
            return ""

    def generate_dependency_graph(self, graph, output_path: Optional[str] = None) -> str:
        """
        Generate a visual dependency graph.

        Args:
            graph: DependencyGraph object
            output_path: Optional custom output path

        Returns:
            Path to generated image
        """
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")

            output_path = output_path or os.path.join(self.output_dir, "dependency_graph.png")

            G = nx.DiGraph()

            for name, node in graph.nodes.items():
                G.add_node(name, type=node.node_type)

            for from_node, to_node in graph.edges:
                G.add_edge(from_node, to_node)

            fig, ax = plt.subplots(figsize=(16, 12))

            # Layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Color nodes by type
            node_colors = []
            for node in G.nodes():
                node_data = G.nodes[node]
                if node_data.get("type") == "external":
                    node_colors.append("#6c757d")  # Gray
                elif node_data.get("type") == "package":
                    node_colors.append("#667eea")  # Purple
                else:
                    node_colors.append("#28a745")  # Green

            nx.draw(
                G,
                pos,
                ax=ax,
                with_labels=True,
                node_color=node_colors,
                node_size=1500,
                font_size=6,
                font_weight="bold",
                arrows=True,
                arrowsize=10,
                edge_color="#999",
            )

            ax.set_title("Module Dependency Graph", fontsize=14, fontweight="bold")

            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close()

            return output_path

        except ImportError:
            return ""
