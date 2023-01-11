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

where ``--workdir`` indicates the working directory and the configuration file is defined from ``nz_state_highway_impact.yaml``. Note that the fixed value **1.0** is assigned in this configuration file.


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
