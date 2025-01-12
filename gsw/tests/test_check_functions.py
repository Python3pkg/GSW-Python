"""
Tests functions with pytest, using the machinery from check_functions.py
"""

import os
import pytest

import numpy as np
from numpy.testing import assert_allclose

import gsw
from gsw._utilities import Bunch
from check_functions import parse_check_functions

root_path = os.path.abspath(os.path.dirname(__file__))

# Function checks that we can't handle automatically yet.
blacklist = ['deltaSA_atlas',  # the test is complicated; doesn't fit the pattern.
             #'CT_from_entropy', # needs prior entropy_from_CT; don't have it in C
             #'CT_first_derivatives', # passes, but has trouble in "details";
                                      # see check_functions.py
             #'entropy_second_derivatives', # OK now; handling extra parens.
             #'melting_ice_into_seawater',  # OK now; fixed nargs mismatch.
             ]

# We get an overflow from ct_from_enthalpy_exact, but the test passes.
cv = Bunch(np.load(os.path.join(root_path, 'gsw_cv_v3_0.npz')))
cf = Bunch()

d = dir(gsw)
funcnames = [name for name in d if '__' not in name]

mfuncs = parse_check_functions(os.path.join(root_path, 'gsw_check_functions_save.m'))
mfuncs = [mf for mf in mfuncs if mf.name in d and mf.name not in blacklist]
mfuncnames = [mf.name for mf in mfuncs]


@pytest.fixture(scope='session', params=mfuncs)
def cfcf(request):
    return cv, cf, request.param


def test_check_function(cfcf):
    cv, cf, mfunc = cfcf
    mfunc.run(locals())
    if mfunc.exception is not None or not mfunc.passed:
        print(('\n', mfunc.name))
        print(('  ', mfunc.runline))
        print(('  ', mfunc.testline))
        if mfunc.exception is None:
            mfunc.exception = ValueError('Calculated values are different from the expected matlab results.')
        raise mfunc.exception
    else:
        print((mfunc.name))
        assert mfunc.passed
