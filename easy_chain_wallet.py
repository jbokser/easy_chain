#!/usr/bin/env python3
from easy_chain.cli_wallet import WalletCLI
from easy_chain.wallet     import Wallet
from easy_chain.network    import Network, network_conf
from easy_chain.tokens     import Tokens


network    = Network()
wallet     = Wallet(network.uuid)
tokens     = Tokens(network)
wallet_cli = WalletCLI(network, wallet, tokens, network_conf.envs)


if __name__ == '__main__':
    wallet_cli()
