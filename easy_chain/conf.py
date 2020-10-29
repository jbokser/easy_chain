import json

from os.path      import dirname, abspath, basename, expanduser, exists
from json.decoder import JSONDecodeError
from sys          import stderr, argv
from os           import environ, makedirs
from errno        import EEXIST
from shutil       import copyfile


app_name = basename(__file__)



def get(out = {},
        call_back    = lambda x: {},
        files        = ['main.json', 'main_default.json'],
        name         = '',
        env_pre      = 'ENV',
        dir_         = '/conf/',
        app_name     = 'easy_chain',
        copy_to_home = True,
        places       = None):

    config_options = None
    file_          = None

    if isinstance(files, str):
        files = [files]

    if isinstance(places, str):
        places = [places]

    if not places:
        places = [dirname(abspath(argv[0])),
                  dirname(abspath(__file__)) + '/data']
    places = [expanduser("~") + '/.' + app_name] + places

    file_list = []
    for d in places:
              for f in files:
                  full_path_file = d + dir_ +  f
                  if not full_path_file in file_list:
                      file_list.append(full_path_file)

    first_file = file_list[0]

    while not(config_options) and file_list:

        file_ = file_list.pop(0)

        try:
            with open(file_, 'r') as f:
                config_options = json.load(f)
        except JSONDecodeError as e:
            print('Error in "{}", {}'.format(file_, str(e)), file=stderr)
            exit(1)
        except Exception as e:
            config_options = {}
    
    if copy_to_home and config_options and file_ != first_file:

        if not exists(dirname(first_file)):
            try:
                makedirs(dirname(first_file))
            except OSError as exc: # Guard against race condition
                if exc.errno != EEXIST:
                    raise

        copyfile(file_, first_file)

    config_options_json = json.dumps(config_options, indent=4, sort_keys=True)

    try:
        data = call_back(config_options)
    except ValueError as e:
        print('Error in "{}", Value error: {}'.format(file_, str(e)), file=stderr)
        exit(1)
    except KeyError as e:
        print('Error in "{}", Key error: {}'.format(file_, str(e)), file=stderr)
        exit(1)
    except TypeError:
        if name:
            message = 'Error, {} configuration not found!'.format(name)
        else:
            message = 'Error, configuration not found!'
        print(message, file=stderr)
        exit(1)

    new_config_options_json = json.dumps(config_options, indent=4, sort_keys=True)

    if  new_config_options_json!=config_options_json:
        with open(first_file, 'w') as f:
            f.write(new_config_options_json)

    if env_pre:

        if 'envs' in out:
            env_dict = out['envs']
        else:
            env_dict={}

        check_env(data, env_pre=env_pre, env_dict=env_dict)

    for key, value in data.items():
        out[key] = value

    out['config_file'] = file_
    if env_pre:      
        out['envs']    = env_dict

    return out


def check_env(d, p = [], env_pre='ENV', env_dict={}):

    for key in d.keys():

        if type(d[key])==dict:
            check_env(d[key], p + [key], env_pre, env_dict)
        else:
            env_name = '_'.join('_'.join([env_pre] + p + [key]).upper().split())
            env_fnc  = type(d[key])
            try:
                raw = environ[env_name]
            except KeyError :
                raw = None
            env_dict[env_name] = d[key]
            if raw != None:
                try:
                    value = env_fnc(raw)
                except:
                    value = None
                if value != None:
                    d[key] = value



if __name__ == '__main__':

    print("File: {}, Ok!".format(repr(__file__)))
    get(globals())
    print("Config file: {}, Ok!".format(repr(config_file)))
