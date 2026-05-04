from src.utils.parsers import parse_colors, add_media, fetch_objects_needing_colors, test_one_object
import logging
import argparse
from urllib.parse import quote


def main(run_update: bool = True, run_parse_colors: bool = False, force_reprocess: bool = False):
    try:
        if run_update:
            logging.info("Starting add_media() to fetch IIIF media URIs...")
            add_media(True)
        if run_parse_colors:
            logging.info("Fetching objects that need color extraction...")
            _objects = fetch_objects_needing_colors(force_reprocess=force_reprocess)
            logging.info(f"Parsing colors for {len(_objects)} objects...")
            parse_colors(_objects, force_reprocess=force_reprocess)
    except Exception as e:
        logging.error(f"Failed to run: {e}")


def update():
    add_media(True)


if __name__ == "__main__":
    test_one_object("1992-0113")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="DMG color tagger")
    parser.add_argument("--update", action="store_true", help="Fetch IIIF media URIs")
    parser.add_argument("--colors", action="store_true", help="Extract colors")
    parser.add_argument("--force", action="store_true", help="Reprocess all objects even if colors already exist")
    args = parser.parse_args()

    # default behaviour if no args given
    run_update = args.update or (not args.update and not args.colors)
    run_colors = args.colors or (not args.update and not args.colors)

    main(
        run_update=run_update,
        run_parse_colors=run_colors,
        force_reprocess=args.force
    )


