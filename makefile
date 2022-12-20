.ONESHELL:

SHELL = /bin/bash

override CONDA = $(CONDA_BASE)/bin/conda
override PKG = climaterisk
override CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
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
	mkdir -p /tmp/$(PKG)
	git clone https://github.com/CLIMADA-project/climada_python.git /tmp/$(PKG)/climada_python
	cd /tmp/$(PKG); git checkout develop
	conda env create -n $(PKG) -f /tmp/$(PKG)/requirements/env_climada.yml
	cd /tmp; pip install -e $(PKG)

all: env
