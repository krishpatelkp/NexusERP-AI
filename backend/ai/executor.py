"""
==========================================================
NexusERP-AI — Executor
==========================================================

The Executor runs the tools selected by the Planner.

Responsibilities:
    - Receive a list of tool names
    - Look each up in the registry
    - Run each tool with the given context
    - Collect and return all results

The Executor does NOT:
    - Decide which tools to run (that is Planner)
    - Build the final response (that is AIService)
    - Talk to the LLM
==========================================================
"""

from ai.tools.base import ToolContext, ToolResult
from ai.exceptions import ToolNotFoundException


class Executor:
    """
    Runs a list of tools and collects their results.

    Parameters
    ----------
    registry : ToolRegistry
    """

    def __init__(self, registry):
        self.registry = registry

    def execute(
        self,
        tool_names: list,
        context: ToolContext,
        tool_kwargs: dict = None,
    ) -> list:
        """
        Run each tool in order and return all results.

        Parameters
        ----------
        tool_names : list of str
            Ordered list from the Planner.

        context : ToolContext
            Company, user, and metadata.

        tool_kwargs : dict, optional
            Per-tool keyword arguments.
            Example: {"employee_register": {"limit": 5}}

        Returns
        -------
        list of ToolResult
            One result per tool, in execution order.
            Failed tools return ToolResult(success=False)
            and do not stop subsequent tools from running.
        """

        if tool_kwargs is None:
            tool_kwargs = {}

        results = []

        for name in tool_names:

            if name not in self.registry:
                results.append(
                    ToolResult(
                        success=False,
                        tool=name,
                        error=f"Tool '{name}' is not registered.",
                    )
                )
                continue

            tool = self.registry.get(name)
            kwargs = tool_kwargs.get(name, {})
            result = tool.run(context, **kwargs)
            results.append(result)

        return results