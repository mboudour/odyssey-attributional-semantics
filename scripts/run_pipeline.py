#!/usr/bin/env python3
"""Run the complete Odyssey attributional-semantics pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from odyssey_attr.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifest = run(args.root)
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
