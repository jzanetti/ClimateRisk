"""
Usage: get_benefit
            --workdir /tmp/climaterisk_data
            --cfg etc/cfg/nz_state_highway_cost_benefit.yaml

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

"""

import argparse
from process.exposure import get_exposure, update_exposure
from process.hazard import get_hazard
from process.impact import get_impact
from process.adaptation import define_adaptation, set_discount_rates, calculate_cost_benefit
from os.path import exists, join
from os import makedirs
from process.utils import read_cfg
from process.vis import plot_cost_benefit_wrapper

def get_example_usage():
    example_text = """example:
        * get_benefit
            --workdir /tmp/climaterisk_data
            --cfg nz_state_highway_cost_benefit.yaml
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Cost-benefit calculation from ClimadaRisk",
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
            "--cfg", "etc/cfg/nz_state_highway_cost_benefit.yaml"
        ]
    )


def get_data():
    args = setup_parser()

    cfg = read_cfg(args.cfg)

    workdir = join(args.workdir, cfg["name"])

    if not exists(workdir):
        makedirs(workdir)

    print("Get exposures ...")
    exp_obj = get_exposure(cfg["input"], economy_growth=cfg["economy_annual_growth"], add_future=True)

    print("Get hazard ...")
    hazards = get_hazard(cfg["hazard"], future_hazard_para=cfg["future_hazard_para"], task_type="cost_benefit") 

    print("Obtain impact based on hazard...")
    impacts = get_impact(cfg["hazard"])

    print("Obtain adaptation ...")
    adaptations = define_adaptation(cfg["adaptation"], impacts)

    print("Obtain discount rates ...")
    discount_rates = set_discount_rates(exp_obj, cfg["adaptation"])

    print("Combining exposure, impact and hazard for both hist and future ...")
    for exp_flag in ["hist", "future"]:
        exp_obj[exp_flag] = update_exposure(
            exp_obj, impacts, hazards, exp_flag=exp_flag, task_type="cost_benefit")

    print("Calculating cost-benefit ...")
    cost_benefit_objs = calculate_cost_benefit(exp_obj, adaptations, discount_rates)

    print("Visualization ...")
    plot_cost_benefit_wrapper(cfg, workdir, exp_obj, cost_benefit_objs, discount_rates)


if __name__ == "__main__":
    get_data()
