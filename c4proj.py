import sys
import os
import re
from cookiecutter.main import cookiecutter
import ruamel.yaml as yaml
#from ruamel.yaml.comments import CommentedMap as CommentedMap
#from ruamel.yaml.comments import CommentedSeq as CommentedSeq
import json


def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def load_config(path):
    with open(path, 'r') as stream:
        data = yaml.safe_load(stream)
    return set_defaults(data)


def extra_context(args):
    cfg = load_config(args.cfg)
    cmd_data = {} #{k: getattr(args, k) for k in vars(args)}
    for k, v in cfg.items():
        if cmd_data.get(k) is None:
            cmd_data[k] = v
    for k, v in cmd_data.items():
        log(k, "---", v)
    return cmd_data


def _cookiecutter(args, **more_args):
    tpl = './cookiecutter-c4proj'
    with open(os.path.join(tpl, "cookiecutter.json"), "w") as json_file:
        json.dump(extra_context(args), json_file, indent=4)
    cookiecutter(tpl, no_input=True, **more_args)


def set_defaults(data):
    def default_to(item, default):
        d = data.get(item)
        if ((d is None) or (str(d) == "")):
            log(f"cfg: item '{item}' empty or not set. defaulting to '{default}'")
            data[item] = default
    name = data['name']
    default_to('url', data['repo'])
    default_to('slug', re.sub(r'[- ]', '_', name.lower()))
    default_to('slugu', re.sub(r'[- ]', '_', name.upper()))
    default_to('slugc', re.sub(r'[- ]', '', name.capitalize()))
    default_to('slugk', name.lower().replace(' ', '-'))
    default_to('author_and_email', f'{data["author"]} <{data["email"]}>')
    return data


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def create(args):
    "create a project"
    _cookiecutter(args)


def update(args):
    "update a project"
    _cookiecutter(args, overwrite_if_exists=True)


def run(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        #usage='c4proj <command> ',
        prog='c4proj',
        description='... description'
    )
    #
    cmds = parser.add_subparsers(help='commands')
    def _add_cmd(fn, *arg_builders):
        name = fn.__name__
        desc = fn.__doc__
        cmd = cmds.add_parser(name, help=desc, description=desc)
        cmd.set_defaults(func=fn)
        for ab in arg_builders:
            ab(cmd)
        return cmd
    def _add_cfg(cmd):
        cmd.add_argument('cfg', type=str,
                         help="path to a c4proj cfg.yml file")
    #
    _add_cmd(create, _add_cfg)
    _add_cmd(update, _add_cfg)
    #
    if not args:
        args = sys.argv[1:]
    parsed_args = parser.parse_args(args)
    log(parsed_args)
    parsed_args.func(parsed_args)
    return parsed_args


if __name__ == "__main__":
    run()
