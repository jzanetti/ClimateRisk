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


