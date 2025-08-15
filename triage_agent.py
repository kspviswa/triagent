from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional

import requests
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, LLM
try:
    # Preferred in newer setups
    from crewai_tools import tool  # type: ignore
except Exception:  # pragma: no cover - fallback for older versions
    from crewai.tools import tool  # type: ignore


# Load environment from .env if present
load_dotenv()

# -----------------------------
# Tool Implementations
# -----------------------------

@tool("restclient")
def restclient(url: str, method: str = "GET", input_data: str | None = None) -> str:
    """
    Call a remote HTTP REST API.

    Use this when you need to fetch or send data over HTTP.
    - url: Full URL to call. Example: https://api.example.com/random
    - method: HTTP method: GET, POST, PUT, PATCH, DELETE
    - input_data: Optional request body as a string (for non-GET methods). If JSON is required, pass a valid JSON string.

    DUMMY IMPLEMENTATION: Does not perform any network I/O. Returns a JSON string echoing inputs to trace routing.
    """
    return json.dumps({
        "tool": "restclient",
        "called": True,
        "url": url,
        "method": method,
        "input_data": input_data,
        "note": "dummy",
    })


@tool("logmatcher")
def logmatcher(pattern: str, filename: str) -> str:
    """
    Search for a pattern in a log file to check if a log line exists.

    Use this when you need to confirm if a particular text or regex occurs in a file.
    - pattern: Regex or plain text to search for. Example: ERROR .* connection failed
    - filename: Path to the log file to search. Example: /var/log/app.log

    DUMMY IMPLEMENTATION: Does not read files. Returns a JSON string echoing inputs to trace routing.
    """
    return json.dumps({
        "tool": "logmatcher",
        "called": True,
        "pattern": pattern,
        "filename": filename,
        "note": "dummy",
    })


@tool("cmdprompt")
def cmdprompt(command: str, args_json: str | None = None, search_path: str | None = None) -> str:
    """
    Execute a shell command and return its output and status.

    Use this for tasks that require interacting with the local shell/CLI.
    - command: The command or executable to run. Example: ls, grep, python
    - args_json: Optional JSON array of arguments, e.g. "[\"-l\", \"/tmp\"]"
    - search_path: Optional directory to search first for the executable. If not found, falls back to system PATH.

    DUMMY IMPLEMENTATION: Does not execute any command. Returns a JSON string echoing inputs to trace routing.
    """
    return json.dumps({
        "tool": "cmdprompt",
        "called": True,
        "command": command,
        "args_json": args_json,
        "search_path": search_path,
        "note": "dummy",
    })


# -----------------------------
# Triage Agent and Runner
# -----------------------------

TRIAGE_TASK_DESCRIPTION = (
    """
You are a general-purpose routing triage agent.

Your job:
- Read the user's RULE.
- Select from the AVAILABLE TOOLS based solely on each tool's description.
- Decide the correct order of calls. You may call multiple tools and chain outputs from earlier calls into later calls when needed.
- Construct inputs carefully to match each tool's signature and expectations (e.g., JSON vs string), based on the tool's description only.
- Produce a concise final answer that states the steps you took, the tools you used, and the final result.

IMPORTANT:
- Do not assume any domain-specific behavior beyond tool descriptions.
- If a step is ambiguous, make a best-effort reasonable assumption and proceed.

RULE:
{rule}
    """
).strip()


def get_perplexity_llm() -> LLM:
    """Create a Perplexity Sonar LLM config for CrewAI.

    Reads API key from env var PPLX_API_KEY or PERPLEXITY_API_KEY.
    """
    api_key = os.getenv("PPLX_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
    return LLM(model="sonar", base_url="https://api.perplexity.ai/", api_key=api_key)


def build_triage_agent(tools: Optional[List] = None, llm: Optional[LLM] = None) -> Agent:
    return Agent(
        role="Triage Router Agent",
        goal=(
            "Understand RULES and route work by selecting and sequencing tools strictly by their descriptions to achieve the requested outcome."
        ),
        backstory=(
            "You are a pragmatic, tool-agnostic operator. You read instructions, pick suitable tools based on their descriptions, "
            "and chain their outputs to complete multi-step tasks."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm or get_perplexity_llm(),
        tools=tools or [restclient, logmatcher, cmdprompt],
    )


@dataclass
class TriageAgentRunner:
    agent: Agent

    def run(self, rule: str) -> str:
        rule = (rule or "").strip()
        if not rule:
            raise ValueError("RULE is empty; please provide a non-empty instruction.")

        task = Task(
            description=TRIAGE_TASK_DESCRIPTION.format(rule=rule),
            expected_output=(
                "A short explanation of the steps taken, tool calls used (in order), and the final result."
            ),
            agent=self.agent,
        )
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
        )
        result = crew.kickoff()
        return str(result)


def run(rule: str, tools: Optional[List] = None, llm: Optional[LLM] = None) -> str:
    """Run the triage agent with a RULE string and an optional list of tools.

    Pass `tools` to extend/override available tools without modifying the agent code.
    """
    runner = TriageAgentRunner(agent=build_triage_agent(tools=tools, llm=llm))
    return runner.run(rule)


def default_tools() -> List:
    """Return the default tool set. Extend or modify by passing `tools` to run()."""
    return [restclient, logmatcher, cmdprompt]


# -----------------------------
# Demo runner
# -----------------------------

def main() -> None:
    """Run a set of sample RULE prompts to demonstrate routing and sequencing."""
    samples: List[str] = [
        # Single-tool: HTTP fetch
        "Issue a GET to https://httpbin.org/uuid and return the body",
        # Chained: HTTP -> shell
        "Issue a GET to https://httpbin.org/uuid and then echo the returned value using a shell command",
        # Log search
        "Check if the file /var/log/app.log contains the pattern ERROR .* connection failed",
        # Command-only
        "Run ls -l /tmp and return whether it succeeded and print the output",
    ]

    print("=== Triage Agent Demo ===")
    for i, rule in enumerate(samples, start=1):
        print(f"\n--- Sample {i} ---")
        print(f"RULE: {rule}")
        try:
            result = run(rule)
        except Exception as e:
            result = f"ERROR: {e}"
        print("RESULT:\n" + str(result))


if __name__ == "__main__":
    main()
