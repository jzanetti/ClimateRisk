import pickle

from datetime import datetime, timedelta
from random import randint

from numpy import datetime64
from copy import deepcopy
from process.climada.plot import plot_tc


tc_track_data_base = pickle.load( open( "etc/test/tc_track.pickle", "rb" ) )

proc_times = []
proc_data_index = []

year_range = [2022, 2030]

year_interval = 1

yearly_increase_ratio = 0.15
intensity_increase_ratio = 0.05

random_track_range = randint(-1, 2)

tc_track_data_list = tc_track_data_base.data

tc_track_data = { datetime.utcfromtimestamp(proc_data["time"].values[0].tolist() / 1e9) : proc_data for proc_data in tc_track_data_list }

max_year = max(tc_track_data).year
last_5_years = max_year - 5

recorded_years_for_last_5_years = []
for tc_date in tc_track_data:
    if tc_date.year > last_5_years:
        recorded_years_for_last_5_years.append(tc_date.year)

most_occured_year_for_last_5_years  = max(set(recorded_years_for_last_5_years), key=recorded_years_for_last_5_years.count)
most_occurance_for_last_5_years = recorded_years_for_last_5_years.count(most_occured_year_for_last_5_years)

for proc_year in range(year_range[0], year_range[1], year_interval):

    year_diff = proc_year - max_year

    total_increment = year_diff * yearly_increase_ratio
    intensity_increment_ratio = year_diff * intensity_increase_ratio

    proc_occurance = int(round(most_occurance_for_last_5_years + total_increment, 0)) + random_track_range

    tc_index = [randint(0, len(tc_track_data)) for iter in range(proc_occurance)]

    for proc_tc_track in [tc_track_data_list[i] for i in tc_index]:

        updated_datetime = []

        for i, proc_datetime in enumerate(proc_tc_track["time"].values):

            proc_datetime_current_step = datetime.utcfromtimestamp(proc_datetime.tolist() / 1e9)

            if i == 0:
                days_delta = randint(1, 45)
                proc_datetime_current_step += timedelta(days=days_delta)
                proc_datetime_previous_step = deepcopy(proc_datetime_current_step)
            else:
                delta_datetime = (proc_datetime_current_step - proc_datetime_previous_step).total_seconds()
                proc_datetime_current_step += timedelta(seconds=delta_datetime)
                proc_datetime_previous_step = deepcopy(proc_datetime_current_step)

            try:
                new_datetime = datetime(proc_year, proc_datetime_current_step.month, proc_datetime_current_step.day, proc_datetime_current_step.hour)
            except ValueError: # leap year
                pass

            updated_datetime.append(datetime64(new_datetime.strftime("%Y-%m-%dT%H:00")))
        
        proc_tc_track = proc_tc_track.assign_coords({"time": updated_datetime}).assign_attrs({"orig_event_flag": False})
        proc_tc_track["max_sustained_wind"].values = proc_tc_track["max_sustained_wind"].values * (1.0 + intensity_increment_ratio)

        tc_track_data_list.append(proc_tc_track)

tc_track_data_base.data = tc_track_data_list

tc_track_data_base.plot()

plot_tc("/tmp", tc_track_data_base, only_nz=False)

