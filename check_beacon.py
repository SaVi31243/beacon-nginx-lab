import subprocess

from lab_settings import CheckSettings


def main():
    try:
        settings = CheckSettings.from_env()
    except ValueError as error:
        print(f"RESULT ERROR configuration {error}")
        return 1

    url = settings.origin.geturl() + "/"
    args = ["curl", "-q", "--silent", "--show-error", "--fail", "--", url]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=settings.timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"RESULT TIMEOUT {url} ({settings.timeout:g}s)")
        return 2
    except OSError as error:
        print(f"RESULT ERROR curl unavailable: {error}")
        return 1

    if result.returncode:
        print(f"RESULT ERROR curl={result.returncode} {result.stderr.strip()}")
        return 1
    if settings.release not in result.stdout:
        print(f"RESULT ERROR missing release {settings.release}")
        return 1

    print(f"RESULT OK release={settings.release} url={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
