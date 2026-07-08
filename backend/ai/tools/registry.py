"""
==========================================================
NexusERP-AI — Tool Registry
==========================================================

The ToolRegistry is like Django's URL router —
but instead of routing HTTP paths to views,
it routes tool names to tool classes.

The Planner never imports tools directly.
It asks the registry:

    registry.get("employee_summary")
    → EmployeeSummaryTool instance

This means:
    - Adding a new tool = one line in registry.py
    - Planner never changes when tools are added
    - Tools can be listed for the LLM to choose from
==========================================================
"""

from ai.exceptions import ToolNotFoundException


# ==========================================================
# TOOL REGISTRY
# ==========================================================

class ToolRegistry:
    """
    Central registry for all NexusERP AI tools.

    Usage
    -----
    registry = ToolRegistry()
    registry.register(EmployeeSummaryTool)
    tool = registry.get("employee_summary")
    result = tool.run(context)
    """

    def __init__(self):
        self._tools: dict = {}

    def register(self, tool_class) -> None:
        """
        Register a tool class by its name.

        Parameters
        ----------
        tool_class : type
            A subclass of BaseTool with a non-empty name.
        """

        if not tool_class.name:
            raise ValueError(
                f"{tool_class.__name__} must define a non-empty name."
            )

        self._tools[tool_class.name] = tool_class

    def get(self, name: str):
        """
        Return an instance of the tool with the given name.

        Parameters
        ----------
        name : str
            The tool's name attribute.

        Returns
        -------
        BaseTool instance

        Raises
        ------
        ToolNotFoundException
            If no tool with that name is registered.
        """

        tool_class = self._tools.get(name)

        if tool_class is None:
            raise ToolNotFoundException(
                f"No tool registered with name '{name}'. "
                f"Available tools: {self.list_names()}"
            )

        return tool_class()

    def list_names(self) -> list:
        """
        Returns a list of all registered tool names.
        Used by the planner to enumerate available tools.
        """
        return list(self._tools.keys())

    def list_for_llm(self) -> list:
        """
        Returns a list of dicts describing all tools.
        Used to build the system prompt so the LLM
        knows what tools it can choose from.

        Example output:
        [
            {
                "name": "employee_summary",
                "description": "Returns employee count and status."
            },
            ...
        ]
        """
        return [
            {
                "name":        name,
                "description": cls.description,
            }
            for name, cls in self._tools.items()
        ]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self._tools)} tools>"


# ==========================================================
# GLOBAL REGISTRY INSTANCE
# ==========================================================

# This is the single registry instance used across the app.
# Import this in tools/__init__.py to register all tools.

registry = ToolRegistry()