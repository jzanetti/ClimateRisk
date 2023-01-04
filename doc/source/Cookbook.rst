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
