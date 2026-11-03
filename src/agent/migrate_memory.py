"""Copy long-term memories between user namespaces, e.g. after changing MEMORY_USER_ID."""

import argparse
import logging

from hy_memory import HyMemoryClient

from constants.agent_constants import MEMORY_MODE, MEMORY_USER_ID

logging.getLogger("hy_memory").setLevel(logging.WARNING)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", help="user ID to copy memories from")
    parser.add_argument(
        "dst",
        nargs="?",
        default=MEMORY_USER_ID,
        help=f"destination user ID (default: current MEMORY_USER_ID, {MEMORY_USER_ID!r})",
    )
    args = parser.parse_args()

    result = HyMemoryClient(mode=MEMORY_MODE).clone_user(args.src, args.dst)
    if result.get("success"):
        print(f"Copied {result.get('cloned_count', 0)} memories from {args.src!r} to {args.dst!r}.")
    else:
        raise SystemExit(f"Migration failed: {result.get('error_message', result)}")


if __name__ == "__main__":
    main()
