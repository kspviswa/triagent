# Summary

## What we built
- **Triage router agent** using CrewAI (`triage_agent.py`) that reads a RULE and, based solely on tool descriptions, selects and sequences tools in the right order with the right inputs.
- **Dummy tools** to validate routing without side effects:
  - `restclient(url, method, input_data)`
  - `logmatcher(pattern, filename)`
  - `cmdprompt(command, args_json, search_path)`
  Each returns a small JSON echo to show invocations and arguments clearly.

## LLM & Config
- Uses **Perplexity Sonar** via CrewAI `LLM(model="sonar", base_url="https://api.perplexity.ai/")`.
- API key read from `.env` (`PPLX_API_KEY` or `PERPLEXITY_API_KEY`) using `python-dotenv` (`load_dotenv()`).

## How to run
- Demo with sample RULEs: `python triage_agent.py`
- Single RULE via CLI: `python main.py "<RULE TEXT>"`

## Extensibility
- Add new tools with `@tool` and pass them to `run(rule, tools=[...])` or `build_triage_agent(tools=[...])`.
- Agent remains **tool-agnostic**, routing purely by tool descriptions.

## Files touched
- `triage_agent.py`: agent, tools, Perplexity LLM, demo `main()`.
- `main.py`: CLI wrapper to run with a single RULE.
- `pyproject.toml`: deps (`crewai`, `requests`, `python-dotenv`).
- `README.md`: usage & examples.
