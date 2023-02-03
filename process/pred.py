import climada.util.dates_times as u_dt
from datetime import datetime, timedelta
from numpy import asarray, unique, array
from random import sample, randint
from process import RCP_CFG


def get_unique_event_name(hazard_to_use) -> array:
    """Get unique event name from hazard

    Args:
        hazard_to_use (_type_): hazard to be used

    Returns:
        array: unique event name
    """
    event_name_list = []
    for proc_event_name in hazard_to_use.event_name:
        try:
            proc_event_name = proc_event_name[: proc_event_name.index("_")]
        except ValueError:
            pass

        event_name_list.append(proc_event_name)

    return unique(asarray(event_name_list))


def update_event_date(hazard_to_use, year_to_use: int):
    """Update event date (year)

    Args:
        hazard_to_use (_type_): hazard to be used
        year_to_use (int): year to be used

    Returns:
        _type_: updated event
    """
    new_event_date = []
    pro_date_ref = None
    for pro_date in hazard_to_use.date:

        if pro_date != pro_date_ref:

            proc_month = str(randint(1, 12)).zfill(2)
            proc_day = str(randint(1, 28)).zfill(2)
            proc_date_to_update = f"{year_to_use}-{proc_month}-{proc_day}"
            proc_date_to_update = u_dt.str_to_date(proc_date_to_update)
            pro_date_ref = pro_date

        new_event_date.append(proc_date_to_update)

    hazard_to_use.date = asarray(new_event_date)

    return hazard_to_use


def update_event_id(hazard_to_use, id_to_start: int):
    """Update event ID number

    Args:
        hazard_to_use (_type_): hazard to be used
        id_to_start (int): ID to start with

    Returns:
        _type_: _description_
    """
    new_event_id = []
    for i in range(1, len(hazard_to_use.event_id) + 1):

        new_event_id.append(id_to_start + i)

    hazard_to_use.event_id = asarray(new_event_id)

    return hazard_to_use


def update_frequency(hazard_to_use, frequency_incre_accum_ratio: float):
    """Update frequency

    Args:
        hazard_to_use (_type_): hazard to be used
        frequency_incre_accum_ratio (float):frequency increment (accumulated)

    Returns:
        _type_: _description_
    """
    hazard_to_use.frequency = hazard_to_use.frequency * (
        1 + frequency_incre_accum_ratio
    )

    return hazard_to_use


def update_intensity(hazard_to_use, intensity_incre_accum_ratio: float):
    """Update intensity

    Args:
        hazard_to_use (_type_): hazard to be used
        intensity_incre_accum_ratio (float):intensity increment (accumulated)

    Returns:
        _type_: _description_
    """
    hazard_to_use.intensity = hazard_to_use.intensity * (
        1 + intensity_incre_accum_ratio
    )

    return hazard_to_use


def update_event_name(hazard_to_use, year_to_use: int):
    """Update event names

    Args:
        hazard_to_use (_type_): harzard to be used
        year_to_use (int): year to be used

    Returns:
        _type_: _description_
    """
    hazard_event_names = []
    for proc_name in hazard_to_use.event_name:
        hazard_event_names.append(str(year_to_use) + proc_name[4:])

    hazard_to_use.event_name = hazard_event_names

    return hazard_to_use


def tc_pred(
    hazard_all, years: list, rcp: str, rcp_cfg: dict = RCP_CFG, ref_years: int = 5
):
    """Predicting TC winds

    Args:
        hazard_all (_type_): base hazard to start with
        years (list): years to be predicted
        rcp (str): RCP name
        rcp_cfg (dict, optional): RCP configuration. Defaults to RCP_CFG.
        ref_years (int, optional): reference years. Defaults to 5.

    Returns:
        _type_: Update hazards
    """

    last_date = datetime.strptime(u_dt.date_to_str(hazard_all.date[-1]), "%Y-%m-%d")
    last_5_years_date = last_date - timedelta(days=365 * ref_years)

    hazard_ref = hazard_all.select(
        date=(f"{last_5_years_date.year}-01-01", f"{last_date.year}-01-01")
    )

    # get unique event names
    unqiue_event_names_ref = get_unique_event_name(hazard_ref)
    unqiue_event_names_all = get_unique_event_name(hazard_all)

    # average unique event over refereced period
    events_num_ref = int(round(len(unqiue_event_names_ref) / float(ref_years)))

    predicted_hazards = []
    for proc_year in years:
        print(f"processing {proc_year}...")
        proc_events_num = int(
            round(
                (
                    events_num_ref
                    + (proc_year - last_date.year) * rcp_cfg[rcp]["events_num_incre"]
                )
            )
        )

        selected_event_name_index = sample(
            range(0, len(unqiue_event_names_all)), proc_events_num
        )

        proc_event_names = []
        for proc_event_name_index in selected_event_name_index:

            proc_event_names.extend(
                [
                    s
                    for s in hazard_all.event_name
                    if unqiue_event_names_all[proc_event_name_index] in s
                ]
            )

        selected_events = hazard_all.select(event_names=proc_event_names)

        selected_events = update_event_date(selected_events, proc_year)
        selected_events = update_event_id(
            selected_events,
            max(
                [
                    max(selected_events.event_id),
                    max(hazard_all.event_id),
                ]
            ),
        )
        selected_events = update_frequency(
            selected_events,
            (proc_year - last_date.year) * rcp_cfg[rcp]["frequency_incre"],
        )
        selected_events = update_intensity(
            selected_events,
            (proc_year - last_date.year) * rcp_cfg[rcp]["intensity_incre"],
        )

        selected_events = update_event_name(selected_events, proc_year)

        predicted_hazards.append(selected_events)

    return predicted_hazards
