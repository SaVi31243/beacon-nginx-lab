def test_configuration_accepts_syntax(host):
    probe = host.run("nginx -t")
    assert probe.rc == 0, probe.stderr


def test_demo_page(host):
    index = host.file("/usr/share/nginx/html/index.html")
    assert index.is_file
    assert index.contains("devops6-demo")
