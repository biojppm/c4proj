import sys
from cookiecutter.main import cookiecutter



def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def extra_context(args):
    return {k: getattr(args, k) for k in vars(args)}


def _cookiecutter(args, **more_args):
    cookiecutter(
        './cookiecutter-c4proj',
        no_input=True,
        extra_context=extra_context(args),
        **more_args
    )


def create(args):
    "create a project"
    _cookiecutter(args)


def update(args):
    "update a project"
    _cookiecutter(args, overwrite_if_exists=True)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def run(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        #usage='c4proj <command> ',
        prog='c4proj',
        description='... description'
    )
    #
    cmds = parser.add_subparsers(help='commands')
    def _add_cmd(fn, arg_builders=[]):
        name = fn.__name__
        desc = fn.__doc__
        cmd = cmds.add_parser(name, help=desc, description=desc)
        cmd.set_defaults(func=fn)
        for ab in arg_builders:
            ab(cmd, fn)
        return cmd
    #
    cmd = _add_cmd(create)
    cmd.add_argument('name',
                     type=str,
                     help='the name of the project to create')
    #
    cmd = _add_cmd(update)
    cmd.add_argument('name',
                     type=str,
                     help='the name of the project to create')
    #
    if not args:
        args = sys.argv[1:]
    parsed_args = parser.parse_args(args)
    log(parsed_args)
    parsed_args.func(parsed_args)
    return parsed_args


if __name__ == "__main__":
    run()
