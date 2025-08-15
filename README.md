# triagent

Minimal CrewAI-based "triage router" agent that reads a natural-language rule and decides which tools to invoke (and in what order) to complete the instruction.

## Tools

- **restclient** (`restclient(url, method="GET", input_data=None) -> str`)
  - Call HTTP APIs. Returns response text or an error string.
- **logmatcher** (`logmatcher(pattern, filename) -> str(JSON)`)
  - Search for a regex or literal pattern in a file. Returns JSON with `found`, `count`, `first_match`, `error?`.
- **cmdprompt** (`cmdprompt(command, args_json=None, search_path=None) -> str(JSON)`)
  - Execute a shell command. Returns JSON with `success`, `returncode`, `stdout`, `stderr`, `executable`.

## Project layout

- `triage_agent.py` — tools and the CrewAI agent (`run(rule: str) -> str`).
- `main.py` — CLI entrypoint to pass a rule dynamically.
- `pyproject.toml` — dependencies (`crewai`, `requests`).

## Setup

```bash
# using uv or pip (choose one)
uv pip install -e .  # recommended if you use uv
# or
python -m pip install -e .
```

Note: CrewAI has several transitive dependencies; installation may take a while.

## Usage

```bash
# as an argument
python main.py "issue a GET to https://httpbin.org/uuid and print the uuid"

# via stdin
echo "issue a GET to https://httpbin.org/uuid and use the return value to run a shell echo command" | python main.py
```

The agent will decide which tool(s) to use (e.g., `restclient` then `cmdprompt`) and print a concise final result.

## Example rules

- "Issue a GET to https://httpbin.org/uuid and print the UUID"
- "Check if the file app.log contains 'ERROR connection failed'"
- "Run `ls -l /tmp` and return whether the command succeeded"

## Programmatic use

```python
from triage_agent import run

result = run("issue a GET to https://httpbin.org/uuid and then echo it")
print(result)