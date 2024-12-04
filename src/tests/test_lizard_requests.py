from ..lizard_requests import LizardRequests
from ..lizard_errors import InvalidUrlError
import requests
import pytest


def test_correct_init():
    s = requests.Session()
    s.headers = {
        "username": "__key__",
        "password": "sQ3zxCaw.2l1WidgNMrx0nXrXrA5ylciAqwsWIiIr",
        "Content-Type": "application/json",
    }
    lr = LizardRequests(session=s, base_url="https://demo.lizard.net/api/v4")
    assert lr
    assert lr.api_base_url == "https://demo.lizard.net/api/v4"
    assert lr.session == s


def test_annonymous_session_init():
    s = requests.Session()
    s.headers = {
        "username": "__key__",
        "password": "",
        "Content-Type": "application/json",
    }
    lr = LizardRequests(session=s, base_url="https://demo.lizard.net/api/v4")
    assert lr
    assert lr.api_base_url == "https://demo.lizard.net/api/v4"
    assert lr.session == s


def test_bad_url_init():
    s = requests.Session()
    s.headers = {
        "username": "__key__",
        "password": "",
        "Content-Type": "application/json",
    }
    with pytest.raises(InvalidUrlError):
        _lr = LizardRequests(session=s, base_url="https://www.google.com")

    with pytest.raises(InvalidUrlError):
        _lr = LizardRequests(session=s, base_url="https://demo.lizard.net/api/v2")
