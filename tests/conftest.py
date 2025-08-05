import pytest


def pytest_addoption(parser):
    parser.addini("test_resources", help="Custom test path", default="")


@pytest.fixture
def ini_value(request):
    return request.config.getini("test_resources")
