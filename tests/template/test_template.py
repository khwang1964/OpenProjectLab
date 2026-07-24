from generator.core.template import TemplateEngine


def test_jinja_render(tmp_path):
    (tmp_path / "x.j2").write_text("Hello {{ name }}", encoding="utf-8")
    assert TemplateEngine(tmp_path).render("x.j2", {"name": "OPL"}) == "Hello OPL"
