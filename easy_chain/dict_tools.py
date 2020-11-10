from json    import load, dump
from os.path import isfile, getsize, exists, dirname
from os      import makedirs
from errno   import EEXIST



class PersistentDict(dict):

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self._load()
        self.update(*args, **kwargs)

    def _load(self):
        if isfile(self.filename) and getsize(self.filename) > 0:
            with open(self.filename, 'r') as file_:
                self.update(load(file_))

    def _dump(self):

        if not exists(dirname(self.filename)):
            try:
                makedirs(dirname(self.filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != EEXIST:
                    raise

        with open(self.filename, 'w') as file_:
            dump(self, file_, indent=2, sort_keys=True)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        self._dump()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._dump()

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value
        self._dump()



def reverse_dict(dict_):
    return dict([ (value, key) for key, value in dict_.items()])



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))

    for fnc, args, ok_out in [  
            (reverse_dict, ({'a': 1, 'b': 2}, ), {1: 'a', 2: 'b'}),
        ]:

        out = fnc(*args)

        if out == ok_out:
            eval_ = 'Ok!'
        else:
            eval_ = 'Return: {}, Error!'.format(out)

        message = 'Test: {}({}), Expect: {}, {}'
        message = message.format(
            fnc.__name__,
            ', '.join([ repr(x) for x in list(args)]),
            repr(ok_out),
            eval_)

        print(message)