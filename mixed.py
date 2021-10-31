import re
from fractions import Fraction

__all__ = ['MixedNumber']

_MIXED_NUMBER_FORMAT = re.compile(r"""
    \A\s*                      # optional whitespace at the start, then
    (?P<sign>[-+]?)            # an optional sign, then
    (?=\d|\.\d)                # lookahead for digit or .digit
    (?:                        # optional whole number:
        (?P<whole>\d+)         # which is a number
        \s+                    # followed by whitespace
        (?=\d+/)               # followed by a numerator and /
    )?
    (?P<num>\d*)               # numerator (possibly empty)
    (?:                        # followed by
       (?:/(?P<denom>\d+))?    # an optional denominator
    |                          # or
       (?:\.(?P<decimal>\d*))? # an optional fractional part
       (?:E(?P<exp>[-+]?\d+))? # and optional exponent
    )
    \s*\Z                      # and optional whitespace to finish
""", re.VERBOSE | re.IGNORECASE)

class MixedNumber(Fraction):
    """This class implements mixed fractions.

    In the three-argument form of the constuctor, MixedNumber(1, 2, 3) will
    produce a rational number equivalent to 1 + 2/3. All arguments must be
    rational. 

    MixedNumbers may also be constructed from:

        - strings of the form '123 567/123'

        - any other inputs accepted by Fraction

    """

    def __new__(cls, whole, numerator=None, denominator=None):
        if isinstance(whole, str):
            m = _MIXED_NUMBER_FORMAT.match(whole)
            if m is None:
                raise ValueError('Invalid literal or fraction: %r' % whole)

            whole = int(m.group('whole') or '0')
            numerator = int(m.group('num') or '0')
            denom = m.group('denom')
            if denom:
                self = super().__new__(cls,
                                       whole + Fraction(numerator, int(denom)))
            else:
                self = super().__new__(cls,
                                       whole + Fraction(numerator))
            if m.group('sign') == '-':
                self = self * -1
            return self
        if numerator or denominator:
            return super().__new__(cls, numerator, denominator) + whole
        else:
            return super().__new__(cls, whole)

    def __str__(self):
        out = ""
        res = self
        # if we're negative prefix with '-' then continue with positive part
        if res < 0:
            out += '-'
            res = -res
        # if we have a whole part, prefix with 'whole ' and continue with
        # fractional part
        if res >= 1:
            whole = res.numerator // res.denominator
            out += str(whole) + ' '
            res = res - whole
        # if we have a fractional part, print that
        if res != 0:
            out += str(res)
        # if out is still empty print 0
        if out == '':
            out = '0'
        return out

    def __add__(self, other):
        res = super().__add__(other)
        return self.__class__(res)

    def __sub__(self, other):
        res = super().__sub__(other)
        return self.__class__(res)

    def __mul__(self, other):
        res = super().__mul__(other)
        return self.__class__(res)

    def __div__(self, other):
        res = super().__div__(other)
        return self.__class__(res)
