from climada.entity import ImpactFuncSet, ImpfTropCyclone
from climada.entity.impact_funcs import impact_func_set
from climada.engine import Impact
from climada.hazard.tc_tracks import TCTracks as TCTracks_type
from climada.entity.exposures.base import Exposures
from climada.engine.impact import Impact as Impact_type
from process.vis import plot_impact

def get_impact_func(impact_func_types: list) -> impact_func_set:
    """Return an impact function

    Returns:
        impact_func_set: Impact function sets
    """

    impf_set = ImpactFuncSet()

    for proc_impact_func in impact_func_types:
        if proc_impact_func == "from_emanuel_usa":
            impf_set.append(ImpfTropCyclone.from_emanuel_usa())
        else:
            raise Exception("not supported yet ...")

    return impf_set


def calculate_impact_func(
    workdir: str, exposure_obj: Exposures, impact_func: impact_func_set, hazard_obj, vis_flag: bool = True) -> Impact_type:
    """Calculate the impact function

    Args:
        exposure_obj (Exposures): _description_
        impact_func (impact_func_set): _description_
        hazard_obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    imp = Impact()
    imp.calc(exposure_obj, impact_func, hazard_obj, save_mat=False)
    print(f"Aggregated average annual impact: {round(imp.aai_agg,0)} $")
    
    if vis_flag:
        plot_impact(workdir, imp)

    return imp