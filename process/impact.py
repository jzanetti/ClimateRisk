from climada.entity import ImpactFuncSet, ImpfTropCyclone
from climada.entity.impact_funcs import impact_func_set
from climada.engine import Impact
from climada.engine.impact import Impact as Impact_type
from process.vis import plot_impact
from climada.util.lines_polys_handler import impact_pnt_agg, AggMethod
from geopandas import GeoDataFrame
from climada.entity import ImpactFunc
from numpy import linspace, sort, array
from climada_petals.entity.impact_funcs.river_flood import flood_imp_func_set

def get_impact(hazard_cfg: dict) -> dict:
    """Return an impact function

    Returns:
        climadarisj_cfg: Hazard configuration
    """

    impf_set = {}

    for proc_hazard_name in hazard_cfg:

        proc_hazard = hazard_cfg[proc_hazard_name]

        if not proc_hazard["enable"]:
            continue

        impf_set[proc_hazard_name] = ImpactFuncSet()

        if proc_hazard_name in ["TC_track", "TC_wind"]:
            proc_func = ImpfTropCyclone.from_emanuel_usa()

        elif proc_hazard_name == "landslide":
            proc_func = landslide_impact_func()

        elif proc_hazard_name == "flood":
            proc_func = flood_impact_func()

        else:
            raise Exception(f"Hazard type {proc_hazard_name} is not supported yet ...")

        impf_set[proc_hazard_name].append(proc_func)


    return impf_set


def flood_impact_func(oceania_func_id: int = 5) -> ImpactFunc:
    """Flood impact function

    Args:
        num (int, optional): _description_. Defaults to 15.

    Returns:
        _type_: _description_
    """
    impf_set = flood_imp_func_set()

    return impf_set.get_func(fun_id=oceania_func_id)[0]


def calculate_impact_func(exposure_objs: dict) -> Impact_type:
    """Calculate the impact function

    Args:
        exposure_obj (Exposures): _description_

    Returns:
        _type_: _description_
    """

    outputs = {}

    for hazard_name in exposure_objs:

        imp = Impact()

        proc_exposure_obj = exposure_objs[hazard_name]

        imp.calc(proc_exposure_obj["exposure"], proc_exposure_obj["impact"], proc_exposure_obj["updated_hazard"], save_mat=True)

        freq_curve = imp.calc_freq_curve()

        outputs[hazard_name] = {
            "imp": imp,
            "freq": freq_curve,
            "exposure": proc_exposure_obj["exposure"],
            "hazard": proc_exposure_obj["hazard"]
        }

    return outputs


def landslide_impact_func(num: int = 15) -> ImpactFunc:
    """Landslide impact function

    Args:
        num (int, optional): _description_. Defaults to 15.

    Returns:
        _type_: _description_
    """

    impf_LS_hist = ImpactFunc()
    impf_LS_hist.haz_type = "LS"
    impf_LS_hist.id = 1
    impf_LS_hist.name = "LS Linear function"
    impf_LS_hist.intensity_unit = "m/m"
    impf_LS_hist.intensity = linspace(0, 1, num=num)
    impf_LS_hist.mdd = sort(
        array([0, 0, 0, 0, 0, 0, 0, 0, 1., 1., 1., 1., 1., 1., 1.]))
    impf_LS_hist.paa = sort(linspace(1, 1, num=num))
    impf_LS_hist.check()
    
    return impf_LS_hist