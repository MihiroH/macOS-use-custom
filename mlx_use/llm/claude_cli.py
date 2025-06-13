"""
Claude CLI integration for mlx-use

This module provides a LangChain-compatible wrapper for the Claude Code CLI,
allowing mlx-use to use Claude CLI instead of API-based LLM providers.
"""

import asyncio
import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Union

from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ClaudeCLI(BaseChatModel):
    """
    LangChain-compatible wrapper for Claude Code CLI.

    This class implements the BaseChatModel interface to integrate Claude CLI
    with the existing mlx-use Agent system.
    """

    claude_command: str = Field(
        default_factory=lambda: os.getenv("CLAUDE_CLI_COMMAND", "claude"),
        description="Claude CLI command"
    )
    timeout: int = Field(
        default_factory=lambda: int(os.getenv("CLAUDE_CLI_TIMEOUT", "300")),
        description="Timeout for Claude CLI calls in seconds"
    )

    class Config:
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "claude_cli"

    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert LangChain messages to a single prompt string for Claude CLI.

        Args:
            messages: List of LangChain messages

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for message in messages:
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}")
            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                if message.tool_calls:
                    # Handle tool calls - convert to text representation
                    tool_calls_text = []
                    for tool_call in message.tool_calls:
                        tool_calls_text.append(f"Tool Call: {tool_call['name']} with args: {json.dumps(tool_call['args'])}")
                    prompt_parts.append(f"Assistant: {message.content}\n{chr(10).join(tool_calls_text)}")
                else:
                    prompt_parts.append(f"Assistant: {message.content}")
            elif isinstance(message, ToolMessage):
                prompt_parts.append(f"Tool Result: {message.content}")

        return "\n\n".join(prompt_parts)

    def _call_claude_cli(self, prompt: str, input_data: Optional[str] = None) -> str:
        """
        Call Claude CLI with the given prompt.

        Args:
            prompt: The prompt to send to Claude
            input_data: Optional data to pipe to Claude CLI

        Returns:
            Claude's response

        Raises:
            Exception: If Claude CLI call fails
        """
        try:
            cmd = [self.claude_command, "-p", prompt]

            if input_data:
                # Use pipe input
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                stdout, stderr = process.communicate(input=input_data, timeout=self.timeout)
            else:
                # Direct command execution
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=self.timeout
                )
                stdout = result.stdout
                stderr = result.stderr
                process = result

            if process.returncode != 0:
                error_msg = f"Claude CLI failed with return code {process.returncode}: {stderr.strip()}"
                logger.error(error_msg)
                raise Exception(error_msg)

            response = stdout.strip()
            if not response:
                logger.warning("Claude CLI returned empty response")
                return "I apologize, but I couldn't generate a response. Please try again."

            return response

        except subprocess.TimeoutExpired:
            error_msg = f"Claude CLI call timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to call Claude CLI: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate response using Claude CLI (synchronous).

        Args:
            messages: List of input messages
            stop: Stop sequences (not used with Claude CLI)
            run_manager: Callback manager
            **kwargs: Additional arguments

        Returns:
            ChatResult with Claude's response
        """
        prompt = self._messages_to_prompt(messages)
        logger.debug(f"Sending prompt to Claude CLI: {prompt[:200]}...")

        response = self._call_claude_cli(prompt)

        message = AIMessage(content=response)
        generation = ChatGeneration(message=message)

        return ChatResult(generations=[generation])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        Generate response using Claude CLI (asynchronous).

        Args:
            messages: List of input messages
            stop: Stop sequences (not used with Claude CLI)
            run_manager: Async callback manager
            **kwargs: Additional arguments

        Returns:
            ChatResult with Claude's response
        """
        # Run the synchronous call in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._generate,
            messages,
            stop,
            None,  # run_manager not supported in executor
            **kwargs
        )
        return result

    def with_structured_output(
        self,
        schema: Union[Dict, type, BaseModel],
        *,
        include_raw: bool = False,
        method: str = "function_calling",
        **kwargs: Any,
    ) -> "ClaudeStructuredOutput":
        """
        Create a structured output version of this model.

        This is required for compatibility with the Agent system which uses
        structured output for action generation.

        Args:
            schema: The schema for structured output
            include_raw: Whether to include raw response
            method: Method for structured output (ignored for Claude CLI)
            **kwargs: Additional arguments

        Returns:
            ClaudeStructuredOutput instance
        """
        return ClaudeStructuredOutput(
            llm=self,
            schema=schema,
            include_raw=include_raw,
            **kwargs
        )


class ClaudeStructuredOutput:
    """
    Structured output wrapper for Claude CLI.

    This class handles the conversion between Claude CLI's text output
    and the structured output format expected by the Agent system.
    """

    def __init__(
        self,
        llm: ClaudeCLI,
        schema: Union[Dict, type, BaseModel],
        include_raw: bool = False,
        **kwargs: Any,
    ):
        self.llm = llm
        self.schema = schema
        self.include_raw = include_raw
        self.kwargs = kwargs

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's response to extract structured data.

        Args:
            response: Raw response from Claude CLI

        Returns:
            Dictionary with parsed data
        """
        try:
            # Try to find JSON in the response
            import re

            # Look for JSON blocks
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, response, re.DOTALL)

            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            # Try to parse the entire response as JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass

            # If no JSON found, create a basic structure
            # This is a fallback - in practice, we'll need to prompt Claude
            # to return properly formatted JSON
            logger.warning(f"Could not parse structured response from Claude CLI: {response[:200]}...")

            # Return a basic structure that matches AgentOutput
            return {
                "current_state": {
                    "evaluation_previous_goal": "Could not parse previous evaluation",
                    "memory": "",
                    "next_goal": "Parse Claude response and continue"
                },
                "action": []
            }

        except Exception as e:
            logger.error(f"Error parsing structured response: {e}")
            # Return minimal valid structure
            return {
                "current_state": {
                    "evaluation_previous_goal": f"Error parsing response: {str(e)}",
                    "memory": "",
                    "next_goal": "Retry with better formatting"
                },
                "action": []
            }

    async def ainvoke(self, messages: List[BaseMessage], **kwargs: Any) -> Dict[str, Any]:
        """
        Asynchronously invoke Claude CLI with structured output.

        Args:
            messages: Input messages
            **kwargs: Additional arguments

        Returns:
            Dictionary with parsed and raw response
        """
        # Create a comprehensive structured instruction
        structured_instruction = """

IMPORTANT: You must respond with a valid JSON object that follows this exact structure:

{
  "current_state": {
    "evaluation_previous_goal": "Evaluate the success or failure of the previous action. Be specific about what worked or didn't work.",
    "memory": "Key information to remember for future actions. Include important context, errors, or successful patterns.",
    "next_goal": "Clearly state what you plan to do next to accomplish the task."
  },
  "action": [
    {
      "action_name": {
        "parameter1": "value1",
        "parameter2": "value2"
      }
    }
  ]
}

Available actions include:
- done: {"text": "completion message"} - Use when task is complete
- click_element: {"index": number, "action": "click"} - Click on UI element
- input_text: {"index": number, "text": "text to type", "submit": true/false} - Type text
- open_app: {"app_name": "Application Name"} - Open an application
- right_click_element: {"index": number} - Right click on element
- scroll_element: {"index": number, "direction": "up/down"} - Scroll element
- apple_script: {"script": "AppleScript code"} - Execute AppleScript

Your response must be ONLY the JSON object, no additional text or explanation.
"""

        # Create a copy of messages to avoid modifying the original
        modified_messages = messages.copy()

        # Add the structured instruction to the last message or create a new one
        if modified_messages and isinstance(modified_messages[-1], HumanMessage):
            modified_messages[-1] = HumanMessage(
                content=modified_messages[-1].content + structured_instruction
            )
        else:
            modified_messages.append(HumanMessage(content=structured_instruction))

        # Get response from Claude CLI
        chat_result = await self.llm._agenerate(modified_messages, **kwargs)
        raw_response = chat_result.generations[0].message.content

        # Parse the structured response
        parsed_response = self._parse_structured_response(raw_response)

        # Validate against schema if it's a Pydantic model
        if hasattr(self.schema, 'model_validate'):
            try:
                validated = self.schema.model_validate(parsed_response)
                parsed_response = validated
            except Exception as e:
                logger.error(f"Schema validation failed: {e}")
                logger.debug(f"Raw response: {raw_response}")
                logger.debug(f"Parsed response: {parsed_response}")
                # Keep the parsed response even if validation fails

        result = {"parsed": parsed_response}
        if self.include_raw:
            result["raw"] = chat_result

        return result

    def invoke(self, messages: List[BaseMessage], **kwargs: Any) -> Dict[str, Any]:
        """
        Synchronously invoke Claude CLI with structured output.

        Args:
            messages: Input messages
            **kwargs: Additional arguments

        Returns:
            Dictionary with parsed and raw response
        """
        # Run async version in sync context
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.ainvoke(messages, **kwargs))
