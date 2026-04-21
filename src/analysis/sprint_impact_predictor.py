"""
Sprint Velocity Impact Prediction Module.

Predicts how technical debt will affect sprint velocity
and estimates the ROI of debt remediation.
"""

from __future__ import annotations

from typing import Optional

from refactorai.models.project import AnalysisConfig
from refactorai.models.technical_debt import TechnicalDebt, SprintImpact, Severity


class SprintImpactPredictor:
    """
    Predicts the impact of technical debt on sprint velocity.

    Uses historical data patterns and debt metrics to estimate:
    - Velocity degradation over time
    - Cost of debt remediation
    - ROI of addressing debt
    """

    # Constants for prediction models
    DEGRADATION_RATE_PER_SMELL = {
        Severity.CRITICAL: 0.05,  # 5% velocity loss per critical smell
        Severity.HIGH: 0.03,
        Severity.MEDIUM: 0.01,
        Severity.LOW: 0.005,
        Severity.INFO: 0.001,
    }

    # Recovery factors after remediation
    RECOVERY_FACTOR = {
        Severity.CRITICAL: 0.15,  # 15% velocity recovery per critical fixed
        Severity.HIGH: 0.10,
        Severity.MEDIUM: 0.05,
        Severity.LOW: 0.02,
        Severity.INFO: 0.01,
    }

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.hourly_rate = config.hourly_rate

    def predict(self, debt: TechnicalDebt, current_velocity: float = 20.0) -> SprintImpact:
        """
        Predict sprint velocity impact based on technical debt.

        Args:
            debt: TechnicalDebt analysis results
            current_velocity: Current story points per sprint (default: 20)

        Returns:
            SprintImpact prediction object
        """
        # Count debts by severity
        debts_by_severity = debt.debt_by_severity

        # Calculate degradation
        total_degradation = sum(
            count * self.DEGRADATION_RATE_PER_SMELL[severity]
            for severity, count in debts_by_severity.items()
        )

        # Calculate recovery (if we fix critical and high)
        critical_and_high = debts_by_severity[Severity.CRITICAL] + debts_by_severity[Severity.HIGH]
        recovery_potential = sum(
            count * self.RECOVERY_FACTOR[severity]
            for severity, count in debts_by_severity.items()
        )

        # Predicted velocities
        velocity_with_debt = current_velocity * (1 - min(0.5, total_degradation))
        velocity_after_fix = current_velocity * (1 - min(0.5, total_degradation - recovery_potential))

        # Calculate costs
        total_debt_cost = debt.total_debt_cost
        prioritized_cost = sum(
            smell.technical_debt_cost
            for smell in debt.get_critical_smells()
        )

        # Sprint recovery estimate
        # Assume 1 sprint = 2 weeks, recovery happens gradually
        avg_sprint_velocity_loss = current_velocity * min(0.5, total_degradation)
        sprints_to_recover = int(avg_sprint_velocity_loss / max(1, velocity_after_fix - velocity_with_debt)) if velocity_after_fix > velocity_with_debt else 0

        return SprintImpact(
            current_velocity=current_velocity,
            predicted_velocity_with_debt=velocity_with_debt,
            debt_remediation_cost=total_debt_cost,
            prioritized_fix_cost=prioritized_cost,
            estimated_velocity_improvement=((velocity_after_fix - velocity_with_debt) / velocity_with_debt * 100) if velocity_with_debt > 0 else 0,
            sprint_weeks_to_recover=sprints_to_recover * 2,  # Convert sprints to weeks
            risk_score=self._calculate_risk_score(debt),
        )

    def _calculate_risk_score(self, debt: TechnicalDebt) -> float:
        """
        Calculate delivery risk score (0-10).

        Based on severity, complexity, and architectural issues.
        """
        risk = 0.0

        # Critical and high smells increase risk
        critical_high = debt.debt_by_severity[Severity.CRITICAL] + debt.debt_by_severity[Severity.HIGH]
        risk += min(4.0, critical_high * 0.5)

        # Dependency cycles are high risk
        risk += min(2.0, len(debt.dependency_cycles) * 0.5)

        # Dead code increases risk
        risk += min(1.0, len(debt.dead_code) * 0.1)

        # Deprecated APIs are medium risk
        risk += min(1.5, len(debt.deprecations) * 0.2)

        # High complexity increases risk
        avg_complexity = sum(
            m.cyclomatic_complexity for m in debt.complexity_metrics.values()
        ) / max(1, len(debt.complexity_metrics))
        if avg_complexity > 15:
            risk += 1.5
        elif avg_complexity > 10:
            risk += 0.5

        return min(10.0, risk)

    def estimate_fix_effort(self, debt: TechnicalDebt) -> dict:
        """
        Estimate the effort to fix all technical debt.

        Returns a breakdown by category and severity.
        """
        effort_by_category = {}
        effort_by_severity = {}

        for smell in debt.smells:
            category = smell.category
            severity = smell.severity

            # By category
            if category not in effort_by_category:
                effort_by_category[category] = {"hours": 0, "cost": 0, "count": 0}
            effort_by_category[category]["hours"] += smell.effort_hours
            effort_by_category[category]["cost"] += smell.technical_debt_cost
            effort_by_category[category]["count"] += 1

            # By severity
            if severity not in effort_by_severity:
                effort_by_severity[severity] = {"hours": 0, "cost": 0, "count": 0}
            effort_by_severity[severity]["hours"] += smell.effort_hours
            effort_by_severity[severity]["cost"] += smell.technical_debt_cost
            effort_by_severity[severity]["count"] += 1

        return {
            "total_hours": debt.debt_hours,
            "total_cost": debt.total_debt_cost,
            "by_category": effort_by_category,
            "by_severity": {
                k.label: v for k, v in effort_by_severity.items()
            },
        }

    def calculate_roi(self, debt: TechnicalDebt, velocity: float = 20.0) -> dict:
        """
        Calculate ROI of debt remediation.

        Args:
            debt: TechnicalDebt analysis
            velocity: Current sprint velocity

        Returns:
            Dictionary with ROI metrics
        """
        impact = self.predict(debt, velocity)
        effort = self.estimate_fix_effort(debt)

        # ROI calculation
        # Assumes 1 story point = $1000 (development cost)
        story_point_value = 1000
        velocity_loss_per_sprint = velocity - impact.predicted_velocity_with_debt

        # Annual cost of velocity loss (26 sprints/year)
        annual_velocity_cost = velocity_loss_per_sprint * 26 * story_point_value

        # ROI = (Benefit - Cost) / Cost * 100
        roi = ((annual_velocity_cost - impact.prioritized_fix_cost) / impact.prioritized_fix_cost * 100) if impact.prioritized_fix_cost > 0 else 0

        # Payback period in weeks
        weekly_velocity_loss = velocity_loss_per_sprint * story_point_value / 2  # 2 weeks per sprint
        payback_weeks = impact.prioritized_fix_cost / weekly_velocity_loss if weekly_velocity_loss > 0 else 0

        return {
            "annual_velocity_cost": annual_velocity_cost,
            "remediation_cost": impact.prioritized_fix_cost,
            "roi_percentage": roi,
            "payback_period_weeks": min(payback_weeks, 260),  # Cap at 5 years
            "net_annual_benefit": annual_velocity_cost - impact.prioritized_fix_cost,
            "break_even_sprints": impact.prioritized_fix_cost / (velocity_loss_per_sprint * story_point_value) if velocity_loss_per_sprint > 0 else 0,
        }

    def generate_velocity_report(self, debt: TechnicalDebt, current_velocity: float = 20.0) -> str:
        """
        Generate a comprehensive velocity impact report.

        Args:
            debt: TechnicalDebt analysis
            current_velocity: Current sprint velocity

        Returns:
            Formatted report as a string
        """
        impact = self.predict(debt, current_velocity)
        roi = self.calculate_roi(debt, current_velocity)
        effort = self.estimate_fix_effort(debt)

        report = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TECHNICAL DEBT SPRINT VELOCITY REPORT                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
"""

        # Current State
        report += f"""
│ CURRENT STATE
│   Current Sprint Velocity:     {current_velocity:.1f} story points/sprint
│   Risk Score:                  {impact.risk_score:.1f}/10
│   Total Debt Cost:              ${debt.total_debt_cost:,.2f}
│   Total Debt Hours:             {debt.debt_hours:.1f} hours
"""

        # Velocity Impact
        report += f"""
│ VELOCITY IMPACT
│   Predicted Velocity (with debt): {impact.predicted_velocity_with_debt:.1f} pts/sprint
│   Velocity Degradation:            {impact.velocity_degradation_rate:.1f}%
│   Velocity After Fix:              {current_velocity:.1f} pts/sprint (potential)
│   Expected Improvement:            {impact.estimated_velocity_improvement:.1f}%
│   Recovery Time:                   {impact.sprint_weeks_to_recover} weeks
"""

        # ROI
        report += f"""
│ RETURN ON INVESTMENT
│   Annual Cost of Debt:          ${roi['annual_velocity_cost']:,.2f}
│   Remediation Investment:       ${roi['remediation_cost']:,.2f}
│   Net Annual Benefit:            ${roi['net_annual_benefit']:,.2f}
│   ROI:                          {roi['roi_percentage']:.1f}%
│   Break-Even:                   {roi['break_even_sprints']:.1f} sprints
│   Payback Period:               {roi['payback_weeks']:.1f} weeks
"""

        # Effort Breakdown
        report += f"""
│ REMEDIATION EFFORT
│   Total Hours:                  {effort['total_hours']:.1f}
│   Total Cost:                   ${effort['total_cost']:,.2f}
│
│   By Severity:"""

        for severity, data in effort["by_severity"].items():
            report += f"""
│     {severity:12s}: {data['count']:3d} issues, {data['hours']:6.1f} hrs, ${data['cost']:8,.2f}"""

        report += """
╚══════════════════════════════════════════════════════════════════════════════╝
"""

        return report

    def what_if_analysis(
        self,
        debt: TechnicalDebt,
        current_velocity: float,
        fix_critical_only: bool = True,
    ) -> dict:
        """
        What-if analysis: What happens if we only fix critical issues?

        Args:
            debt: TechnicalDebt analysis
            current_velocity: Current velocity
            fix_critical_only: If True, only fix CRITICAL+HIGH; if False, fix all

        Returns:
            Analysis results
        """
        if fix_critical_only:
            # Calculate impact of fixing only critical + high
            critical_high_cost = sum(
                smell.technical_debt_cost
                for smell in debt.smells
                if smell.severity in (Severity.CRITICAL, Severity.HIGH)
            )
            critical_high_hours = sum(
                smell.effort_hours
                for smell in debt.smells
                if smell.severity in (Severity.CRITICAL, Severity.HIGH)
            )
        else:
            critical_high_cost = debt.total_debt_cost
            critical_high_hours = debt.debt_hours

        # Recalculate velocity impact
        remaining_debt = debt.total_debt_cost - critical_high_cost
        remaining_smells = len(debt.smells) - (
            debt.debt_by_severity[Severity.CRITICAL] + debt.debt_by_severity[Severity.HIGH]
        )

        # Simplified velocity calculation
        remaining_degradation = remaining_debt / max(1, debt.total_debt_cost) * 0.3  # Max 30% degradation
        new_velocity = current_velocity * (1 - remaining_degradation)

        return {
            "scenario": "Critical + High Only" if fix_critical_only else "Full Remediation",
            "cost": critical_high_cost,
            "hours": critical_high_hours,
            "remaining_debt": remaining_debt,
            "remaining_smells": remaining_smells,
            "predicted_velocity": new_velocity,
            "velocity_recovery": current_velocity - new_velocity,
            "percentage_coverage": (
                (1 - remaining_debt / debt.total_debt_cost) * 100 if debt.total_debt_cost > 0 else 0
            ),
        }
