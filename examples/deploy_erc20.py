#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain.cli       import show_transaction, wait_blocks, print_title, print_line
from easy_chain.wallet    import WalletGanache
from easy_chain.network   import Network
from easy_chain.contracts import ERC20

network = Network('ganache')

# Non persistent wallet with the deterministic Gananche address
wallet = WalletGanache() 



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
        