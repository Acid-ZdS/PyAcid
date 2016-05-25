#!/usr/bin/env python3.4
# coding: utf-8

"""
Entry for the Acid parser/lexer/compiler/interpreter.

Contributors: myrma
"""

import argparse

from acid import tokenize, parse


arg_parser = argparse.ArgumentParser(
	prog='Acid compiler',
	description="Tokenize, parse, compile or execute the given input file"
)
arg_parser.add_argument('path', metavar='PATH', help='the input file')
arg_parser.add_argument('--lex', '-l', dest='lex', action='store_true',
                   		help='tokenize the given input file')
arg_parser.add_argument('--ast', '-a', dest='ast', action='store_true',
                   		help='parse the given input file')
arg_parser.add_argument('--compile', '-c', dest='compile', action='store_true',
						help='compile the given input file')


def main(path, lex=False, ast=False, compile=False):
	with open(path) as file:
		code = file.read()

		if lex:
			for token in tokenize(code):
				print(token)

		elif ast:
			tree = parse(code, path)
			print(tree)

		elif compile:
			raise NotImplementedError('Compiling is not implemented yet')

		else:
			raise NotImplementedError('The interpreter is not implemented yet')
			# when the interpreter will be implemented
			# execute(code)

if __name__ == '__main__':
	args = arg_parser.parse_args()
	main(**args.__dict__)
