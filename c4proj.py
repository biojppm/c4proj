import sys
import os
import re
import shutil
from cookiecutter.main import cookiecutter
import ruamel.yaml as yaml
import json
import argparse
import git


def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def load_config(path):
    with open(path, 'r') as stream:
        data = yaml.safe_load(stream)
    return set_defaults(data)


def _cookiecutter(args, cfg, **more_args):
    tpl = './cookiecutter-c4proj'
    with open(os.path.join(tpl, "cookiecutter.json"), "w") as json_file:
        json.dump(cfg, json_file, indent=2)
    cookiecutter(tpl, no_input=True, **more_args)


def set_defaults(cfg):
    def default_to(item, default):
        d = cfg.get(item)
        if ((d is None) or (str(d) == "")):
            log(f"cfg: item '{item}' empty or not set. defaulting to '{default}'")
            cfg[item] = default
    name = cfg['name']
    default_to('url', cfg['repo'])
    default_to('slug', re.sub(r'[- ]', '_', name.lower()))
    default_to('slugu', re.sub(r'[- ]', '_', name.upper()))
    default_to('slugc', re.sub(r'[- ]', '', name.capitalize()))
    default_to('slugk', name.lower().replace(' ', '-'))
    default_to('author_and_email', f'{cfg["author"]} <{cfg["email"]}>')
    return cfg


def check_clean_repo(path, cmd):
    try:
        repo = git.Repo(path)
        if repo.is_dirty():
            return DirtyRepo(path, cmd)
    except git.exc.InvalidGitRepositoryError:
        pass
        raise NotARepo(path, cmd)


def proj_path(path):
    return path


def gencfg_path(args, member):
    out = None
    if hasattr(args, member):
        out = getattr(args, member)
    if out is None:
        out = "."
    out = os.path.abspath(out)
    return out


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def gencfg(args):
    """create a c4proj cfg.yml configuration file for subsequent use in
    creating a project"""
    src = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join(src, "cfg.yml")
    check_file(exists, src)
    dst = gencfg_path(args, "output")
    if args.mkdir:
        if not os.path.exists(dst):
            log(f"creating directory: '{dst}'")
            os.makedirs(dst)
    check_dir(exists, dst)
    dst = os.path.join(dst, "cfg.yml")
    if not args.overwrite:
        check_file(not_exists, dst)
    shutil.copyfile(src, dst)
    check_file(exists, dst)
    log(f"""Generated config file:

  {dst}

Edit the file and run "c4proj create" to create the project.""")


def create(args):
    "create a project"
    cwd = os.getcwd()
    if not args.cfg:
        args.cfg = os.path.join(cwd, "cfg.yml")
    check_file(exists, args.cfg)
    cfg = load_config(args.cfg)
    #
    if not args.output:
        args.output = os.path.join(cwd, cfg['name'])
    check_dir(not_exists, args.output)
    #
    _cookiecutter(args, cfg, output_dir=os.path.dirname(args.output))
    #
    with open(os.path.join(args.output, "cfg.yml"), "w") as stream:
        yml = yaml.YAML()
        yml.width = 128
        yml.dump(cfg, stream)


def update(args):
    "update a project"
    if not args.proj:
        args.proj = os.cwd()
    args.proj = os.path.abspath(args.proj)
    check_clean_repo(args.proj, "update")
    cfg = os.path.join(args.proj, "cfg.yml")
    check_file(exists, cfg)
    _cookiecutter(args, cfg,
                  output_dir=os.path.dirname(args.proj),
                  overwrite_if_exists=True)


# -----------------------------------------------------------------------------

def run(args=None):
    parser = argparse.ArgumentParser(
        prog='c4proj',
        description='... description'
    )
    #
    cmds = parser.add_subparsers(help='commands')
    def _add_cmd(cmd_fn, *arg_builders):
        name = cmd_fn.__name__
        desc = cmd_fn.__doc__
        cmd = cmds.add_parser(name, help=desc, description=desc)
        cmd.set_defaults(func=cmd_fn)
        for ab in arg_builders:
            ab(cmd)
        return cmd
    #
    cmd = _add_cmd(gencfg)
    cmd.add_argument('output', type=str, help="directory to put the c4proj cfg.yml file")
    cmd.add_argument('-m', '--mkdir', action="store_true", help="create the directory if it doesn't exist")
    cmd.add_argument('-w', '--overwrite', action="store_true", help="overwrite an existing file")
    #
    cmd = _add_cmd(create)
    cmd.add_argument('cfg', type=str, help="path to an existing c4proj cfg.yml file")
    cmd.add_argument('-o', '--output', type=str, help="directory where to place the project")
    #
    cmd = _add_cmd(update)
    cmd.add_argument('proj', type=proj_path, help="path to an existing project directory")
    #
    if not args:
        args = sys.argv[1:]
    parsed_args = parser.parse_args(args)
    log(parsed_args)
    parsed_args.func(parsed_args)
    return parsed_args


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


class NotARepo(Exception):
    def __init__(self, path, cmd):
        super().__init__(f"Refuse to run command '{cmd}' in directory: not a repo: '{path}'")


class DirtyRepo(Exception):
    def __init__(self, path, cmd):
        super().__init__(f"Refuse to run command '{cmd}' in a dirty repository: {path}")


class FileExists(Exception):
    def __init__(self, path):
        super().__init__(f"File already exists: {path}")


class FileNotExists(Exception):
    def __init__(self, path):
        super().__init__(f"File not found: {path}")


class DirExists(Exception):
    def __init__(self, path):
        super().__init__(f"Directory already exists: {path}")


class DirNotExists(Exception):
    def __init__(self, path):
        super().__init__(f"Directory not found: {path}")


def check_file(exists_or_not_exists, path):
    if exists_or_not_exists:
        if not os.path.exists(path):
            raise FileNotExists(path)
    else:
        if os.path.exists(path):
            raise FileExists(path)


def check_dir(exists_or_not_exists, path):
    if exists_or_not_exists:
        if (not os.path.exists(path)) or (not os.path.isdir(path)):
            raise DirNotExists(path)
    else:
        if os.path.exists(path):
            raise DirExists(path)


exists = True
not_exists = False


if __name__ == "__main__":
    run()
