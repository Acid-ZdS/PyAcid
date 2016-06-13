#!/usr/bin/env python3.4
# coding: utf-8

"""
Entry for the Acid parser/lexer/compiler/interpreter.

Contributors: myrma
"""

import os
import argparse

from acid.parser import Parser, tokenize
from acid.compiler import Compiler


arg_parser = argparse.ArgumentParser(
	prog='acid',
	description="Tokenize, parse, compile or execute the given input file"
)
arg_parser.add_argument('path', metavar='PATH', help='the input file')
arg_parser.add_argument('--lex', '-l', dest='lex', action='store_true',
                   		help='tokenize the given input file')
arg_parser.add_argument('--ast', '-a', dest='ast', action='store_true',
                   		help='parse the given input file')
arg_parser.add_argument('--compile', '-c', dest='comp', action='store_true',
                   		help='compile the given input file')


def main(path, lex=False, ast=False, comp=False):
	path = os.path.abspath(path)

	if lex:
		with open(path) as file:
			code = file.read()

			for token in tokenize(code):
				print(token)

	elif ast:
		parser = Parser.from_file(path)
		tree = parser.run()
		print(tree)

	elif comp:
		compiler = Compiler.from_file(path)
		compiler.dump()

	else:
		if path.endswith('.acidc'):
			Compiler.execute_compiled_file(path)
		else:
			compiler = Compiler.from_file(path)
			compiler.execute()

if __name__ == '__main__':
	args = arg_parser.parse_args()
	main(**args.__dict__)
