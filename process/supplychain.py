from pickle import load as pickle_load
from climada_petals.engine import SupplyChain

def get_supplychain(cfg_input: dict):
    """Get Supply chain data

    Args:
        cfg_input (dict): input configuration

    Returns:
        _type_: _description_
    """
    return pickle_load(open(cfg_input["file"], "rb"))


def calculate_direct_impact(supplychain, hazard, exp, impact_func):

    # selected_subsec_list = ["service", "manufacturing", "agriculture", "mining"]
    selected_subsec_list = "manufacturing"
    supplychain.calc_sector_direct_impact(hazard, exp, impact_func, selected_subsec=selected_subsec_list)
    from pandas import DataFrame
    from numpy import vstack
    from tabulate import tabulate
    df_imp = DataFrame(data=vstack(
        [   
            supplychain.direct_aai_agg[supplychain.reg_pos['AUS']],
            supplychain.direct_aai_agg[supplychain.reg_pos['CHN']]
        ]),
        columns=supplychain.sectors,
        index=['AUS', 'CHN'])

    # x = tabulate(df_imp, headers='keys', tablefmt='psql')
    df_imp.to_csv("test.csv", index=False)

    raise Exception("!23")





