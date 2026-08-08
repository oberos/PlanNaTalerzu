from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Dump recipes app fixture data for ingredients, nutrition info, recipes, and recipe-ingredient links."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            default="recipes/fixtures/recipe_data.json",
            help=(
                "Relative path from project root to write the JSON fixture file. "
                "Defaults to recipes/fixtures/recipe_data.json."
            ),
        )
        parser.add_argument(
            "--app",
            default="recipes",
            help="Django app label to dump. Defaults to recipes.",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="Number of spaces to indent the JSON output.",
        )

    def handle(self, *args, **options):
        output_path = Path(settings.BASE_DIR) / options["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as output_file:
            call_command(
                "dumpdata",
                options["app"],
                format="json",
                indent=options["indent"],
                stdout=output_file,
            )

        self.stdout.write(self.style.SUCCESS(f"Recipe fixtures dumped to {output_path.relative_to(settings.BASE_DIR)}"))
