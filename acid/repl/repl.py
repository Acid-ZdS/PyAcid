#!/usr/bin/env python3.4
# coding: utf-8

"""
acid.repl implements a read-eval-print loop for Acid.

Contributors: myrma
"""

import os
import sys
import inspect
import traceback
from collections import OrderedDict

from acid.repl.command import REPLCommand
from acid.repl.syntax import parse_repl_line
from acid.compiler import Compiler
from acid.parser import Parser
from acid.prelude import default_env
from acid.exception import ParseError

DEFAULT_REPL_HEADER = """

       ____,──┬───────._
      ╱  '  _╱    │     ╲
    ╱   ,  ╱ ╲__  │  __╱ ╲
   ╱ `    │     ╲_│_╱     │
  │   ' . │______╱ ╲______│
  │'  .   │     ╱╲ ╱╲     │
   ╲   .  │    ╱  │  │    │
    ╲  ,   ╲ _╱   │   ╲ _╱
      ╲  .  '╲_   │   _╱
       '───.____╲_│__╱


Acid - Implémentation Python
Un projet de la communauté ZesteDeSavoir
"""


class REPL:
    """
    A read-eval-print loop that interactively runs Acid code.
    """

    aliases = {}
    commands = OrderedDict()

    def __init__(self, path=None, prelude=default_env):
        self.path = path
        self.default_env = default_env.copy()
        self.environment = default_env.copy()
        self.cmd_count = 0
        self.prompt = '> '
        self.header = DEFAULT_REPL_HEADER
        self.running = False

    @classmethod
    def get_command(cls, name):
        """
        Gets the function associated with the command from its name or alias.
        """

        try:
            return cls.commands[name]
        except KeyError:
            realname = cls.aliases[name]
            return cls.commands[realname]

    @classmethod
    def register(cls, name, *aliases):
        """
        Binds a function to a command by name.
        """

        def _decorator_wrapper(fn):
            cls.commands[name] = fn

            for alias in aliases:
                cls.aliases[alias] = name

            return fn

        return _decorator_wrapper

    def load(self, path):
        """
        Loads a path into the current environment.
        """

        print('Loading file "{}"'.format(path))

        self.environment = self.default_env.copy()

        with open(path) as load_file:
            compiler = Compiler.from_file(path)
            compiler.load(self.environment)
            self.path = path

    def reload(self):
        """
        Reloads the current path into the environment.
        """
        if self.path is not None:
            self.load(self.path)
        else:
            print('Error: No module loaded. Type `:load [file]` to load one.')

    def read_command(self):
        """
        Reads a user-typed REPL command from the input stream.
        """

        try:
            inp = input(self.prompt.format(**self.__dict__))
        except EOFError:
            print('')
            inp = ''

        cmd = parse_repl_line(inp)

        return cmd

    def quit(self):
        """
        Stops the REPL and displays an exit message.
        """

        self.running = False
        print('Goodbye.')

    def run(self, display_header=True):
        """
        Runs the REPL.
        """

        self.running = True

        if display_header:
            print(self.header)

        while self.running:
            try:
                cmd = self.read_command()
                res = cmd.execute(self)
            except KeyboardInterrupt:
                print('Interrupted.')
            except Exception as exc:
                if self.path is None:
                    msg = 'File <stdin>, input #{repl.cmd_count}'.format(repl=self)
                else:
                    msg = 'File "{repl.path}", input #{repl.cmd_count}'.format(repl=self)

                print(msg)
                print('An error has ocurred:')
                print('{}: {}'.format(
                    type(exc).__name__,
                    ''.join(map(str, exc.args))
                ))
            else:
                self.cmd_count += 1

                if res is not None:
                    print(res)


REPL.register('load', 'l')(REPL.load)
REPL.register('reload', 'r')(REPL.reload)
REPL.register('quit', 'q')(REPL.quit)


@REPL.register('prompt')
def set_prompt(self, string):
    """
    Sets the REPL prompt.
    """

    if isinstance(string, str):
        self.prompt = string
    else:
        print('`:prompt`: expected string')


@REPL.register('clear', 'cls')
def clear(self):
    """
    Clears the console screen.
    """

    os.system('cls' if os.name == 'nt' else 'clear')

@REPL.register('help', 'h')
def help(self, command=None):
    """
    Lists all available command from the prompt or show help for a given command.
    """

    if command is None:
        print('Commands available from the prompt:', end='\n' * 2)

        print(*map(_get_command_desc, self.commands), sep='\n')
    else:
        print('Showing help for command {!r}'.format(command))
        print(_get_command_desc(command))

        aliases = []

        for alias, name in self.aliases.items():
            if name == command:
                aliases.append(alias)

        if len(aliases) == 1:
            print('Alias: {!r}'.format(aliases[0]))
        elif len(aliases) > 1:
            print('Aliases:', ', '.join(map(repr, aliases)))


def _get_command_desc(name):
    try:
        fn = REPL.get_command(name)
    except KeyError:
        print('Error: command {!r} is not defined.'.format(name))

    if fn.__doc__ is not None:
        doc = fn.__doc__.strip()
    else:
        doc = 'No documentation available for this command'

    arg_desc = ''
    sig = inspect.signature(fn)

    # ignore the self parameter
    for pname, param in list(sig.parameters.items())[1:]:
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if param.default == inspect._empty:
                arg_desc += '<{}> '.format(pname)
            elif param.default is None:
                arg_desc += '[{}] '.format(pname)
            else:
                arg_desc += '[{}={!r}] '.format(pname, param.default)
        elif param.kind == inspect.Parameter.POSITIONAL_ONLY:
            arg_desc += '[{} ...] '.format(pname)
        else:
            # dirty :(
            pass

    desc = ':{name} {args}'.format(
        name=name,
        args=arg_desc
    )
    return '{desc:<30}\t\t{doc}'.format(
        desc=desc,
        doc=doc
    )
