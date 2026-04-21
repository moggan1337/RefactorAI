"""
FastAPI Server for RefactorAI.

Provides a REST API for technical debt analysis.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from refactorai import __version__
from refactorai.analysis.analyzer import TechDebtAnalyzer
from refactorai.models.project import AnalysisConfig, FileType
from refactorai.models.technical_debt import TechnicalDebt, CodeSmell, Severity

# Initialize FastAPI app
app = FastAPI(
    title="RefactorAI API",
    description="AI-Powered Technical Debt Analyzer API",
    version=__version__,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results
analysis_results: dict[str, dict] = {}


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for analysis."""

    project_path: str = Field(..., description="Path to the project to analyze")
    analyze_complexity: bool = Field(True, description="Enable complexity analysis")
    analyze_duplication: bool = Field(True, description="Enable duplication detection")
    analyze_dependencies: bool = Field(True, description="Enable dependency analysis")
    analyze_dead_code: bool = Field(True, description="Enable dead code detection")
    analyze_deprecations: bool = Field(True, description="Enable deprecation tracking")
    max_cyclomatic_complexity: int = Field(10, description="Max cyclomatic complexity threshold")
    max_method_length: int = Field(50, description="Max method length threshold")
    include_tests: bool = Field(False, description="Include test files in analysis")
    use_ai_suggestions: bool = Field(True, description="Generate AI-powered refactoring suggestions")


class SmellSummary(BaseModel):
    """Summary of a code smell."""

    id: str
    type: str
    severity: str
    name: str
    location: str
    cost: float
    effort_hours: float


class AnalysisSummary(BaseModel):
    """Summary of analysis results."""

    id: str
    project_path: str
    analyzed_at: str
    debt_score: float
    debt_rating: str
    total_cost: float
    total_hours: float
    files_analyzed: int
    lines_analyzed: int
    smells_count: int
    duplications_count: int
    dependency_cycles_count: int
    dead_code_count: int
    deprecations_count: int


class AnalyzeResponse(BaseModel):
    """Response model for analysis."""

    status: str
    analysis_id: str
    summary: AnalysisSummary
    smells: List[SmellSummary]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RefactorAI API",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": __version__}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_project(request: AnalyzeRequest):
    """
    Analyze a project for technical debt.

    Returns a summary of findings and all detected code smells.
    """
    if not os.path.exists(request.project_path):
        raise HTTPException(status_code=400, detail=f"Project path does not exist: {request.project_path}")

    # Build configuration
    config = AnalysisConfig(
        analyze_complexity=request.analyze_complexity,
        analyze_duplication=request.analyze_duplication,
        analyze_dependencies=request.analyze_dependencies,
        analyze_dead_code=request.analyze_dead_code,
        analyze_deprecations=request.analyze_deprecations,
        generate_suggestions=request.use_ai_suggestions,
        generate_sprint_impact=True,
        max_cyclomatic_complexity=request.max_cyclomatic_complexity,
        max_method_length=request.max_method_length,
        include_tests=request.include_tests,
    )

    # Run analysis
    analyzer = TechDebtAnalyzer(config)
    result, suggestions = analyzer.analyze_with_suggestions(request.project_path)

    # Store results
    analysis_results[result.id] = {
        "result": result,
        "suggestions": suggestions,
    }

    # Build response
    summary = AnalysisSummary(
        id=result.id,
        project_path=result.project_path,
        analyzed_at=result.analyzed_at.isoformat(),
        debt_score=result.debt_score,
        debt_rating=result.debt_rating,
        total_cost=result.total_debt_cost,
        total_hours=result.debt_hours,
        files_analyzed=result.files_analyzed,
        lines_analyzed=result.lines_analyzed,
        smells_count=len(result.smells),
        duplications_count=len(result.duplications),
        dependency_cycles_count=len(result.dependency_cycles),
        dead_code_count=len(result.dead_code),
        deprecations_count=len(result.deprecations),
    )

    smells = [
        SmellSummary(
            id=smell.id,
            type=smell.smell_type.value,
            severity=smell.severity.label,
            name=smell.name,
            location=str(smell.location),
            cost=smell.technical_debt_cost,
            effort_hours=smell.effort_hours,
        )
        for smell in result.smells
    ]

    return AnalyzeResponse(
        status="completed",
        analysis_id=result.id,
        summary=summary,
        smells=smells,
    )


@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a previously run analysis by ID."""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")

    data = analysis_results[analysis_id]
    result = data["result"]
    suggestions = data["suggestions"]

    return {
        "id": result.id,
        "project_path": result.project_path,
        "analyzed_at": result.analyzed_at.isoformat(),
        "debt_score": result.debt_score,
        "debt_rating": result.debt_rating,
        "total_cost": result.total_debt_cost,
        "smells": [
            {
                "id": s.id,
                "type": s.smell_type.value,
                "severity": s.severity.label,
                "name": s.name,
                "description": s.description,
                "location": str(s.location),
                "cost": s.technical_debt_cost,
                "effort_hours": s.effort_hours,
                "tags": s.tags,
            }
            for s in result.smells
        ],
        "suggestions": [
            {
                "id": s.id,
                "pattern": s.pattern.value,
                "title": s.title,
                "description": s.description,
                "confidence": s.confidence,
                "priority": s.priority,
                "automated": s.automated,
            }
            for s in suggestions
        ],
    }


@app.get("/project-stats/{project_path}")
async def get_project_stats(project_path: str):
    """Get statistics about a project without full analysis."""
    from refactorai.utils.file_scanner import FileScanner

    if not os.path.exists(project_path):
        raise HTTPException(status_code=400, detail="Project path does not exist")

    scanner = FileScanner()
    stats = scanner.get_project_stats(project_path)

    return {
        "project_path": project_path,
        "total_files": stats["total_files"],
        "total_lines": stats["total_lines"],
        "by_language": stats["by_language"],
    }


def main():
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
