from climada.entity.measures import Measure
from numpy import array


def define_adaptation(adaptation_cfg: dict):
    """Define a adaptation measure

    Args:
        hazard_name (str): _description_
        hazard_type (str): _description_
        adaptation_cfg (dict): _description_

    Returns:
        _type_: _description_
    """

    adaptation = {}

    for proc_hazard_name in adaptation_cfg:

        meas = Measure()
        meas.name = proc_hazard_name
        meas.haz_type = "dummy" # will be replaced by the hazard type from hazard function later
        meas.color_rgb = array(list(eval(adaptation_cfg["color_rgb"])))
        meas.cost = eval(adaptation_cfg["cost"])
        meas.mdd_impact = eval(adaptation_cfg["mdd_impact"])
        meas.paa_impact = eval(adaptation_cfg["paa_impact"])
        meas.hazard_inten_imp = eval(adaptation_cfg["hazard_inten_imp"])

        adaptation[proc_hazard_name] = meas

    return meas