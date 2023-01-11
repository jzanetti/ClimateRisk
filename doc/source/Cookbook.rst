Cookbook
#######


1. Calculating climate risk impact
==========

In this example, the climate impacts on the New Zealand State Highway are calculated. Three hazard types: landslide, tropical cyclone and river flood are considered.

First we need to activate the **ClimateRisk** environment:

.. code-block:: bash

    conda activate climaterisk

Then the impact can be produced as:

.. code-block:: bash

    get_impact --workdir /tmp/climaterisk_data --cfg etc/cfg/nz_state_highway_impact.yaml

where ``--workdir`` indicates the working directory and the configuration file is defined from ``nz_state_highway_impact.yaml``. Note that the asset value **52 billion** is assigned in this configuration file.

With the historical hzards data up to 2020, the above command will give the impacts on the state highway from flood, landslide and tropical cyclone (TC).

.. image:: img/all_impacts.png
   :width: 650

As we can see, TC affects more areas across the country while the expected annual impact on average is not as significant as the one from landslide or flood.
The system also provides ``exceedance frequency curve`` for a particular type of hazard. For example, the below shows the exceedance frequency for landslide
over different return period.

.. image:: img/impact_frequemcy_landslide.png
   :width: 450

2. Calculating Cost-benefit
==========

In this example, the Cost-benefit for a few different adapation measures on the New Zealand State Highway are calculated. The used hazard types is tropical cyclone.

First we need to activate the **ClimateRisk** environment:

.. code-block:: bash

    conda activate climaterisk

Then the impact can be produced as:

.. code-block:: bash

    get_benefit --workdir /tmp/climaterisk_data --cfg etc/cfg/nz_state_highway_cost_benefit.yaml

where ``--workdir`` indicates the working directory and the configuration file is defined from ``nz_state_highway_cost_benefit.yaml``.

3. Calculating Supply-chain impact
==========

In this example,  we calculate the direct and indirect supply-chain impacts for countries listed in Input-Output Database.

First we need to activate the **ClimateRisk** environment:

.. code-block:: bash

    conda activate climaterisk

Then the impact can be produced as:

.. code-block:: bash

    get_supplychain --workdir /tmp/climaterisk_data --cfg etc/cfg/nz_supplychain.yaml

where ``--workdir`` indicates the working directory and the configuration file is defined from ``nz_supplychain.yaml``.
