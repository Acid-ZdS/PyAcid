#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines the builtin values of Acid.

Contributors: myrma
"""

import operator as op
from functools import reduce


default_env = {
	'+': lambda *xs: reduce(op.add, xs),  # or just `sum`
	'-': op.sub,
	'*': lambda *xs: reduce(op.mul, xs),
	'/': op.truediv,
	'**': op.pow,
	'div': op.floordiv,
	'mod': op.mod,
	'==': op.eq,
	'!=': op.ne,
	'<': op.lt,
	'<=': op.le,
	'>': op.gt,
	'>=': op.ge,
	'and': op.and_,
	'xor': op.xor,
	'or': op.or_,
	'not': op.not_,
	'<<': op.lshift,
	'>>': op.rshift,
	'~': op.invert,
	'#': op.getitem,
	'#=': op.setitem,
	'#~': op.delitem,
	'negate': op.neg,
	'print': print,
}
