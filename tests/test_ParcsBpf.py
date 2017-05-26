# Class in test
from nfq.xfp.parcs import ParcsBpf


def test_parcs_ParcsBpf():
    # first open ParcsBpf file:
    test = ParcsBpf('tests/files/PARCS.bpf')
    assert test.get_var_data('bank-0145')[0][1] == 48
