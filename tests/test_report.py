"""The calculation report in all three formats, and the figures it carries."""
import copy
import zipfile

import pytest
from matplotlib.figure import Figure

from lythospile import render, report
from lythospile.config import DEFAULT_CONFIG
from lythospile.engine import PileAnalysis
from lythospile.plotting import PLOT_KEYS, SOCKET_PLOT_KEYS, Plotter, SocketPlotter
from lythospile.socket import SocketAnalysis


@pytest.fixture(scope="module")
def analysis():
    a = PileAnalysis(DEFAULT_CONFIG)
    a.run()
    return a


@pytest.fixture(scope="module")
def socket():
    s = SocketAnalysis(DEFAULT_CONFIG)
    s.run()
    return s


@pytest.mark.parametrize("theme", ["light", "dark", "paper"])
def test_every_figure_draws_in_every_theme(analysis, socket, theme):
    for key in PLOT_KEYS:
        fig = Figure(figsize=(8, 6))
        Plotter(analysis, "en", theme).draw(key, fig)
        assert fig.axes, key
    for key in SOCKET_PLOT_KEYS:
        fig = Figure(figsize=(8, 6))
        SocketPlotter(socket, "tr", theme).draw(key, fig)
        assert fig.axes, key


def test_the_figures_come_out_as_png(analysis, socket):
    png = render.figure_to_png(render.analysis_figure(analysis, "length", "tr"))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    png = render.figure_to_png(render.socket_figure(socket, "socket_side", "en"))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_an_unknown_figure_is_refused(analysis, socket):
    with pytest.raises(ValueError):
        render.analysis_figure(analysis, "nonsense")
    with pytest.raises(ValueError):
        render.socket_figure(socket, "section")


def test_every_case_draws_its_figures():
    """The less common paths: a single pile, a square pile in clay, water at the
    surface, no critical depth, the other methods."""
    cases = [
        {"group": {"nx": 1, "ny": 1}},
        {"pile": {"shape": "square", "L": 12.0}, "options": {"clay_method": "lambda",
                                                             "tip_method": "vesic"}},
        {"groundwater": {"depth": 0.0}, "options": {"critical_depth": False}},
        {"group": {"nx": 4, "ny": 2, "sy": 3.0}, "settlement": {"group_method": "meyerhof"}},
        {"options": {"tip_method": "janbu", "clay_method": "beta"}},
    ]
    for changes in cases:
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        for section, values in changes.items():
            cfg[section].update(values)
        a = PileAnalysis(cfg)
        a.run()
        for key in PLOT_KEYS:
            Plotter(a, "en", "light").draw(key, Figure(figsize=(8, 6)))


def test_the_html_report_is_self_contained(analysis, socket, tmp_path):
    path = tmp_path / "r.html"
    report.export_html(str(path), analysis, "en", socket=socket)
    text = path.read_text(encoding="utf-8")
    assert "data:image/png;base64," in text
    for word in ("Meyerhof", "Vesić", "Janbu", "Converse–Labarre", "Block failure",
                 "Equivalent raft", "Rock-socketed pile", "Horvath &amp; Kenney",
                 "Randolph &amp; Wroth", "Method notes"):
        assert word in text, word


def test_the_sections_are_numbered_in_order(analysis, socket):
    text = report.build_html(analysis, "en", {}, socket=socket)
    numbers = [int(n) for n in __import__("re").findall(r"<h2[^>]*>(\d+)\. ", text)]
    assert numbers == list(range(1, len(numbers) + 1))


def test_a_socket_alone_makes_a_report(socket, tmp_path):
    path = tmp_path / "s.pdf"
    report.export_pdf(str(path), None, "tr", socket=socket)
    assert path.read_bytes()[:5] == b"%PDF-"
    with pytest.raises(ValueError):
        report.build_html(None, "en", {})


def test_the_turkish_report_is_in_turkish(analysis, tmp_path):
    path = tmp_path / "r.html"
    report.export_html(str(path), analysis, "tr")
    text = path.read_text(encoding="utf-8")
    assert "Tek kazığın taşıma gücü" in text and "Yöntem notları" in text


def test_the_pdf_report(analysis, socket, tmp_path):
    path = tmp_path / "r.pdf"
    report.export_pdf(str(path), analysis, "tr", socket=socket)
    data = path.read_bytes()
    assert data[:5] == b"%PDF-" and len(data) > 50_000


def test_the_word_report(analysis, tmp_path):
    path = tmp_path / "r.docx"
    report.export_docx(str(path), analysis, "en")
    with zipfile.ZipFile(path) as archive:
        body = archive.read("word/document.xml").decode("utf-8")
    assert "Capacity of a single pile" in body
