from climada.entity.measures import Measure, MeasureSet
from numpy import array, arange, ones
from climada.entity import DiscRates
from climada.entity import Entity
from climada.engine import CostBenefit
from process import FUTURE_YEARS
from climada.engine.cost_benefit import risk_aai_agg

def calculate_cost_benefit(exp_objs: dict, adaptations: dict, discount_rates: dict):
    """Calculating cost benefit

    Args:
        exp_objs (dict): _description_
        adaptations (dict): _description_
        discount_rates (dict): _description_

    Returns:
        _type_: _description_
    """

    cost_benefit_output = {}
    adaptation_measures_output = {}

    for hazard_name in adaptations:

        adaptation_measure_objs = {}
        for exp_flag in ["hist", "future"]:
            adaptation_measure_objs[exp_flag] = create_adaptation_measure(
                exp_objs[exp_flag][hazard_name]["exposure"], 
                discount_rates[hazard_name], 
                adaptations[hazard_name], 
                exp_objs[exp_flag][hazard_name]["impact"])

        costben = CostBenefit()

        costben.calc(
            exp_objs["hist"][hazard_name]["hazard"], 
            adaptation_measure_objs["hist"], 
            haz_future=exp_objs["future"][hazard_name]["hazard"], 
            ent_future=adaptation_measure_objs["future"],
            future_year=FUTURE_YEARS, 
            risk_func=risk_aai_agg, imp_time_depen=1, save_imp=True)

        cost_benefit_output[hazard_name] = costben
        adaptation_measures_output[hazard_name]= adaptation_measure_objs
    

    # costben.plot_waterfall(exp_objs["hist"][hazard_name]["hazard"], adaptation_measure_objs["hist"], exp_objs["future"][hazard_name]["hazard"], adaptation_measure_objs["future"],
    #                           risk_func=risk_aai_agg)

    return {
        "cost_benefit": cost_benefit_output,
        "adaptation_measures": adaptation_measures_output
    }



def set_discount_rates(exp_obj: dict, adaptation_cfg: dict) -> dict:
    """Set discount rates for each hazard type

    Args:
        exp_obj (dict): _description_
        adaptation_cfg (dict): _description_

    Returns:
        dict: _description_
    """
    discount_rates = {}
    year_range = arange(exp_obj["hist"].ref_year, exp_obj["future"].ref_year + 1)
    n_years = exp_obj["future"].ref_year - exp_obj["hist"].ref_year + 1

    for proc_hazard_name in adaptation_cfg:

        for measure_name in adaptation_cfg[proc_hazard_name]:

            annual_discount_rate = ones(n_years) * adaptation_cfg[proc_hazard_name][measure_name]["discount_rate"]

            discount_rates[proc_hazard_name] = DiscRates(year_range, annual_discount_rate)

    return discount_rates


def define_adaptation(adaptation_cfg: dict, imapct_obj) -> dict:
    """Define a adaptation measure

    Args:
        hazard_name (str): _description_
        hazard_type (str): _description_
        adaptation_cfg (dict): _description_

    Returns:
        _type_: _description_
    """

    adaptation = {}

    for proc_hazard_name in imapct_obj:

        if proc_hazard_name not in adaptation_cfg:
            raise Exception(f"Hazard {proc_hazard_name} is enabled but not defined in adaptation ...")

        meas_set = MeasureSet()

        for measure_name in adaptation_cfg[proc_hazard_name]:

            meas = Measure()
            meas.name = measure_name
            meas.haz_type = imapct_obj[proc_hazard_name].get_hazard_types()[0]
            meas.color_rgb = array(
                list(eval(adaptation_cfg[proc_hazard_name][measure_name]["color_rgb"])))
            meas.cost = adaptation_cfg[proc_hazard_name][measure_name]["cost"]
            meas.mdd_impact = eval(
                adaptation_cfg[proc_hazard_name][measure_name]["mdd_impact"])
            meas.paa_impact = eval(
                adaptation_cfg[proc_hazard_name][measure_name]["paa_impact"])
            meas.hazard_inten_imp = eval(
                adaptation_cfg[proc_hazard_name][measure_name]["hazard_inten_imp"])

            meas_set.append(meas)

        adaptation[proc_hazard_name] = meas_set

    return adaptation



def create_adaptation_measure(exp_obj_input, discount_rate, adaptation_measure, impact_func_set) -> dict:
    """Creating adaptation measures

    Args:
        exp_obj (Exposures): _description_
        discount_rate (_type_): _description_
        adaptation_measure (_type_): _description_
        impact_func_set (_type_): _description_

    Returns:
        dict: _description_
    """
    return Entity(
        exposures=exp_obj_input, 
        disc_rates=discount_rate,
        impact_func_set=impact_func_set, 
        measure_set=adaptation_measure)