from pickle import load as pickle_load
from pandas import DataFrame
from numpy import vstack
from process import RISK_COUNTRY
from os.path import join


def get_supplychain(supply_chain_inputdata: str):
    """Get Supply chain data

    Args:
        cfg_input (dict): input configuration

    Returns:
        _type_: _description_
    """
    return pickle_load(open(supply_chain_inputdata, "rb"))


def calculate_supplychain_impact(workdir: str, supplychain, hazard, exp, impact_func, fields: list) -> dict:
    """_summary_

    Args:
        supplychain (_type_): _description_
        hazard (_type_): _description_
        exp (_type_): _description_
        impact_func (_type_): _description_

    Raises:
        Exception: _description_
    """
    
    # country_to_be_assessed = RISK_COUNTRY
    country_to_be_assessed = "AUS"

    direct_impact = {}
    indirect_impact = {}

    for proc_field in fields:

        supplychain.calc_sector_direct_impact(hazard, exp, impact_func, selected_subsec=proc_field)
        supplychain.calc_indirect_impact(io_approach='ghosh')

        df_direct_impact = DataFrame(data=vstack(
            [   
                supplychain.direct_aai_agg[supplychain.reg_pos[country_to_be_assessed]]
            ]),
            columns=supplychain.sectors,
            index=[country_to_be_assessed])

        df_indirect_impact = DataFrame(data=vstack(
            [   
                supplychain.indirect_aai_agg[supplychain.reg_pos[country_to_be_assessed]]
            ]),
            columns=supplychain.sectors,
            index=[country_to_be_assessed])

        df_direct_impact.to_csv(join(workdir, f"direct_impact_{proc_field}.csv"), index=False)

        df_indirect_impact.to_csv(join(workdir, f"indirect_impact_{proc_field}.csv"), index=False)

        direct_impact[proc_field] = df_direct_impact
        indirect_impact[proc_field] = df_indirect_impact

    x = 3
    
    return {
        "direct": direct_impact,
        "indirect": indirect_impact
    }





