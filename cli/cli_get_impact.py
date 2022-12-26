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
from process.exposure import get_exposure, update_exposure
from process.hazard import get_hazard
from process.impact import get_impact, calculate_impact_func
from os.path import exists, join
from os import makedirs
from process.utils import read_cfg
from process.vis import plot_wrapper

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

    parser.add_argument(
        "--cfg",
        required=True,
        help="the path of configuration file")

    return parser.parse_args(
        [
            "--workdir", "/tmp/climaterisk",
            "--cfg", "etc/cfg/nz_state_highway.yaml"
        ]
    )


def get_data():
    args = setup_parser()

    cfg = read_cfg(args.cfg)

    workdir = join(args.workdir, cfg["name"])

    if not exists(workdir):
        makedirs(workdir)

    print("Get exposures ...")
    exp_obj = get_exposure(cfg["input"])

    print("Get hazard ...")
    hazards = get_hazard(cfg["hazard"]) 

    print("Obtain impact based on hazard...")
    impacts = get_impact(cfg["hazard"])

    print("Combining exposure, impact and hazard ...")
    exp_objs = update_exposure(cfg, exp_obj, impacts, hazards)

    print("Calculating impacts ...")
    exp_objs = calculate_impact_func(exp_objs)

    print("Visualization ...")
    plot_wrapper(cfg, workdir, exp_objs)

if __name__ == "__main__":
    get_data()
