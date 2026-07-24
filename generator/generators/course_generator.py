from generator.core.filesystem import FileSystem
from generator.core.template import TemplateEngine
from generator.generators.base import BaseGenerator


class CourseGenerator(BaseGenerator):
    name = "course"

    def generate(self, context):
        fs = FileSystem()
        engine = TemplateEngine(context.project_root / "templates")
        out = context.resolved_output_dir()
        fs.ensure_directory(out, dry_run=context.dry_run)
        fs.write_text(
            out / "README.md",
            engine.render("course/README.md.j2", context.variables),
            overwrite=context.force,
            dry_run=context.dry_run,
        )
        for d in ["slides", "lecture-notes", "demos", "labs", "homework", "quizzes", "solutions"]:
            fs.ensure_directory(out / d, dry_run=context.dry_run)
