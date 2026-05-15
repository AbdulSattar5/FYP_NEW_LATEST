from django.core.management.base import BaseCommand

from store.product_importer import ProductImporter


class Command(BaseCommand):
    help = "Import products from the real CSV files bundled with the project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["auto", "cleaned", "products", "uk"],
            default="auto",
            help="CSV source to import (default: auto)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing products before importing",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional row limit for testing",
        )

    def handle(self, *args, **options):
        importer = ProductImporter()
        summary = importer.import_products(
            source=options["source"],
            clear=options["clear"],
            limit=options["limit"],
        )

        self.stdout.write(self.style.SUCCESS("Product import completed"))
        self.stdout.write(f"Source file: {summary.source_file}")
        self.stdout.write(f"Total rows read: {summary.total_rows}")
        self.stdout.write(f"Products created: {summary.created_products}")
        self.stdout.write(f"Products updated: {summary.updated_products}")
        self.stdout.write(f"Categories created: {summary.created_categories}")
        self.stdout.write(f"Skipped rows: {summary.skipped_rows}")
        self.stdout.write(f"Errors: {summary.errors}")
