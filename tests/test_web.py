"""
Tests for the browser interface: the session that does the work, and the HTTP
layer that serves it. The server is started on a port of its own and driven
with urllib, so what is tested is the same thing the browser talks to.
"""
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from lythospile import forms, render, summary
from lythospile.web import server as server_module
from lythospile.web.session import Session
from lythospile.web.strings import shell_strings

# --------------------------------------------------------------------------- #
#  The session
# --------------------------------------------------------------------------- #


def test_meta_carries_everything_the_page_needs():
    meta = Session().meta()
    assert meta["app"] == "Lythos Pile"
    assert meta["languages"] == ["en", "tr"]
    assert meta["schema"]["pile"]["groups"] and meta["schema"]["socket"]["groups"]
    assert meta["defaults"]["D"] > 0
    assert meta["figures"] == render.PLOT_KEYS
    assert meta["socket_figures"] == render.SOCKET_PLOT_KEYS
    assert all(meta["figure_labels"][key] for key in meta["figures"] + meta["socket_figures"])


def test_analyse_returns_cards_text_table_and_figures():
    result = Session().analyse(forms.defaults())
    assert result["ok"]
    assert [card["key"] for card in result["cards"]] == summary.CARD_KEYS
    assert f"{result['Q_ult_net']:,.0f}" in result["text"]
    assert len(result["table"]["rows"]) == 6          # five clay methods and the SPT rule
    assert sum(row["primary"] for row in result["table"]["rows"]) == 1


def test_the_socket_returns_cards_text_and_its_table():
    result = Session().analyse_socket(forms.defaults())
    assert [card["key"] for card in result["cards"]] == summary.SOCKET_CARD_KEYS
    assert len(result["table"]["rows"]) == 12
    assert "ROCK-SOCKETED PILE" in result["text"]


def test_a_refused_analysis_says_why_in_the_session_language():
    values = forms.defaults()
    values["Q"] = 0.0
    session = Session(lang="tr")
    with pytest.raises(ValueError) as caught:
        session.analyse(values)
    assert "Gruba gelen yük" in str(caught.value)


def test_a_figure_needs_an_analysis_first():
    with pytest.raises(ValueError):
        Session().plot("analysis", "section")
    with pytest.raises(ValueError):
        Session().plot("socket", "socket_side")


def test_a_study_runs_in_the_background_and_can_be_read_back():
    session = Session()
    values = forms.defaults()
    values["study_n"] = 30
    values["study_variables"] = [{"path": "loading.Q", "label": "Q", "mode": "dist",
                                  "dist": "normal", "mean": 10000.0, "cov": 0.1}]
    session.analyse(values)
    assert session.start_study(values)["ok"]
    for _ in range(200):
        if session.state()["job"] != "running":
            break
        time.sleep(0.05)
    payload = session.study_payload()
    assert payload["ok"] and payload["n"] == 30
    assert session.plot("study", "hist", "FS")[:4] == b"\x89PNG"


def test_a_study_without_variables_is_refused():
    assert not Session().start_study(forms.defaults())["ok"]


def test_a_foreign_file_is_refused():
    with pytest.raises(ValueError):
        Session().load_project({"format": "lythos-bearing"})


def test_the_shell_has_every_string_in_both_languages():
    assert set(shell_strings("en")) == set(shell_strings("tr"))


# --------------------------------------------------------------------------- #
#  The HTTP layer
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def base_url():
    server_module.SESSION = Session()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url):
    with urllib.request.urlopen(url) as response:
        return response.status, response.headers, response.read()


def post(url, payload):
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request) as response:
        return response.status, response.headers, response.read()


def test_the_page_and_its_files_are_served(base_url):
    for path, kind in (("/", "text/html"), ("/static/app.js", "javascript"),
                       ("/static/style.css", "text/css"), ("/favicon.ico", "svg")):
        status, headers, body = get(base_url + path)
        assert status == 200 and kind in headers["Content-Type"] and body


def test_the_static_route_cannot_leave_its_folder(base_url):
    with pytest.raises(urllib.error.HTTPError) as caught:
        get(base_url + "/static/../session.py")
    assert caught.value.code == 404


def test_analyse_plot_and_report_over_http(base_url):
    status, _, body = post(base_url + "/api/analyse", {"values": forms.defaults()})
    assert status == 200 and json.loads(body)["ok"]
    status, headers, body = get(base_url + "/api/plot?target=analysis&kind=group")
    assert headers["Content-Type"] == "image/png" and body[:4] == b"\x89PNG"
    status, _, body = post(base_url + "/api/socket", {"values": forms.defaults()})
    assert status == 200 and json.loads(body)["ok"]
    status, headers, body = get(base_url + "/api/plot?target=socket&kind=socket_settlement")
    assert headers["Content-Type"] == "image/png" and body[:4] == b"\x89PNG"
    status, headers, body = post(base_url + "/api/report", {"format": "pdf"})
    assert body[:5] == b"%PDF-"
    assert "lythospile_report.pdf" in headers["Content-Disposition"]


def test_a_saved_project_opens_again(base_url):
    values = forms.defaults()
    values["D"] = 0.95
    _, headers, body = post(base_url + "/api/project", {"values": values})
    assert "project.pile" in headers["Content-Disposition"]
    _, _, loaded = post(base_url + "/api/load", {"project": json.loads(body)})
    assert json.loads(loaded)["values"]["D"] == 0.95


def test_an_error_comes_back_as_json(base_url):
    values = forms.defaults()
    values["D"] = 0.0
    with pytest.raises(urllib.error.HTTPError) as caught:
        post(base_url + "/api/analyse", {"values": values})
    assert "error" in json.loads(caught.value.read())


def test_the_language_can_be_switched(base_url):
    _, _, body = post(base_url + "/api/language", {"lang": "tr"})
    assert json.loads(body)["strings"]["tab_inputs"].startswith("1 · Kazık")
    post(base_url + "/api/language", {"lang": "en"})
