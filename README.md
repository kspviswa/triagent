# triagent

Minimal CrewAI-based "triage router" agent that reads a natural-language rule and decides which tools to invoke (and in what order) to complete the instruction.

## Dummy Tools

- **restclient** (`restclient(url, method="GET", input_data=None) -> str`)
  - Call HTTP APIs. Returns response text or an error string.
- **logmatcher** (`logmatcher(pattern, filename) -> str(JSON)`)
  - Search for a regex or literal pattern in a file. Returns JSON with `found`, `count`, `first_match`, `error?`.
- **cmdprompt** (`cmdprompt(command, args_json=None, search_path=None) -> str(JSON)`)
  - Execute a shell command. Returns JSON with `success`, `returncode`, `stdout`, `stderr`, `executable`.

## Project layout

- `triage_agent.py` — tools and the CrewAI agent (`run(rule: str) -> str`).
- `pyproject.toml` — dependencies (`crewai`, `requests`).