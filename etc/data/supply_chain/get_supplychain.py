from climada_petals.engine import SupplyChain
import pickle

supplychain = SupplyChain()
supplychain.read_wiod16(year=2012)
pickle.dump(supplychain, open("etc/data/supply_chain/supply_chain.pickle", "wb"))