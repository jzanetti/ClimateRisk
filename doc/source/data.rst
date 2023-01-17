Data
#######

Data such as ``exposure`` and ``hazard`` must be provided from external sources.


Exposure
=========
**Exposure** describes the set of assets, people, livelihoods, infrastructures, etc. within an area of interest that to be analyzed.

* In **ClimateRisk**, the baseline of **Exposure** must be provided in the format of *shapefile*. Some examples are provided in ``etc/data``

* In addition to the baseline, the ``asset value`` must be provided. The value can be either provided as a fixed value, or it can be estimated from ``LitPop`` or ``GDP``.
    
    The options of ``asset value`` should be defined in the configuration file (Details can be obtained from `Exposure value <https://climaterisk.readthedocs.io/en/latest/Concepts.html#exposure-value>`_).
    ``LitPop`` or ``GDP`` value can be obtained either from **CLIMADA** API, or a preprocessing procedure:
       
    * ``LitPop`` (in ``process/exposure.py``):

        .. code-block:: python

            from climada.util.api_client import Client

            client = Client()

            if isinstance(country, str):
                litpop_obj = client.get_litpop(country=country)

    * ``GDP`` (in ``etc/data/get_gdp``):

        ``GDP`` data must be firstly downloaded from `The Inter-Sectoral Impact Model Intercomparison Project <https://www.isimip.org>`_.
        Then the downloaded ``netcdf`` data can be processed by the *CLIMADA* API as:

        .. code-block:: python

            from climada_petals.entity.exposures.gdp_asset import GDP2Asset

            gdpa = GDP2Asset()
            gdpa.set_countries(countries = ['NZL'], ref_year = 2020, path="/Users/zhans/Downloads/gdp_2005soc_0p5deg_annual_2006-2099.nc4")
            gdpa_gdf = gdpa.gdf
        
        Where the path is the downloaded data from *ISIMPI*. Then the GDP data can be assigned to the exposure baseline data.

Hazard
=========
Currently there are three types of hazards (``Tropical cyclone``, ``landslide`` and ``flood``) can be applied:

- Tropical cyclone: 

    Tropical cyclone (TC) contains two types of dataset: ``track`` and ``wind speed``. In **ClimateRisk** at the moment,
    ``track`` is  used in the impact or supply-chain calculation, while ``wind speed`` is used for estimating cost-benefit.


    There are two ways to obtain the TC data (defined in ``process/hazard.py``):

    - The data can be obtained from the downloaded ``ibtracs`` netcdf file (via ``CLIMADA`` API):

        .. code-block:: python

            from climada.hazard.tc_tracks import TCTracks

            hazard_hist = TCTracks.from_ibtracs_netcdf(
                provider=tc_data_cfg["track"]["provider"], 
                year_range=str2list_for_year(tc_data_cfg["track"]["year_range"]), 
                estimate_missing=True)

    - The data also can be directly obtained from ``CLIMADA`` API as:

        .. code-block:: python

            from climada.util.api_client import Client

            client = Client()

            client.get_hazard(
                "tropical_cyclone",
                properties={
                    "country_name": country,
                    "climate_scenario": "historical",
                    "nb_synth_tracks": "10"})

- Landslide:
Landslide data are obtained from `NASA global landslide catalog (points) <https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521>`_.
The **CLIMADA-PETALS** call *Landslide** then can be used to decode the data:

.. code-block:: python

    from process.climada_petals.landslide import Landslide

    landslide = Landslide.from_hist(bbox=domain, input_gdf=LANDSLIDE_DATA, res=res)

The above gives landslide data globally, while for New Zealand, there are a total of 164 events recorded spanning from 1979 to 2018. 

- Flood:

Global flood data can be downloaded from `The Inter-Sectoral Impact Model Intercomparison Project <https://www.isimip.org>`_.
The netcdf file can be obtained from `Here <https://files.isimip.org/cama-flood/results>`_.

- ``flood depth``: flddph_150arcsec_clm40_gswp3_0.nc
- ``flood fraction``: fldfrc_150arcsec_clm40_gswp3_0.nc

The downloaded `netCDF` file can be decoded using :

.. code-block:: python

    from climada_petals.hazard.river_flood import RiverFloods
    years = array(range(1979, 2010, 1)).tolist()
    rf = RiverFlood.from_nc(countries = ["NZL"], years=years, dph_path=dph_path, frc_path=frc_path)

where ``NZL`` means we only process the data for New Zealand.
