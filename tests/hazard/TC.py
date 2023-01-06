from climada.util.api_client import Client
import matplotlib.pyplot as plt
from pandas import DataFrame
client = Client()

data_types = client.list_dataset_infos()
dtf = DataFrame(data_types)

# unique_fields = set([d.get('data_type') for d in dtf["data_type"]])



"""

future_year = 2080
haz_present = client.get_hazard('tropical_cyclone',
                                properties={
                                    'country_name': 'New Zealand',
                                    'climate_scenario': 'historical',
                                    'nb_synth_tracks':'10'}
                                )

print("xxx")
haz_present.plot_rp_intensity(return_periods=(50,), smooth=False)
plt.savefig("test.png")
plt.close()
print("done")
"""