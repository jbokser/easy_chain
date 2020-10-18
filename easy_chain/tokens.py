import json
from sys      import path
from os       import listdir
from os.path  import dirname
from tabulate import tabulate

path.append(dirname(__file__))

from conf      import get as config
from contracts import ERC20

def config_call_back(options):
    return {
        'tokens_conf': options 
    }

config(locals(),
       config_call_back,
       ['tokens.json', 'tokens_default.json'],
       'tokens',
       env_pre = 'wallet')



class Token(ERC20):
    pass



class Tokens(list):

    def __init__(self, network):
        self._network = network
        self.profile = network.profile
        token_dict = tokens_conf.get(self.profile, {})
        for key, value in token_dict.items():
            self.append(Token(network, key, **value))
        
    def __call__(self, search):
        for token in self:
            if str(search).lower() in [token.address.lower(),
                                       token.name.lower(),
                                       token.symbol.lower()]:
                return token
        return None



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    from network import Network, network_profiles
    table = []
    for profile in network_profiles.keys():
        network = Network(profile)
        tokens = Tokens(network)
        table += [ t.as_dict for t in tokens ]
    print()
    print(tabulate(table, headers={}))
    print()
