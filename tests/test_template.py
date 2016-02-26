#!/usr/bin/env python

from __future__ import print_function
import unittest
from numpy.testing import assert_almost_equal as aa_eq

class TestSomething(unittest.TestCase):

    def test_something(self):
        a = [1., 2., 4.]
        b = [1.000000000001, 2., 4.]
        aa_eq(a, b)


if __name__ == "__main__":
    unittest.main()
