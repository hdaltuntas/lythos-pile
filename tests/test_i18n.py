"""The two languages stay complete and in step."""
import re

from lythospile.i18n import ENTRIES, TRANSLATIONS, t
from lythospile.web.strings import REUSED, SHELL


def test_every_entry_has_both_languages():
    for key, pair in ENTRIES.items():
        assert isinstance(pair, tuple) and len(pair) == 2, key
        assert pair[0] and pair[1], key


def test_the_placeholders_are_the_same_in_both_languages():
    for key, (en, tr) in ENTRIES.items():
        assert set(re.findall(r"\{(\w+)", en)) == set(re.findall(r"\{(\w+)", tr)), key


def test_the_shell_reuses_only_keys_that_exist():
    for key in REUSED:
        assert key in TRANSLATIONS["en"], key
    for key, pair in SHELL.items():
        assert len(pair) == 2 and all(pair), key


def test_an_unknown_key_comes_back_as_itself():
    assert t("en", "no_such_key") == "no_such_key"


def test_turkish_is_actually_turkish():
    assert t("tr", "res_title") == "KAZIK TAŞIMA GÜCÜ SONUÇLARI"


def test_every_method_and_choice_has_a_name():
    from lythospile.config import (
        CLAY_METHODS,
        EFFICIENCY_METHODS,
        SOCKET_BASE_METHODS,
        SOCKET_SIDE_METHODS,
        TIP_METHODS,
    )
    for lang in ("en", "tr"):
        L = TRANSLATIONS[lang]
        for key in CLAY_METHODS + TIP_METHODS:
            assert f"method_{key}" in L
        for key in EFFICIENCY_METHODS:
            assert f"eff_{key}" in L
        for key in SOCKET_SIDE_METHODS:
            assert f"side_{key}" in L
        for key in SOCKET_BASE_METHODS:
            assert f"base_{key}" in L


def test_every_warning_the_engines_raise_has_a_text():
    import pathlib
    source = "".join(p.read_text(encoding="utf-8")
                     for p in pathlib.Path(__file__).parent.parent.joinpath("lythospile")
                     .glob("*.py"))
    for key in set(re.findall(r'message\("(\w+)"', source)) | \
            set(re.findall(r'PileError\("(\w+)"', source)):
        assert key in ENTRIES, key
