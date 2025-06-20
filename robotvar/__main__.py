"""RoboTvar - Font merger for Roboto and TossFace fonts.

This module provides command-line interface for the RoboTvar font creation process.
"""

import argparse
import sys
from pathlib import Path
import traceback

def parse_args():
    parser = argparse.ArgumentParser(
        description="Create RoboTvar fonts by merging Roboto with TossFace or Twemoji emoji fonts"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--download-only",
        action="store_true",
        help="Only download the required fonts without merging",
    )
    group.add_argument(
        "--merge-only",
        action="store_true",
        help="Only merge existing fonts without downloading (default: TossFace emoji merge)",
    )
    group.add_argument(
        "--merge-twemoji",
        action="store_true",
        help="Merge Roboto with Twemoji emoji font instead of TossFace",
    )
    group.add_argument(
        "--test-app",
        action="store_true",
        help="Run Kivy test application to preview the fonts",
    )
    group.add_argument(
        "--compare-fonts",
        action="store_true",
        help="Compare character sets between two fonts",
    )
    group.add_argument(
        "--delete",
        action="store_true",
        help="Delete the merged folder and exit",
    )
    group.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete all font folders in the fonts directory and exit",
    )
    parser.add_argument(
        "--font1",
        type=Path,
        help="First font file for comparison",
    )
    parser.add_argument(
        "--font2",
        type=Path,
        help="Second font file for comparison",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Custom output directory for merged fonts",
        default=Path(__file__).parent / "merged",
    )
    parser.add_argument(
        "--showcase",
        action="store_true",
        help="Showcase DejaVu fonts in the test app",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Handle delete/reset actions first
    if args.delete or args.delete_all:
        from .scripts.reset import delete_merged_folder, delete_all_fonts, delete_screenshots_folder_content
        if args.delete:
            merged_dir = args.output_dir
            delete_merged_folder(merged_dir)
        if args.delete_all:
            fonts_dir = Path(__file__).parent / "fonts"
            screenshots_folder = Path(__file__).parent / "screenshots"
            delete_screenshots_folder_content(screenshots_folder)
            delete_merged_folder(args.output_dir)
            delete_all_fonts(fonts_dir)
        return

    # --showcase only valid with --merge-twemoji
    if args.showcase and not args.merge_twemoji:
        print(
            "Error: --showcase can only be used together with --merge-twemoji.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.compare_fonts:
        if not args.font1 or not args.font2:
            print(
                "Error: Both --font1 and --font2 must be specified with --compare-fonts",
                file=sys.stderr,
            )
            sys.exit(1)
        from .scripts.compare_sources import compare_fonts

        compare_fonts(args.font1, args.font2)
        return

    try:
        if args.test_app:
            from .scripts.test_app import run_test_app

            run_test_app(font_dir=args.output_dir)
        else:
            if not args.merge_only and not args.merge_twemoji:
                from .scripts.download import download_fonts
                download_fonts()

            if not args.download_only:
                if args.merge_twemoji:
                    from .scripts.merge_dejavu_and_twemoji import merge_all_fonts as merge_twemoji_fonts
                    merge_twemoji_fonts(showcase=args.showcase, output_dir=args.output_dir)
                else:
                    from .scripts.merge import merge_all_fonts as merge_tossface_fonts
                    merge_tossface_fonts(output_dir=args.output_dir)

    except Exception as e:
        print("Error occurred:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()