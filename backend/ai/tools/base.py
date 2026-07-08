"""
==========================================================
NexusERP-AI — Base Tool
==========================================================

Every AI tool in NexusERP inherits from BaseTool.

Contract
--------
Every tool must define:
    name        : str  — unique identifier used by registry
    description : str  — used by planner to choose tools
    execute()   : method — runs the tool logic

Every tool receives a ToolContext containing:
    company     : Company instance — enforces isolation
    user        : User instance    — for permissions

Every tool returns a ToolResult:
    success     : bool
    tool        : str (tool name)
    data        : any structured result
    message     : str (human-readable summary)
    error       : str (only when success=False)

Tools must NOT:
    - Query the database directly
    - Build prompts
    - Call Ollama
    - Decide which other tool to run next
    - Return raw exceptions
==========================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


# ==========================================================
# TOOL CONTEXT
# ==========================================================

@dataclass
class ToolContext:
    """
    Passed to every tool on execute().

    Provides company isolation, user identity,
    and request metadata without each tool
    needing to extract these from request objects.

    Every tool automatically respects company
    isolation by using context.company.
    """

    company: Any
    user: Any
    conversation_id: Optional[str] = None
    extra: dict = field(default_factory=dict)


# ==========================================================
# TOOL RESULT
# ==========================================================

@dataclass
class ToolResult:
    """
    Standard return type for every tool.

    Using a dataclass instead of plain dicts ensures
    the planner and LLM always receive consistent
    structure regardless of which tool ran.
    """

    success: bool
    tool: str
    data: Any = None
    message: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        """
        Convert to a plain dictionary for JSON
        serialization and LLM consumption.
        """
        if self.success:
            return {
                "success": True,
                "tool":    self.tool,
                "data":    self.data,
                "message": self.message,
            }
        return {
            "success": False,
            "tool":    self.tool,
            "error":   self.error,
        }


# ==========================================================
# BASE TOOL
# ==========================================================

class BaseTool(ABC):
    """
    Abstract base class for all NexusERP AI tools.

    Subclasses must define:
        name        : str
        description : str
        execute()   : method

    Subclasses should NOT override:
        run()       : handles error wrapping automatically

    Usage:
        class EmployeeSummaryTool(BaseTool):
            name = "employee_summary"
            description = "Returns employee count and status breakdown."

            def execute(self, context, **kwargs):
                service = EmployeeReportService(context.company)
                data = service.employee_summary()
                return ToolResult(
                    success=True,
                    tool=self.name,
                    data=data,
                    message=f"Found {data['total']} employees.",
                )
    """

    name: str = ""
    description: str = ""

    def run(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:
        """
        Public entry point for all tools.

        Wraps execute() with error handling so
        uncaught exceptions never reach the view layer.

        The planner and executor always call run(),
        never execute() directly.
        """

        try:
            return self.execute(context, **kwargs)

        except Exception as exc:
            return ToolResult(
                success=False,
                tool=self.name,
                error=str(exc),
            )

    @abstractmethod
    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:
        """
        Implement this in every tool subclass.

        Parameters
        ----------
        context : ToolContext
            Provides company, user, and metadata.
        **kwargs
            Tool-specific input parameters.

        Returns
        -------
        ToolResult
            Always return a ToolResult, never raise.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"