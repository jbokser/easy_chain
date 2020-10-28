import sys, os, json
from tabulate import tabulate
from os       import listdir
from os.path  import isfile, join, dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(dirname(base_dir)))

from easy_chain.contracts.contract_base import *
from easy_chain.conf                    import get as config

sys.path = bkpath



def config_call_back(options):
    return {
        'contracts_conf': options 
    }

config(locals(),
       config_call_back,
       ['contracts.json', 'contracts_default.json'],
       'contracts',
       env_pre = 'wallet')



def get_modules():

    exclude       = ['contract_base.py']
    mypath        = os.path.dirname(__file__)
    files         = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    files         = [f for f in files if f not in exclude]
    modules_names = [ n[:-3] for n in files if n[-3:] =='.py' and n[:1]!='_']

    bkpath   = sys.path[:]
    base_dir = dirname(abspath(__file__))
    sys.path.append(base_dir)

    for name in modules_names:
        obj = __import__(name)
        for n in dir(obj):
            if n[:1]!='_':
                sub_obj = getattr(obj, n)
                if sub_obj!=Contract:
                    globals()[n] = sub_obj

    sys.path = bkpath



get_modules()
del get_modules


class ContractsBase(list):


    def __call__(self, search):
        for contract in self:
            address = contract.address
            if address:
                address = address.lower()
            if str(search).lower() in [address,
                                       contract.name.lower()]:
                return contract
        return None



class Contracts(ContractsBase):


    def __init__(self, network):
        self._network = network
        self.profile = network.profile
        contracts_dict = contracts_conf.get(self.profile, {})
        for address, value in contracts_dict.items():
            address = network.Address(address)
            if isinstance(value, dict):
                if not 'class' in value:
                    value['class'] = "Contract"
                if not value['class'] in globals():
                    value['class'] = "Contract"
                constructor = globals()[value['class']]
                kargs = dict(value)
                del kargs['class']
                kargs['network'] = network
                kargs['address'] = address
                c = constructor(**kargs)
                self.append(c)



class ContractsFromJsonFiles(ContractsBase):

    def __init__(self, network, dir_):

        self._network = network
        self.profile = network.profile

        file_list= [ f for f in listdir(dir_) if isfile(
            join(dir_, f)) and f.endswith('.json') ]

        for file_name in file_list:
            file_path = join(dir_, file_name)
            try:
                with open(file_path, 'r') as file_:
                    data = json.load(file_)
            except:
                data = {}

            address = None
            if "networks" in data:
                if data["networks"]:
                    if str(network.chain_id) in data["networks"]:
                        address = data["networks"][str(network.chain_id)]['address']

            name = None
            if "contractName" in data:
                name = data["contractName"]

            kargs = dict(
                network       = network,
                address       = address,
                name          = name,
                abi_path      = dir_,
                abi_file      = file_name,
                bytecode_path = dir_,
                bytecode_file = file_name)

            try:
                self.append(Contract(**kargs))
            except ValueError:
                pass




if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    bkpath   = sys.path[:]
    base_dir = dirname(abspath(__file__))
    sys.path.append(dirname(dirname(base_dir)))

    from easy_chain.network import Network, network_conf

    sys.path = bkpath

    table = []
    for profile in network_conf.network_profiles.keys():
        network = Network(profile)
        contracts = Contracts(network)
        table += [ c.as_dict for c in contracts ]
    print()
    print(tabulate(table, headers={}))
    print()
