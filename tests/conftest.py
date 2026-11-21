import pytest

from lab_settings import CheckSettings


@pytest.fixture(scope="session")
def beacon_config():
    return CheckSettings.from_env()
