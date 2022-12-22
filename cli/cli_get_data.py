"""
Usage: get_data
            --workdir /tmp/climaterisk_data
            --job show

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

Debug:
    export PYTHONPATH=/Users/zhans/Github/ClimateRisk:$PYTHONPATH
"""

import argparse
from process import GET_DATA_JOBS
from process.get_data import show_data, download_data

def get_example_usage():
    example_text = """example:
        * get_data
            --workdir /tmp/climaterisk_data
            --job show
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Get build-in dataset from ClimadaRisk",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir",
        required=True,
        help="working directory")

    parser.add_argument(
        "--job",
        required=True,
        choices=GET_DATA_JOBS,
        help=f"Climada get_data job name, choices {GET_DATA_JOBS}")

    return parser.parse_args(
        [
               "--workdir", "/tmp/climaterisk",
              "--job", "download_litpop",
        ]
    )


def get_data():
    args = setup_parser()

    if args.job in ["show_all_jobs"]:
        show_data()

    elif args.job in ["download_litpop"]:
        download_data(args.job)

if __name__ == "__main__":
    get_data()
