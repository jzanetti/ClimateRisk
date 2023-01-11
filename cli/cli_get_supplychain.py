"""
Usage: get_supplychain
            --workdir /tmp/climaterisk_data
            --cfg etc/cfg/nz_state_highway_impact.yaml

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

"""

import argparse
from process.supplychain import get_supplychain, calculate_direct_impact
from process.impact import get_impact
from process.exposure import get_from_litpop
from climada.entity import Exposures
from process.utils import gdf2centroids, read_cfg
from process.hazard import get_hazard
from process.exposure import update_exposure

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
        [
            "--workdir", "/tmp/climaterisk",
            "--cfg", "etc/cfg/nz_supplychain.yaml"
        ]
    )


def get_data():
    args = setup_parser()
    cfg = read_cfg(args.cfg)

    print("Get exposures ...")
    all_exps = []
    for proc_country in cfg["input"]["countries"]:
        all_exps.append(get_from_litpop(country=proc_country))
    exp = Exposures.concat(all_exps)

    print("Obtain impact based on hazard...")
    impacts = get_impact({"TC": {"enable": True}})

    print("Get supply chain data ...")
    supplychain = get_supplychain(cfg["input"])

    print("Get hazard (TC) ...")
    hazards = get_hazard(
        {"TC": {"enable": True}}, 
        None, 
        task_type="supplychain",
        tc_data_cfg={
            "cyclone": {
                "countries": ["New Zealand", "Japan", "Australia", "China"],
                "year_range": "2010-2011", # # 2010-2012 or None
                "pert_tracks": 1
            }}
    )

    print("Update exposure ...")
    updated_exp = update_exposure(
        {"hist": exp}, 
        impacts, 
        hazards,
        task_type="supplychain")

    print("Calculating direct impact ...")
    calculate_direct_impact(supplychain, updated_exp["TC"]["updated_hazard"], updated_exp["TC"]["exposure"], updated_exp["TC"]["impact"])

    """
    from climada.hazard import TropCyclone
    centr = gdf2centroids(tc_hazard.gdf)
    tc_cyclone = TropCyclone.from_tracks(tracks=tc_hazard, centroids=centr)
    tc_cyclone.plot_intensity(event=0)
    import matplotlib.pyplot as plt
    plt.savefig("test.png")
    plt.close()
    """
    raise Exception("!23123")

    print("Get exposures ...")
    all_exps = []
    for proc_country in cfg["input"]["countries"]:
        all_exps.append(get_from_litpop(country=proc_country))
    exps = Exposures.concat(all_exps)
    #exps.plot_hexbin(pop_name=False)

    #import matplotlib.pyplot as plt
    #plt.savefig("test.png")
    #plt.close()



    # supply_chain_data = get_supplychain(cfg["input"])




if __name__ == "__main__":
    get_data()
