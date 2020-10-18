import click, functools, sys

from tabulate import tabulate
from time     import sleep



cli = click



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
    color_base = lambda c: lambda x: click.style(str(x), fg=c)
else:
    color_base = lambda c: str

yellow = color_base('bright_yellow')
white  = color_base('bright_white')
red    = color_base('bright_red')
green  = color_base('bright_green')
grey   = color_base('bright_black')



def wei_to_tuple(value):
    """ wei --> (value, str_unit) """
    value    = int(value)
    str_unit = 'wei'
    if value > 1000:
        for str_unit in ['Kwei', 'Mwei', 'Gwei', 'Microether', 'Milliether',
                         'Ether', 'Kether', 'Mether', 'Gether', 'Tether']:
            value = value/1000
            if value<1000:
                break
    return (value, str_unit)



def wei_to_str(value):
    """ wei --> str """
    return '{0:.2f} {1}'.format(*wei_to_tuple(value))



def validate_connected(network):
    def validate_is_connect(fnc):
        """ Decorator to validate is connected """

        @functools.wraps(fnc)
        def wrapper():
            if not network.is_connected:
                raise click.ClickException(red(
                'Can not connect to the node\n{}'.format(network.uri)))
            return fnc()

        return wrapper
    return validate_is_connect



def cli_group(fnc=None, name=None):
    if not fnc:
        return click.group(context_settings=CONTEXT_SETTINGS)
    return fnc.group(context_settings=CONTEXT_SETTINGS, name = name)



def show_transaction(network, transaction, frequency=5, times= 120):
    """
    Show data of a transaction
    """
    print()
    print(' '.join([white('Transaction:'), yellow(transaction)]))

    print()
    print('Getting transaction receipt ...', end='', flush=True)
    transaction_receipt, c = None, 1
    while transaction_receipt is None and (c < times):
        transaction_receipt = network.get_transaction_receipt(transaction)
        print('.', end='', flush=True)
        c += 1
        if not transaction_receipt:
            sleep(frequency)
    if transaction_receipt is None:
        print(red(' Timeout!'))
    else:
        print(white(' Ok!'))
        print('')
        print('Block Number:    {}'.format(
            white(transaction_receipt['blockNumber'])))
        print('Gas used:        {}'.format(
            white(wei_to_str(transaction_receipt['gasUsed']))))
        print('Status:          {}'.format(
            {0: red('Fail'),
             1: green('Ok')}.get(
                transaction_receipt['status'],
                white(transaction_receipt['status']))))
        if 'contractAddress' in transaction_receipt:
            if transaction_receipt['contractAddress']:
                print('Contract address {}'.format(
                    yellow(transaction_receipt['contractAddress'])))
    print('')
    return transaction_receipt


def wait_blocks(network, top_=1, frequency=5, times= 120):
    """ Wait for new blocks """
    current  = network.block_number
    wait_for = current + top_ 
    print()
    if top_> 1:
        print(' '.join([white('Current block:'), yellow(current)]))
        print(' '.join([white('Wait for:     '), yellow(wait_for)]))
    else:
        print(' '.join([white('Wait for next block: '), yellow(wait_for)]))
    print()
    print('Getting block ...', end='', flush=True)
    c = 1
    while (current<wait_for) and (c < times):
        current = network.block_number
        print('.', end='', flush=True)
        c += 1
        if current<wait_for:
            sleep(5)
    if current<wait_for:
        print(red(' Timeout!'))
    else:
        print(white(' Ok!'))
    print('')
    return current>=wait_for


def print_line(len=50, symbol="_", color=grey):
    print(color(symbol*len))


def print_title(title, symbol="=", color=grey):
    print()
    print()
    title_lst = str(title).split()
    title_lst[0] = title_lst[0].title()
    print(white(" ".join(title_lst)))
    print(color(" ".join([ symbol[0]*len(x) for x in  title_lst ])))
    print()



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
        print()
        for color in ['yellow', 'white', 'red', 'green', 'grey']:
            fnc = locals()[color]
            print(       ">>> print('This is {}!'.format({}('{}')))".format('{}', color, color.upper())           )
            print('This is {}!'.format(fnc(color.upper())))
        print()
    print(">>>  print_title('hello, this is a title')")
    print_title('hello, this is a title')
    print(">>>  print_line()")
    print_line()



