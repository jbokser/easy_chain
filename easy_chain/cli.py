import threading, click, functools, sys

from tabulate import tabulate
from time     import sleep



cli = click



CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])



OK_COLOR = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()



if OK_COLOR:
    color_base = lambda c: lambda x: click.style(str(x), fg=c)
else:
    color_base = lambda c: str

yellow = color_base('bright_yellow')
white  = color_base('bright_white')
red    = color_base('bright_red')
green  = color_base('bright_green')
grey   = color_base('bright_black')



def show_help(command_line):
    with cli.Context(command_line) as ctx:
        cli.echo(command_line.get_help(ctx)) 



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
        return click.group(
            context_settings=CONTEXT_SETTINGS,
            invoke_without_command=True)
    return fnc.group(context_settings=CONTEXT_SETTINGS, name = name)



class Wheeler():

    def __init__(self):

        if OK_COLOR:

            fps = 5
            starts = red('○ ○ ○')
            sequence = [
                ('\b'* 5 + red('● ○ ○')),
                ('\b'* 5 + red('○ ● ○')),
                ('\b'* 5 + red('○ ○ ●')),
                ('\b'* 5 + red('○ ● ○'))]
            ends = ('\b' * len(starts)) +  (' ' * len(starts)) + ('\b' * len(starts))

        else:

            fps = 1
            starts = red('..')
            sequence = ['.']
            ends = ' '

        self._flag =True

        def task():
            print(starts, end='', flush=True)
            i = 0
            while self._flag:
                print(sequence[i], end='', flush=True)
                i += 1
                if i > (len(sequence)-1):
                    i = 0
                sleep(1/fps)
            print(ends, end='', flush=True)

        self._thread = threading.Thread(target=task)
        self._thread.start()

    def stop(self):
        self._flag = False
        self._thread.join()


class Response():

    _ok_list  = ['ok', 'ok!', 'yes', 'yes!', '1', 'si', 'si!']
    _err_list = ['err', 'err', 'error', 'error!', 'no', 'no!',
                 '0', 'fail', 'fail!', 'timeout', 'timeout!']

    def __init__(self, value, **kargs):
        self._value = value
        for key, value in kargs.items():
            setattr(self, key, value)

    @property
    def value(self):
        return self._value
    
    def __bool__(self):
        if self.value and isinstance(self.value, str):
            s_value = self.value.lower().strip()
            if s_value in self._ok_list:
                return True
            if s_value in self._err_list:
                return False
        return bool(self.value)

    def __str__(self):
        if self.value==None:
            return grey('(none)')
        if OK_COLOR:
            if self.value==False:
                return red('✖')
            if self.value==True:
                return green('✔')
            if self.value and isinstance(self.value, str) and self.value.lower(
                    ).strip() in (self._ok_list + self._err_list):
                return '{} {}'.format(
                    green('✔') if bool(self) else red('✖'),
                    white(self.value))
            return white(str(self.value))          
        return str(self.value)



class Ok(Response):

    _ok_list  = ['ok!']

    def __init__(self, **kargs):
        kargs['value'] = 'Ok!'
        Response.__init__(self, **kargs)



class Timeout(Response):

    _err_list = ['timeout!']

    def __init__(self, **kargs):
        kargs['value'] = 'Timeout!'
        Response.__init__(self, **kargs)



class Error(Response):

    _err_list = ['error!']

    def __init__(self, **kargs):
        kargs['value'] = 'Error!'
        Response.__init__(self, **kargs)



class Fail(Response):

    _err_list = ['fail']

    def __init__(self, **kargs):
        kargs['value'] = 'Fail'
        Response.__init__(self, **kargs)



def show_transaction(network, transaction, frequency=5, times=120):
    """
    Show data of a transaction
    """
    print()
    print(' '.join([white('Transaction:'), yellow(transaction)]))
    print()
    print('Getting transaction receipt ', end='', flush=True)
    wheeler = Wheeler()
    transaction_receipt, c = None, 1
    while transaction_receipt is None and (c < times):
        transaction_receipt = network.get_transaction_receipt(transaction)
        c += 1
        if not transaction_receipt:
            sleep(frequency)
    wheeler.stop()
    if transaction_receipt is None:
        response = Timeout()
        print(red('Timeout!'))
    else:
        kargs = dict(
                receipt = transaction_receipt,
                block   = transaction_receipt['blockNumber'],
                gas     = transaction_receipt['gasUsed'],
                status  = {0: Fail(),
                           1: Ok()}.get(
                               transaction_receipt['status'],
                               Response(transaction_receipt['status']))
            )
        if transaction_receipt['contractAddress']:
            kargs['contract_address'] = transaction_receipt['contractAddress']
        response = Ok(**kargs)


        print(white('Ok!'))
        print('')
        print('Block Number:    {}'.format(white(response.block)))
        print('Gas used:        {}'.format(white(wei_to_str(response.gas))))
        print('Status:          {}'.format(response.status))
        if 'contractAddress' in transaction_receipt:
            if transaction_receipt['contractAddress']:
                print('Contract address {}'.format(
                    yellow(response.contract_address)))
    print('')
    return response



def wait_blocks(network, top_=1, frequency=5, times=120):
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
    print('Getting block ', end='', flush=True)
    wheeler = Wheeler()
    c = 1
    while (current<wait_for) and (c < times):
        current = network.block_number
        c += 1
        if current<wait_for:
            sleep(5)
    wheeler.stop()
    if current<wait_for:
        response = Timeout()
    else:
        response = Ok()
    print(response)
    print('')
    return response



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



def pause():
    if OK_COLOR:
        print()
    cli.pause()



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    if OK_COLOR:
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

    print()
    print('Wheeler test: ', end='', flush=True)
    wheeler = Wheeler()
    sleep(5)
    wheeler.stop()
    print('ok!')
    print()

    print(">>>  print(Response(None))")
    print(Response(None))
    print(">>>  print(Response(True))")
    print(Response(True))
    print(">>>  print(Response(False))")
    print(Response(False))
    print(">>>  print(Response('Ok'))")
    print(Response('Ok'))
    print(">>>  print(Response('Error'))")
    print(Response('Error'))
    print(">>>  Response('some value', data='some data').data")
    print(repr(Response('some value', data='some data').data))
    print(">>>  bool(Response('Ok'))")
    print(repr(bool(Response('Ok'))))
    print(">>>  bool(Response('Error'))")
    print(repr(bool(Response('Error'))))
    print(">>>  print(Ok())")
    print(Ok())
    print(">>>  print(Timeout())")
    print(Timeout())
    print(">>>  print(Error())")
    print(Error())
    print(">>>  print(Fail())")
    print(Fail())
