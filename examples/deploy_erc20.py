#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.cli       import show_transaction, wait_blocks, print_title, print_line
from easy_chain.wallet    import Wallet
from easy_chain.network   import Network
from easy_chain.contracts import ERC20

network = Network('ganache')

# Non persistent wallet
wallet  = Wallet() 

# Add first deterministic gananche address
wallet.add_priv_key(
    "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
    encrypt=False)


def deploy():

    token = ERC20(network, name='My Token', symbol='MYT')

    transaction = token.deploy(wallet.sign, wallet.default, gas_limit = 3500000)

    response = show_transaction(network, transaction)


    if not response.contract_address:
        print("Can't get the contract address")
        return

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    token.address = response.contract_address

    transaction = token.mint(wallet.sign, wallet.default, wallet.default, 123, gas_limit = 3500000)

    show_transaction(network, transaction)

    if not wait_blocks(network):
        print("Can't get the next block")
        return

    print_line()
    print_title(token)
    print('Balance of {} = {} {}'.format(
        wallet.default,
        token.balance(wallet.default),
        token.symbol))
    print()



if __name__ == '__main__':
    if network.is_connected:
        deploy()
    else:
        print('For this example you need to have ganache running (in deterministic mode).')
        