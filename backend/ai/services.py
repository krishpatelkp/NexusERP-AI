"""
==========================================================
NexusERP-AI — AI Service
==========================================================

The main orchestrator for the AI module.

Flow:
    1. Receive question + context
    2. Planner selects tools
    3. Executor runs tools
    4. LLM generates natural language response (or tool output fallback)
    5. Return response
==========================================================
"""

import json

from ai.llm.ollama_client import OllamaClient
from ai.planner import Planner
from ai.executor import Executor
from ai.memory import ConversationMemory
from ai.prompts import SYSTEM_PROMPT, RESPONSE_PROMPT
from ai.tools.base import ToolContext
from ai.exceptions import AIException, LLMConnectionException


class AIService:
    """
    Main entry point for the AI module.

    Called by AIChatAPIView.
    Coordinates Planner, Executor, and LLM.
    """

    def __init__(self):
        from ai.tools import registry
        self.registry = registry
        self.client = OllamaClient()
        self.planner = Planner(self.client, self.registry)
        self.executor = Executor(self.registry)

    def _keyword_plan(self, question: str) -> list:
        """
        Fallback keyword tool selector when LLM is unreachable.
        """
        q = question.lower()
        tools = []
        if "absent" in q or "attendance" in q or "present" in q:
            tools.append("attendance_dashboard")
        elif "payroll" in q or "salary" in q or "payslip" in q or "cost" in q:
            tools.append("payroll_summary")
        elif "employee" in q or "staff" in q or "headcount" in q or "department" in q:
            tools.append("employee_summary")
        elif "leave" in q or "vacation" in q or "holiday" in q:
            tools.append("leave_summary")
        elif "asset" in q or "inventory" in q or "maintenance" in q:
            tools.append("inventory_summary")
        elif "payment" in q or "due" in q:
            tools.append("payment_summary")
        return tools

    def chat(
        self,
        question: str,
        company,
        user,
        conversation_history: list = None,
    ) -> dict:
        """
        Process a chat message and return the AI response.
        """

        context = ToolContext(
            company=company,
            user=user,
        )

        is_ollama_online = self.client.is_available()
        tool_names = []

        if is_ollama_online:
            try:
                tool_names = self.planner.plan(question)
            except Exception:
                tool_names = self._keyword_plan(question)
        else:
            tool_names = self._keyword_plan(question)

        # Off-topic / Unmapped guardrail
        if not tool_names:
            return {
                "response": (
                    "I am NexusERP AI, an enterprise assistant built exclusively for NexusERP. "
                    "I can only assist with enterprise operations such as Employees, Attendance, "
                    "Leave Management, Payroll, Inventory, Payments, and Company Reports."
                ),
                "tools_used":   [],
                "tool_results": [],
                "success":      True,
            }

        # Execute tools
        tool_results = []
        tools_used = []

        results = self.executor.execute(
            tool_names=tool_names,
            context=context,
        )

        for result in results:
            tools_used.append(result.tool)
            tool_results.append(result.to_dict())

        # Build natural language response
        if is_ollama_online:
            tool_results_text = json.dumps(
                tool_results,
                indent=2,
                default=str,
            )

            response_prompt = RESPONSE_PROMPT.format(
                question=question,
                tool_results=tool_results_text,
            )

            messages = [
                {
                    "role":    "system",
                    "content": SYSTEM_PROMPT,
                },
            ]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({
                "role":    "user",
                "content": response_prompt,
            })

            try:
                response_text = self.client.chat(
                    messages=messages,
                    temperature=0.3,
                )
                return {
                    "response":     response_text,
                    "tools_used":   tools_used,
                    "tool_results": tool_results,
                    "success":      True,
                }
            except Exception:
                pass

        # Fallback to direct tool result message if LLM formatting unavailable
        messages = [r.message for r in results if r.success and r.message]
        response_text = "\n\n".join(messages) if messages else "Execution completed."

        return {
            "response":     response_text,
            "tools_used":   tools_used,
            "tool_results": tool_results,
            "success":      True,
        }