Impact
===================================

We are able to produce impact assessments for infrastructures given different types of hazards.
All **infrastructures** must be provided in the `shapefile` format, which contains objects such as `LineString` or `Point`. 
In contrast, the **hazard** can come from a file in the `shapefile` format, or be obtained from the `Climada` API.

The production of an impact assessment task is controlled by a configuration file in the format of `YAML`.

Configuration
^^^^^^^^^
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
                value: 52000000000

    hazard:
        landslide:
            enable: True
        TC:
            enable: True
        flood:
            enable: True

    vis:
        basemap: etc/data/nz_coastlines/nz-coastlines-and-islands-polygons-topo-150k.shp
        extent: null
        exposure:
            enable: False
        hazard:
            enable: False
        impact:
            enable: True


In the above file, there are mainly **5** sections:

- ``name``: The experiment name will be included in the filename of any outputs.
- ``input``: This section controls the infrastructure to be assessed.
    - ``file``: this must be a file in the format of `shapefile`.
    - ``value_adjustment_option``: The default value for an infrastructure is `1.0`, but we can overwrite it with either the values from the nearest grid point in the ``Litpop``/``gdp2asset`` dataset, or a customized fixed value. 
    ``litpop`` and ``fix`` cannot be both set to True. 
    Note that for ``fix``, when the method is ``total``, the defined value is the total value for all the infrastructure. 
    If the method is ``individual``, the value is used for each segment for the infrastructure 
- ``hazard``: This defines the types of hazards to be used for the climate risk assessment. Currently ``landslide``, ``TC (Tropical Cyclone)`` and ``flood`` are supported.


.. note::

   Note that for the New Zealand state highway, the total length is 11,000 kilometres (`ref <https://www.nzta.govt.nz/roads-and-rail/research-and-data/state-highway-frequently-asked-questions/>`_.), and
   the total estimated asset value is NZD$52 billion (`ref <https://www.nzta.govt.nz/planning-and-investment/national-land-transport-programme/2021-24-nltp/activity-classes/state-highway-maintenance/>`_).