"""Rock-socketed piles: the correlations, the length, and the elastic settlement."""
import copy
import math

import pytest

from lythospile import socket as sk
from lythospile.config import DEFAULT_CONFIG, SOCKET_BASE_METHODS, SOCKET_SIDE_METHODS
from lythospile.errors import PileError


def test_every_side_correlation_by_hand_at_ten_mpa():
    qu, fc = 10.0, 40.0
    expected = {
        "rosenberg_journeaux": 0.375 * qu ** 0.515, "horvath_kenney": 0.21 * qu ** 0.5,
        "meigh_wolski": 0.22 * qu ** 0.6, "williams": 0.44 * qu ** 0.36,
        "reynolds_kaderabek": 0.30 * qu, "gupton_logan": 0.20 * qu,
        "rowe_armitage": 0.45 * qu ** 0.5, "carter_kulhawy": 0.20 * qu ** 0.5,
        "toh": 0.25 * qu, "zhang_einstein": 0.40 * qu ** 0.5,
        "oneill_reese": 0.65 * 0.8 * 0.101325 * math.sqrt(qu / 0.101325),
        "kulhawy_2005": 0.101325 * math.sqrt(qu / 0.101325),
    }
    assert set(expected) == set(SOCKET_SIDE_METHODS)
    for key, value in expected.items():
        assert sk.side_shear(key, qu, fc, 0.8) == pytest.approx(value), key


def test_carter_kulhawy_side_shear_is_the_normalised_lower_bound():
    # 0.20·√qu [MPa] is 0.63·pa·√(qu/pa)
    assert sk.side_shear("carter_kulhawy", 25.0, 40.0, 1.0) == pytest.approx(
        0.63 * 0.101325 * math.sqrt(25.0 / 0.101325), rel=0.01)


def test_the_aashto_side_shear_is_capped_by_the_concrete():
    capped = sk.side_shear("oneill_reese", 400.0, 1.0, 1.0)
    assert capped == pytest.approx(7.8 * 0.101325 * math.sqrt(1.0 / 0.101325))


def test_base_methods_by_hand():
    hb = sk.hoek_brown(60.0, 10.0, 0.0)
    got = {key: sk.base_resistance(key, 20.0, hb, 1.0, 2.0, 0.6, 1.0)["qb"]
           for key in SOCKET_BASE_METHODS}
    assert got["coates"] == pytest.approx(60.0)
    assert got["rowe_armitage"] == pytest.approx(54.0)
    assert got["aashto"] == pytest.approx(50.0)
    assert got["zhang_einstein"] == pytest.approx(4.83 * 20 ** 0.51)
    s, m = hb["s"], hb["mb"]
    assert got["carter_kulhawy"] == pytest.approx((math.sqrt(s) + math.sqrt(m * math.sqrt(s)
                                                                            + s)) * 20.0)
    K = (3 + 0.6) / (10 * math.sqrt(1 + 300 * 0.001 / 0.6))
    assert got["cfem"] == pytest.approx(3 * K * 1.8 * 20.0)


def test_rock_mass_modulus():
    assert sk.modulus_ratio_rqd(100.0) == pytest.approx(0.99)
    assert sk.modulus_ratio_rqd(40.0) == pytest.approx(0.15)
    assert sk.modulus_ratio_gsi(100.0, 0.0) == pytest.approx(
        0.02 + 1 / (1 + math.exp(-40 / 11)))
    assert sk.alpha_E(1.0) == pytest.approx(1.0) and sk.alpha_E(0.1) == pytest.approx(0.55)


def test_randolph_wroth_rigid_pile_limits():
    """A very stiff, very short pile tends to a rigid disk on the half-space."""
    got = sk.randolph_wroth(1000.0, 1e-3, 0.5, 1e5, 1e5, 0.25, 1e12)
    assert got["K"] == pytest.approx(4 * 1e5 * 0.5 / 0.75, rel=0.02)
    side = sk.randolph_wroth(1000.0, 10.0, 0.5, 1e5, 1e5, 0.25, 1e12, with_base=False)
    assert side["base_share"] == 0.0
    zeta = math.log((0.25 + 2.5 * 0.75 - 0.25) * 10.0 / 0.5)
    assert side["K"] == pytest.approx(1e5 * 0.5 * 2 * math.pi / zeta * 20.0, rel=0.02)


@pytest.fixture(scope="module")
def socket():
    return sk.analyse_socket(DEFAULT_CONFIG)


def test_the_required_length_carries_the_load(socket):
    res = socket.results
    at = socket.capacity(res["Ls_req"], res["fs_design"])
    assert at["Q_all"] == pytest.approx(socket.Q, rel=1e-3)
    for key, entry in res["side"].items():
        if math.isfinite(entry["Ls_req"]) and entry["Ls_req"] > 0:
            got = socket.capacity(entry["Ls_req"], entry["fs"])["Q_all"]
            assert got == pytest.approx(socket.Q, rel=1e-3), key


def test_a_stronger_correlation_needs_a_shorter_socket(socket):
    side = socket.results["side"]
    order = sorted(SOCKET_SIDE_METHODS, key=lambda key: side[key]["fs"])
    lengths = [side[key]["Ls_req"] for key in order]
    assert lengths == sorted(lengths, reverse=True)


def test_the_weak_rock_rules_leave_the_statistics_in_strong_rock(socket):
    res = socket.results
    assert not res["side"]["gupton_logan"]["in_range"]
    assert res["stats"]["n"] == len(SOCKET_SIDE_METHODS) - 3
    assert res["stats"]["upper"] < res["side"]["gupton_logan"]["fs"]


def test_weak_rock_keeps_every_rule():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["socket"]["qu"] = 3.0
    res = sk.analyse_socket(cfg).results
    assert res["stats"]["n"] == len(SOCKET_SIDE_METHODS)


def test_the_design_statistic_is_used(socket):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["socket"]["design"] = "lower"
    res = sk.analyse_socket(cfg).results
    assert res["fs_design"] == pytest.approx(res["stats"]["lower"])
    assert res["Ls_design"] > socket.results["Ls_design"]
    cfg["socket"]["design"] = "horvath_kenney"
    res = sk.analyse_socket(cfg).results
    assert res["fs_design"] == pytest.approx(res["side"]["horvath_kenney"]["fs"])


def test_without_the_base_the_socket_is_longer(socket):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["socket"]["base_design"] = "none"
    assert sk.analyse_socket(cfg).results["Ls_req"] > socket.results["Ls_req"]


def test_the_weight_counts_buoyant_below_the_water(socket):
    A = math.pi / 4
    dry = 2.5 - 1.0
    wet = (12.0 + 4.0) - 2.5
    assert socket.weight(4.0) == pytest.approx(A * (25.0 * dry + (25.0 - 9.81) * wet))


def test_settlement_falls_as_the_rock_stiffens(socket):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["socket"]["Ei"] = 60000.0
    stiffer = sk.analyse_socket(cfg).results["settlement"]
    softer = socket.results["settlement"]
    assert stiffer["rw"]["w"] < softer["rw"]["w"]
    assert softer["rw"]["total"] == pytest.approx(softer["rw"]["w"] + softer["shortening"])
    assert 0 < softer["rw"]["base_share"] < 1


def test_bad_socket_inputs_are_refused():
    for section, key, value in (("socket", "D", 0.0), ("socket", "qu", 0.0),
                                ("socket", "Q", -1.0), ("socket", "rock_depth", 0.5),
                                ("socket", "nu_r", 0.6)):
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg[section][key] = value
        with pytest.raises(PileError):
            sk.SocketAnalysis(cfg)
