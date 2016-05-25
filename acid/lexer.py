#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines some types and functions for tokenizing a given code string.
"""

__all__ = ['TokenType', 'Token', 'tokenize']


import re
from enum import Enum

from acid.types import SourcePos
from acid.exception import ParseError


# derive from Enum to allow iteration through the token types
class TokenType(Enum):
	"""
	Lists every token type and stores their regular expression pattern.
	"""

	def __init__(self, pattern):
		self.regex = re.compile(pattern)

	DEFINE = r'define'
	LAMBDA = r'lambda'
	LPAREN, RPAREN = r'\(', r'\)'
	FLOAT_LITERAL = r'\d+\.\d+'
	INT_LITERAL = r'\d+'
	ATOM = r"[\w+\-'*/:,$<>=~#&|@ç^_%!?.]+"
	WHITESPACE = r'\s+'


class Token:
	"""
	Concrete lexeme type.
	"""

	def __init__(self, type, value, pos):
		self.type = type
		self.value = value
		self.pos = pos

	def __repr__(self):
		fmt = 'Token(type={tok.type}, value={tok.value!r}, pos={tok.pos!s})'
		return fmt.format(tok=self)


def tokenize(code):
	"""
	Chop the given string in Token instances.
	"""
	
	cursor = SourcePos(line=1, column=1)

	while code:
		# iterates over all TokenType instances in order
		for token_type in TokenType:
			match = token_type.regex.match(code)

			if match is not None:
				# pop the matched string
				code = code[match.end():]

				# skipping whitespace
				if token_type is not TokenType.WHITESPACE:
					# value is assigned to the entire match string
					value = match.group(0)

					# update cursor position (line and column index)
					cursor.feed(value)

					# copy the cursor to avoid unwanted reference
					pos = cursor.copy()

					yield Token(token_type, value, pos)

				break
		else:
			# when every token type has been tried
			raise ParseError(pos, "Failed to tokenize code")
