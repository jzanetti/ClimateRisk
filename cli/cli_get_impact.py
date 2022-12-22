"""
Usage: get_impact
            --workdir /tmp/climaterisk_data
            --job show

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

Debug:
    export PYTHONPATH=/Users/zhans/Github/ClimateRisk:$PYTHONPATH
"""

import argparse
from process.exposure import get_litpop
from process.hazard import get_tc
from process.impact import get_impact_func, calculate_impact_func
from os.path import exists
from os import makedirs

def get_example_usage():
    example_text = """example:
        * get_impact
            --workdir /tmp/climaterisk_data
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Impact calculation from ClimadaRisk",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir",
        required=True,
        help="working directory")

    return parser.parse_args(
        [
            "--workdir", "/tmp/climaterisk",
        ]
    )


def get_data():
    args = setup_parser()

    workdir = args.workdir

    if not exists(workdir):
        makedirs(workdir)

    impact_func = get_impact_func(["from_emanuel_usa"])

    litpop_obj = get_litpop(workdir, impact_func)

    tc_obj = get_tc(workdir, litpop_obj)

    impact = calculate_impact_func(workdir, litpop_obj, impact_func, tc_obj, vis_flag=True)

if __name__ == "__main__":
    get_data()
