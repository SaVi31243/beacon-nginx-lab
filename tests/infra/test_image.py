import pytest


DOCUMENT_ROOT = "/opt/beacon/public"


def test_nginx_config_syntax(host):
    response = host.run("nginx -t")
    assert response.rc == 0, response.stderr


@pytest.mark.parametrize(
    "filepath",
    ["/etc/nginx/conf.d/default.conf", f"{DOCUMENT_ROOT}/index.html", f"{DOCUMENT_ROOT}/health.json"],
)
def test_image_has_required_file(host, filepath):
    assert host.file(filepath).is_file


def test_index_is_readable_by_worker(host):
    mode = host.file(f"{DOCUMENT_ROOT}/index.html").mode
    assert mode == 0o644, f"index.html has mode {mode:04o}, expected 0644"


def test_local_page_marks_release(host, beacon_config):
    index = host.file(f"{DOCUMENT_ROOT}/index.html")
    assert beacon_config.release in index.content_string
