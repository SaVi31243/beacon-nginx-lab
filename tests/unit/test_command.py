from subprocess import CompletedProcess, TimeoutExpired

import pytest

import check_beacon


@pytest.fixture
def command_environment(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://beacon.invalid:8001/")
    monkeypatch.setenv("EXPECTED_RELEASE", "unit-beacon")
    monkeypatch.setenv("CHECK_TIMEOUT", "1.75")


def test_uses_environment_and_reports_success(command_environment, monkeypatch, capsys):
    def fake_run(args, **options):
        assert args[:2] == ["curl", "-q"]
        assert args[-1] == "http://beacon.invalid:8001/"
        assert options == {"capture_output": True, "text": True, "timeout": 1.75}
        return CompletedProcess(args, 0, "unit-beacon", "")

    monkeypatch.setattr(check_beacon.subprocess, "run", fake_run)
    assert check_beacon.main() == 0
    assert "RESULT OK release=unit-beacon" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("exit_code", "content", "reason"),
    [(22, "", "curl=22"), (0, "foreign-release", "missing release")],
)
def test_failure_messages(command_environment, monkeypatch, capsys, exit_code, content, reason):
    def fake_run(args, **options):
        return CompletedProcess(args, exit_code, content, "request failed")

    monkeypatch.setattr(check_beacon.subprocess, "run", fake_run)
    assert check_beacon.main() == 1
    assert reason in capsys.readouterr().out


def test_timeout_exit(command_environment, monkeypatch, capsys):
    def fake_run(args, *, timeout, **options):
        raise TimeoutExpired(args, timeout)

    monkeypatch.setattr(check_beacon.subprocess, "run", fake_run)
    assert check_beacon.main() == 2
    assert "RESULT TIMEOUT" in capsys.readouterr().out


def test_missing_release_configuration(command_environment, monkeypatch, capsys):
    def unexpected_call(*args, **options):
        pytest.fail("curl should not run with incomplete configuration")

    monkeypatch.delenv("EXPECTED_RELEASE")
    monkeypatch.setattr(check_beacon.subprocess, "run", unexpected_call)
    assert check_beacon.main() == 1
    assert "EXPECTED_RELEASE" in capsys.readouterr().out
