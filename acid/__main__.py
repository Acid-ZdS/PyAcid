#!/usr/bin/env python3.4
# coding: utf-8

"""
Entry for the Acid parser/lexer/compiler/interpreter.

Contributors: myrma
"""

import os
import signal
import argparse

from acid.parser import Parser, tokenize
from acid.compiler import Compiler
from acid.exception import ParseError
from acid.repl import REPL


class Call(argparse.Action):
	def __init__(self, func, *args, **kwds):
		super().__init__(*args, **kwds)
		self.func = func

	def __call__(self, parser, namespace, values, option_string=None):
		setattr(namespace, self.dest, self.func(values))


def execute(path):
	if path.endswith('.acidc'):
		Compiler.execute_compiled_file(path)
	else:
		compiler = Compiler.from_file(path)
		compiler.execute()


def lex(path):
	with open(path) as file:
		code = file.read()

		try:
			token_queue = tokenize(code)
		except ParseError as err:
			print(err)
		else:
			for token in tokenize(code):
				print(token)


def parse(path):
	parser = Parser.from_file(path)

	try:
		tree = parser.run()
	except ParseError as err:
		print(err)
	else:
		print(tree)


def compile(path):
	compiler = Compiler.from_file(path)
	compiler.dump()


def interactive(path=None):
	repl = REPL()
	signal.signal(signal.SIGINT, lambda *_: repl.quit())

	if path is not None:
		repl.load(path)

	repl.run()


arg_parser = argparse.ArgumentParser(
	prog='acid',
	description="Tokenize, parse, compile or execute the given input file"
)

action = arg_parser.add_mutually_exclusive_group()

action.add_argument(
	'--exec', '-e',
	dest='path',
	metavar='PATH',
	action=Call,
	func=execute,
	help='executes the given file')

action.add_argument(
	'--lex', '-l',
	dest='path',
	metavar='PATH',
	action=Call,
	func=lex,
	help='tokenize the given file')

action.add_argument(
	'--parse', '--ast', '-p',
	dest='path',
	metavar='PATH',
	action=Call,
	func=parse,
	help='parse the given file')

action.add_argument(
	'--compile', '-c',
	dest='path',
	metavar='PATH',
	action=Call,
	func=compile,
	help='compile the given file')

action.add_argument(
	'--repl', '-i',
	dest='path',
	metavar='PATH',
	nargs='?',
	action=Call,
	func=interactive,
	default=None,
	help='starts an interactive interpreter')


if __name__ == '__main__':
	arg_parser.parse_args()
