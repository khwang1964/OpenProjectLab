from generator.core.context import GeneratorContext
from generator.generators.course_generator import CourseGenerator


def test_course_generator(tmp_path):
    root = tmp_path / "root"
    (root / "templates/course").mkdir(parents=True)
    (root / "templates/course/README.md.j2").write_text("# {{ title }}", encoding="utf-8")
    out = tmp_path / "course"
    CourseGenerator().run(
        GeneratorContext(out, {"title": "C++", "course_id": "cpp"}, project_root=root)
    )
    assert (out / "README.md").read_text(encoding="utf-8") == "# C++"
    assert (out / "labs").is_dir()
