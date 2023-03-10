Configuration
#######


Calculating hazard impact
============

The configuration file must be defined before any impact assessment tasks. A basic configuration file is shown below:

.. code-block:: yaml

    name: nz_state_highway

    input:
        file: etc/data/nz-state-highway-centrelines-2012-SHP/nz-state-highway-centrelines-2012.shp
        value_adjustment_option: 
            litpop: null
            gdp2asset: null
            fix: 
                method: individual
                value: 30

    hazard:
        landslide:
            enable: True
            cfg: null
        TC:
            enable: True
            cfg:
                climate_scenario: historical
                country_name:
                    - New Zealand
                years: 1980-2020
                use_total: false
        flood:
            enable: True
            cfg: null

    vis:
        basemap: etc/data/nz_coastlines/nz-coastlines-and-islands-polygons-topo-150k.shp
        extent: (174.65, 174.9, -41.37, -41.27)
        exposure:
            enable: False
        hazard:
            enable: False
        impact:
            enable: True


In the above file, there are mainly **4** sections:

- ``name``: The experiment name will be included in the filename of any outputs.

- ``input``: This section controls the infrastructure to be assessed.

    - ``file``: this must be a file in the format of `shapefile`. Details can be obtained at `Exposure: input <https://climaterisk.readthedocs.io/en/latest/Concepts.html#input-data>`_.
    
    - ``value_adjustment_option``: The default value for an infrastructure is `1.0`, but we can overwrite it with either the values from the nearest grid point in the ``Litpop``/``gdp2asset`` dataset, or a customized fixed value. ``litpop`` and ``fix`` cannot be both set to True. 
    
    .. note::

        Note that for ``fix``, when the method is ``total``, the defined value is the total value for all the infrastructure. 
        If the method is ``individual``, the value is used for each segment for the infrastructure.
        Details can be obtained at `Exposure: value <https://climaterisk.readthedocs.io/en/latest/Concepts.html#exposure-value>`_.

- ``hazard``: This defines the types of hazards to be used for the climate risk assessment. Currently ``landslide``, ``TC (Tropical Cyclone)`` and ``flood`` are supported. Details can be obtained at `Hazard <https://climaterisk.readthedocs.io/en/latest/Concepts.html#hazard>`_. An impact function will be assigned automatically depending on the required ``hazard(s)`` in the configuration file. Note that each hazard must be configured seperately in ``cfg``:

    - For example, for ``topical cyclone`` we have:

        - ``climate_scenario``: rcp26, rcp45, rcp60 or historical

        - ``country_name``: the list of countries, e.g., New Zealand, Australia etc.

        - ``years``:

            - for historical data: set a range such as "2012-2020" (Note that the range must be between 1980 and 2020 for now)
            - for projection data, set a number within the range (2040, 2060 and 2080)

        - ``use_total``: If we apply the accumulated hazards when calculating impacts (this only applies when ``climate_scenario`` is ``historical``)

- ``vis``:  This defines how the visualization will be produced. ``basemap`` defines the map to be used (it can be set to ``null``). ``extent`` is set as ``(lon_min, lon_max, lat_min, lat_max)`` (if it is set to ``null``, the default extent from hazard/exposure will be used.)

.. note::

   - Note that for the New Zealand state highway, the total length is 11,000 kilometres (`ref <https://www.nzta.govt.nz/roads-and-rail/research-and-data/state-highway-frequently-asked-questions/>`_.), and the total estimated asset value is NZD$52 billion (`ref <https://www.nzta.govt.nz/planning-and-investment/national-land-transport-programme/2021-24-nltp/activity-classes/state-highway-maintenance/>`_).

   - By default, the output from **Climaterisk** represnets annual hazard impact. The accumulated impact can be switched on by setting ``use_all_years=True`` in the function ``update_exposure``.


Calculating Cost-benefit
============

For calculating the cost-benefit for an adaptation measure, in addition to the configuration for impact calculation (as above), the adaptation configuration section
must be included. For example, we can define the following adaptation for TC (wind):

.. code-block:: yaml

    adaptation:
        TC_wind:
            measure1:
                mdd_impact: (1, 0)
                paa_impact: (1, -0.15)
                hazard_inten_imp: (1, -10)
                cost: 10000
                color_rgb: (1, 1, 1)
                discount_rate: 0.014
            measure2:
                ...

Details about how to define a adaptation configuration can be found in `Adaptation <https://climaterisk.readthedocs.io/en/latest/Concepts.html#Adaptation>`_.

For all the **cost-benefit** calculations, we also need to include future impacts and economy (for exposure) which can be configured as:

.. code-block:: yaml

    economy_annual_growth: 0.03
    future_hazard_para: 0.1

where ``future_hazard_para`` can be set to ``None`` or a number (float):

- ``future_hazard_para = None``: a CLIMADA build-in function (e.g., using data from RCP45) will be used to produce future climate hazard.
- ``future_hazard_para = <number>``: the future climate hazard will be ``<present hazard> * (1.0 + <number>)``. (e.g., by 2080 the impact intensity will 10% stronger).
- ``economy_annual_growth``: Economy annual growth applied to expousre (e.g., it is 3% for the above example).


