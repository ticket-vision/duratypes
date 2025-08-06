import pytest


def pytest_addoption(parser):
    """
    Add a new ini option for pytest configuration.

    This function allows registration of a custom test path as an ini option in pytest.
    The option can be used to specify or modify the test resources location and configurations.

    :param parser: The pytest configuration parser object used to register ini options.
                   It allows defining and modifying pytest configurations.
    :type parser: ConfigParser.ConfigParser
    """
    parser.addini("test_resources", help="Custom test path", default="")


@pytest.fixture
def ini_value(request):
    """
    Fixture to retrieve a specific configuration value from pytest's INI settings.

    This fixture accesses the pytest config and fetches the INI setting named
    "test_resources". It simplifies retrieving custom configuration values during
    test execution.

    :param request: The pytest fixture `request`, which provides access to the
        pytest environment, including configuration options and command-line
        arguments.
    :return: The value associated with the "test_resources" INI setting, as
        defined in pytest's configuration.
    :rtype: Any
    """
    return request.config.getini("test_resources")
