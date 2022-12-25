from climada.entity import ImpactFuncSet, ImpfTropCyclone
from climada.entity.impact_funcs import impact_func_set
from climada.engine import Impact
from climada.engine.impact import Impact as Impact_type
from process.vis import plot_impact
from climada.util.lines_polys_handler import impact_pnt_agg, AggMethod
from geopandas import GeoDataFrame

def get_impact(hazard_cfg: dict, impact_cfg: dict) -> dict:
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

        for proc_impact_func in impact_cfg["func"]:

            if proc_impact_func == "from_emanuel_usa":

                if proc_hazard_name == "TC":
                    proc_func = ImpfTropCyclone.from_emanuel_usa()
                else:
                    raise Exception(f"Hazard type {proc_hazard_name} is not supported yet ...")

                impf_set[proc_hazard_name].append(proc_func)
            else:
                raise Exception(f"Impact function {proc_impact_func} is not supported yet ...")

    return impf_set


def calculate_impact_func(
    exposure_objs: dict, 
    geometry_type: str) -> Impact_type:
    """Calculate the impact function

    Args:
        exposure_obj (Exposures): _description_
        impact_func (impact_func_set): _description_
        hazard_obj (_type_): _description_

    Returns:
        _type_: _description_
    """

    outputs = {}

    for hazard_name in exposure_objs:

        imp = Impact()

        proc_exposure_obj = exposure_objs[hazard_name]

        imp.calc(proc_exposure_obj["exposure"], proc_exposure_obj["impact"], proc_exposure_obj["hazard"], save_mat=True)

        freq_curve = imp.calc_freq_curve()

        outputs[hazard_name] = {
            "imp": imp,
            "freq": freq_curve,
            "exposure": proc_exposure_obj["exposure"],
        }

    return outputs


def calculate_impact_func2(
    workdir: str, exposure_obj: dict, impact_func: impact_func_set, hazard_obj, vis_flag: bool = True, basemap: None or GeoDataFrame = None) -> Impact_type:
    """Calculate the impact function

    Args:
        exposure_obj (Exposures): _description_
        impact_func (impact_func_set): _description_
        hazard_obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    imp = Impact()
    imp.calc(exposure_obj["exposure_obj"], impact_func, hazard_obj, save_mat=True)

    if exposure_obj["type"] == "line":
        exposure_obj["exposure_obj"] = impact_pnt_agg(imp, exposure_obj["exposure_obj"].gdf, AggMethod.SUM)

    freq_curve = imp.calc_freq_curve()

    if vis_flag:
        plot_impact(workdir, basemap, exposure_obj, imp, freq_curve)

    return imp