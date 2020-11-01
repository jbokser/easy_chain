import sys
from os.path import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from easy_chain.cli     import white, red, grey, Response, BadParameter, command, command_group
from easy_chain.cli     import tabulate, validate_connected, Choice, argument
from easy_chain.wallet  import BadPassword
from easy_chain.network import wei_to_str, network_conf

sys.path = bkpath



def NetworkCLI(group, network, network_conf):


    @command(group, 'gas')
    @validate_connected(network)
    def gas_price():
        """ Show the gas price """
        print(white('gasPrice = {}').format(wei_to_str(network.gas_price)))
        print(white('minimum  = {}').format(wei_to_str(network.minimum_gas_price)))


    @command(group, 'block')
    @validate_connected(network)
    def block_number():
        """ Last block """
        n = network.block_number
        print(white('blockNumber = {}').format(n))
        print(white('timestamp   = {}').format(network.block_timestamp(n)))


    if network_conf.envs:
        @command(group, 'envs')
        def show_envs():
            """ Show environment variables to use """
            print()
            print(tabulate(network_conf.envs.items(),
                headers = ['Environment variable',
                           'Default value']))
            print()


    @command(group, 'default')
    @argument('network', type=Choice(network_conf.network_profiles.keys()))
    def network_default(network):
        """ Set the default NETWORK to operate """

        if network not in network_conf.network_profiles:
            raise BadParameter(red('Network not found'))

        network_conf.selected_profile = network

        print(white('{} has been marked as default.'.format(repr(network))))


    @command(group, 'list')
    def network_list():
        """ List of wallet addresses """
        table = []
        for name, data in network_conf.network_profiles.items():
            row = {}
            row['name'] = name
            row['default'] = Response(name==network_conf.selected_profile)
            for key, value in data.items():
                row[key] = value
            if not 'poa' in row:
                row['poa'] = None
            row['poa'] = Response(row['poa'])
            table.append(row)
            if 'profile' in row:
                del row['profile']
        print()
        headers = {
            'name' :    white('Name'),
            'default':  white('Default'),
            'chain_id': white('Chain ID'),
            'poa':      white('PoA'),
            'uri':      white('URI')}
        print(tabulate(table, headers=headers))
        print()
        print(grey('(config file: {})'.format(network_conf.config_file)))
        print()


    @command(group, 'filename')
    def network_filename():
        """ Show network config file name """
        print(network_conf.config_file)



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
