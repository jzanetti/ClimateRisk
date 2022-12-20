.ONESHELL:

SHELL = /bin/bash

override CONDA = $(CONDA_BASE)/bin/conda
override PKG = climaterisk
override CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
	@echo "set conda_base, e.g., export CONDA_BASE=/Users/zhans/miniconda3"
	@echo "current conda_base: $(CONDA_BASE)"
	@echo "current conda: $(CONDA)"
	@echo "- install climaterisk: make all"
	@echo "- install env: make env"
	@echo "- remove all dependancies: make clear_all"

clear_env:
	rm -rf $(CONDA_BASE)/envs/$(PKG)

clear_all:
	rm -rf $(CONDA_BASE)/envs/$(PKG)
	rm -rf $(CONDA_BASE)/pkgs/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/.cache/paths/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/.cache/recipe/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/.cache/paths/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/.cache/recipe/$(PKG)*
	$(CONDA) index $(CONDA_BASE)/conda-bld

env: clear_env
	rm -rf /tmp/$(PKG)
	mkdir -p /tmp/$(PKG)
	curl -o /tmp/$(PKG)/env_climada.yml https://raw.githubusercontent.com/CLIMADA-project/climada_python/main/requirements/env_climada.yml
	conda env create -n $(PKG) -f /tmp/$(PKG)/env_climada.yml
	conda activate $(PKG); $(CONDA_BASE)/envs/$(PKG)/bin/pip install climada

all: env
