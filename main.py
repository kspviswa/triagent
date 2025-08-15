import sys
from typing import Optional

from triage_agent import run as run_triage


def _read_rule_from_args() -> Optional[str]:
    # If a rule is passed as a single CLI arg, use it directly
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return None


def _read_rule_from_stdin() -> Optional[str]:
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        return data.strip() if data else None
    return None


def main():
    """Entry point: provide RULE as an argument or via stdin."""
    rule = _read_rule_from_args() or _read_rule_from_stdin()
    if not rule:
        print("Usage: python main.py '<RULE TEXT>'\n  or: echo '<RULE TEXT>' | python main.py")
        sys.exit(2)

    result = run_triage(rule)
    print(result)


if __name__ == "__main__":
    main()
