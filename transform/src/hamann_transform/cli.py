from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import MODEL_ID, Transnormer
from .xml_transform import transform_xml


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize historical German text while preserving XML markup."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--alignment-report", type=Path)
    parser.add_argument("--letters", help="Comma-separated letterText IDs")
    parser.add_argument("--model", default=MODEL_ID)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-beams", type=int, default=4)
    parser.add_argument("--no-progress", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    if args.input.resolve() == args.output.resolve():
        raise SystemExit("Input and output must differ; review the generated XML first.")
    letters = set(args.letters.split(",")) if args.letters else None
    normalizer = Transnormer(
        model_id=args.model,
        device=args.device,
        batch_size=args.batch_size,
        num_beams=args.num_beams,
        show_progress=not args.no_progress,
    )
    summary = transform_xml(
        args.input,
        args.output,
        normalizer,
        report_path=args.alignment_report,
        letters=letters,
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
