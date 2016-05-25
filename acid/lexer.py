#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines some types and functions for tokenizing a given code string.
"""

__all__ = ['TokenType', 'Token', 'tokenize']


import re
from enum import Enum
from itertools import dropwhile

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
	LINE_COMMENT = r'//'
	COMMENT_START, COMMENT_END = r'/\*', r'\*/'
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

				# value is assigned to the entire match string
				value = match.group(0)

				# update cursor position (line and column index)
				cursor.feed(value)

				if token_type == TokenType.LINE_COMMENT:
					# drop every character until newline
					code = ''.join(dropwhile(lambda c: c != '\n', code))

				elif token_type == TokenType.COMMENT_START:
					# test if the code matches a comment ending token
					m = TokenType.COMMENT_END.regex.match(code)

					# while the comment block is not ended
					while m is None:
						# feed a character from the comment string
						cursor.feed(code[0])

						# pop a single character
						code = code[1:]

						# retest if the code matches a comment ending token
						m = TokenType.COMMENT_END.regex.match(code)

					# pop the matched string
					code = code[m.end():]

				# skipping whitespace
				elif token_type is not TokenType.WHITESPACE:
						# copy the cursor to avoid unwanted reference
						pos = cursor.copy()

						yield Token(token_type, value, pos)

				break
		else:
			# when every token type has been tried
			raise ParseError(pos, "Failed to tokenize code")
