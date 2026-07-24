from generator.core.filesystem import FileSystem
from generator.core.template import TemplateEngine
from generator.generators.base import BaseGenerator


class BootstrapGenerator(BaseGenerator):
    name = "bootstrap"

    def generate(self, context):
        engine = TemplateEngine(context.project_root / "templates")
        fs = FileSystem()
        out = context.resolved_output_dir()
        fs.ensure_directory(out, dry_run=context.dry_run)
        for template, target in [
            ("project/README.md.j2", "README.md"),
            ("project/gitignore.j2", ".gitignore"),
        ]:
            fs.write_text(
                out / target,
                engine.render(template, context.variables),
                overwrite=context.force,
                dry_run=context.dry_run,
            )
