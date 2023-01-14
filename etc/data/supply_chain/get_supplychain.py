from climada_petals.engine import SupplyChain
from pickle import dump as pickle_dump

supplychain = SupplyChain()
supplychain.read_wiod16(year=2012)
pickle_dump(supplychain, open("etc/data/supply_chain/supply_chain.pickle", "wb"))