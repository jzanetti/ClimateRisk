"""
Usage: get_supplychain
            --workdir /tmp/climaterisk_data
            --cfg etc/cfg/nz_state_highway_impact.yaml

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

"""

import argparse
from process.supplychain import get_supplychain, calculate_supplychain_impact
from process.impact import get_impact
from process.exposure import get_from_litpop
from os.path import join, exists
from os import makedirs
from process.utils import read_cfg
from process.hazard import get_hazard
from process.exposure import update_exposure
from process import TC_DATA

def get_example_usage():
    example_text = """example:
        * get_supplychain
            --workdir /tmp/climaterisk_data
            --cfg nz_state_highway.yaml
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Supply chain impacts",
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
        # [
        #    "--workdir", "/tmp/climaterisk",
        #    "--cfg", "etc/cfg/nz_supplychain.yaml"
        # ]
    )


def get_data():
    args = setup_parser()

    cfg = read_cfg(args.cfg)

    workdir = join(args.workdir, cfg["name"])

    if not exists(workdir):
        makedirs(workdir)

    print("Get exposures ...")
    exp = get_from_litpop(country=cfg["input"]["countries"])

    print("Obtain impact based on hazard...")
    impacts = get_impact({"TC": {"enable": True}})

    print("Get supply chain data ...")
    supplychain = get_supplychain(cfg["input"]["file"])

    print("Get hazard (TC) ...")
    hazards = get_hazard(
        {"TC": {"enable": True}}, 
        None, 
        task_type="supplychain",
        tc_data_cfg=TC_DATA["track2"]
    )

    print("Update exposure ...")
    updated_exp = update_exposure(
        {"hist": exp}, 
        impacts, 
        hazards,
        task_type="supplychain")

    print("Calculating direct and indirect impact ...")
    calculate_supplychain_impact(
        workdir,
        supplychain, 
        updated_exp["TC"]["updated_hazard"], 
        updated_exp["TC"]["exposure"], 
        updated_exp["TC"]["impact"],
        fields = cfg["fields"]
        )




if __name__ == "__main__":
    get_data()
