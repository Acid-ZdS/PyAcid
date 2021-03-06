#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines some types and functions for tokenizing a given code string.

Contributors: myrma
"""

__all__ = ['TokenType', 'Token', 'tokenize']


import re
from enum import Enum
from itertools import dropwhile

from acid.parser.types import SourcePos, SourceSpan
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
	IF = r'if'
	HASTYPE = r'(::|hastype)'
	LINE_COMMENT = r'//'
	COMMENT_START, COMMENT_END = r'/\*', r'\*/'
	LPAREN, RPAREN = r'\(', r'\)'
	CHAR_LITERAL = r"'([^'\\]|\\.)'"
	STRING_LITERAL = r'"([^"\\]|\\.)*"'
	FLOAT_LITERAL = r'\d+\.\d+'
	INT_LITERAL = r'\d+'
	ATOM = r"[\w+\-*/:,$<>=~#&|@ç^_%!?.]+"
	WHITESPACE = r'\s+'


class Token:
	"""
	Concrete lexeme type.
	"""

	def __init__(self, type, value, span):
		self.type = type
		self.value = value
		self.span = span

	def __repr__(self):
		fmt = 'Token(type={tok.type}, value={tok.value!r}, span={tok.span!r})'
		return fmt.format(tok=self)

	@property
	def pos(self):
		return self.span.start


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
				# source position before the code is consumed
				startpos = cursor.copy()

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
						endpos = cursor.copy()

						span = SourceSpan(startpos, endpos)
						tok = Token(token_type, value, span)
						yield tok

				break
		else:
			# when every token type has been tried
			raise ParseError(code, cursor, "Failed to tokenize code")
