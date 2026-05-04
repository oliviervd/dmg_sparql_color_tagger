from src.utils.parsers import parse_colors, fetch_objects_needing_colors, test_one_object
import logging
import argparse
import json
import os
from typing import Optional


PROGRESS_FILE = "color_progress.json"

def save_progress(object_number: str):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_processed": object_number}, f)

def load_progress() -> Optional[str]:
    if not os.path.exists(PROGRESS_FILE):
        return None
    try:
        with open(PROGRESS_FILE) as f:
            return json.load(f).get("last_processed")
    except Exception:
        return None

def clear_progress():
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        logging.info("Progress file cleared")

def main(
    run_parse_colors: bool = False,
    force_reprocess: bool = False,
    batch_size: Optional[int] = None,
    resume: bool = False
):
    try:
        if run_parse_colors:
            logging.info("Fetching objects that need color extraction...")
            _objects = fetch_objects_needing_colors(force_reprocess=force_reprocess)
            logging.info(f"Total objects queued: {len(_objects)}")

            # resume from last processed object
            if resume:
                last = load_progress()
                if last and last in _objects:
                    start_index = _objects.index(last) + 1
                    logging.info(f"Resuming from {last} — skipping {start_index} already processed objects")
                    _objects = _objects[start_index:]
                else:
                    logging.info("No valid resume point found — starting from beginning")

            # apply batch size
            if batch_size:
                logging.info(f"Processing batch of {batch_size} objects")
                _objects = _objects[:batch_size]

            logging.info(f"Parsing colors for {len(_objects)} objects...")

            # wrap parse_colors to save progress after each object
            for idx, object_number in enumerate(_objects, start=1):
                logging.info(f"[{idx}/{len(_objects)}] Processing {object_number}")
                try:
                    parse_colors([object_number], force_reprocess=force_reprocess)
                    save_progress(object_number)
                except Exception as e:
                    logging.error(f"Failed on {object_number}: {e}")
                    continue

            logging.info("Batch complete")

    except Exception as e:
        logging.error(f"Failed to run: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="DMG color tagger")
    parser.add_argument("--colors", action="store_true", help="Extract colors")
    parser.add_argument("--force", action="store_true", help="Reprocess all objects even if colors already exist")
    parser.add_argument("--batch", type=int, default=None, help="Only process this many objects then stop")
    parser.add_argument("--resume", action="store_true", help="Resume from last processed object")
    parser.add_argument("--clear-progress", action="store_true", help="Clear saved progress and start fresh")
    parser.add_argument("--test", type=str, default=None, help="Test a single object number")
    args = parser.parse_args()

    if args.test:
        test_one_object(args.test)

    elif args.clear_progress:
        clear_progress()

    else:
        run_colors = args.colors or (not args.colors)

        main(
            run_parse_colors=run_colors,
            force_reprocess=args.force,
            batch_size=args.batch,
            resume=args.resume or args.force  # ← auto-resume when force is set
        )
