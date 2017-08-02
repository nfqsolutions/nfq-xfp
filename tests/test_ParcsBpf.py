# Class in test
from nfq.xfp.parcs import ParcsBpf


def test_parcs_ParcsBpf():
    # first open ParcsBpf file:
    test = ParcsBpf('tests/files/PARCS.bpf')
    #We allow a small difference due to different PARCS versions
    assert abs(test.get_var_data("tcool-A06R0024")[-1][1]- 287.47552490234375) <1.0
