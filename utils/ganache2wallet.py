#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.wallet    import WalletGanache, Wallet
from easy_chain.network   import Network

network = Network('ganache')

# Non persistent wallet with the deterministic Gananche address
wallet_ganache = WalletGanache()
wallet         = Wallet(network.uuid)

for key, value in wallet_ganache.items():
    name = wallet_ganache.get_name(key)
    print('{}: {}'.format(name, key))
    wallet.add_priv_key(value, encrypt=False, name=name)

