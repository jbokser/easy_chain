#!/usr/bin/env python3
from easy_chain.cli        import cli_group
from easy_chain.cli_wallet import WalletCLI
from easy_chain.wallet     import Wallet
from easy_chain.network    import Network, network_conf
from easy_chain.tokens     import Tokens


network    = Network()
wallet     = Wallet(network.uuid)
tokens     = Tokens(network)


@cli_group()
def wallet_cli():
    """
    Simple Easy Chain CLI Wallet

    Develped by Juan S. Bokser (2020)
    """

WalletCLI(wallet_cli, network, wallet, tokens, network_conf.envs)



if __name__ == '__main__':
    wallet_cli()
