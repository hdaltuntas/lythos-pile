"""Settlement of a pile and of a pile group, by hand."""
import math

import pytest

from lythospile import settlement as stl
from lythospile.profile import Profile


def test_vesic_single_pile_term_by_term():
    got = stl.single_pile(Qw=600.0, Qs=900.0, Qb=300.0, L=15.0, D=0.5, Ap=0.19635,
                          perimeter=1.5708, Ep=30000.0, Es_base=40.0, nu_base=0.3,
                          Es_shaft=20.0, nu_shaft=0.3, xi=0.5)
    Qws, Qwb = 450.0, 150.0
    s1 = (Qwb + 0.5 * Qws) * 15.0 / (0.19635 * 30e6)
    s2 = (Qwb / 0.19635) * 0.5 * (1 - 0.09) * 0.85 / 40_000.0
    Iws = 2 + 0.35 * math.sqrt(30.0)
    s3 = Qws / (1.5708 * 15.0) * 0.5 * (1 - 0.09) * Iws / 20_000.0
    assert got["s1"] == pytest.approx(s1)
    assert got["s2"] == pytest.approx(s2)
    assert got["s3"] == pytest.approx(s3)
    assert got["s"] == pytest.approx(s1 + s2 + s3)


def test_a_clay_consolidates_on_its_recompression_line_first():
    clay = {"behaviour": "cohesive", "Cc": 0.3, "Cr": 0.05, "e0": 1.0, "OCR": 2.0,
            "E": 10.0, "nu": 0.3}
    below = stl.layer_compression(clay, 100.0, 50.0, 2.0)
    assert below["s"] == pytest.approx(2.0 * 0.05 * math.log10(1.5) / 2.0)
    above = stl.layer_compression(clay, 100.0, 200.0, 2.0)
    assert above["s"] == pytest.approx(2.0 * (0.05 * math.log10(2.0)
                                              + 0.3 * math.log10(1.5)) / 2.0)


def test_a_sand_compresses_with_its_constrained_modulus():
    sand = {"behaviour": "granular", "E": 30.0, "nu": 0.3}
    M = 30_000.0 * 0.7 / (1.3 * 0.4)
    assert stl.layer_compression(sand, 100.0, 60.0, 1.0)["s"] == pytest.approx(60.0 / M)


def test_the_equivalent_raft_spreads_and_stops_where_the_stress_is_small():
    layers = [{"name": "sand", "thickness": 60.0, "behaviour": "granular", "gamma": 19.0,
               "gamma_sat": 20.0, "E": 50.0, "nu": 0.3}]
    profile = Profile(layers, 100.0, 9.81)
    got = stl.equivalent_raft(profile, 5000.0, 4.0, 4.0, 10.0)
    first = got["rows"][0]
    widen = (first["z"] - 10.0) / 2.0
    assert first["dsigma"] == pytest.approx(5000.0 / (4.0 + widen) ** 2)
    assert got["z_stop"] < 60.0 and not got["reached_bottom"]
    assert got["s"] == pytest.approx(sum(row["s"] for row in got["rows"]))


def test_vesic_and_meyerhof_group_rules():
    assert stl.vesic_group(0.01, 4.0, 1.0) == pytest.approx(0.02)
    got = stl.meyerhof_group(200.0, 4.0, 20.0, 25.0)
    assert got["I"] == 0.5                                    # 1 − 20/32 < 0.5
    assert got["s"] == pytest.approx(0.96 * 200 * 2.0 * 0.5 / 25.0 / 1000.0)
