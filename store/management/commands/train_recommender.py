from django.core.management.base import BaseCommand, CommandError

from store.recommendation_engine import train_recommender_artifacts


class Command(BaseCommand):
    help = "Train leakage-safe recommender artifacts with temporal split evaluation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--top-k",
            type=int,
            default=12,
            help="Top-K cutoff used for Precision/Recall/NDCG metrics (default: 12).",
        )
        parser.add_argument(
            "--train-ratio",
            type=float,
            default=0.7,
            help="Temporal train split ratio (default: 0.7).",
        )
        parser.add_argument(
            "--validation-ratio",
            type=float,
            default=0.15,
            help="Temporal validation split ratio (default: 0.15).",
        )

    def handle(self, *args, **options):
        top_k = options["top_k"]
        train_ratio = options["train_ratio"]
        validation_ratio = options["validation_ratio"]

        self.stdout.write(self.style.WARNING("Training recommender pipeline..."))
        self.stdout.write(
            f"Using temporal split train={train_ratio:.2f}, validation={validation_ratio:.2f}, "
            f"test={1.0 - train_ratio - validation_ratio:.2f}"
        )

        try:
            metrics = train_recommender_artifacts(
                top_k=top_k,
                train_ratio=train_ratio,
                val_ratio=validation_ratio,
            )
        except (RuntimeError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        precision_key = f"precision@{top_k}"
        recall_key = f"recall@{top_k}"
        ndcg_key = f"ndcg@{top_k}"

        model_test = metrics["model"]["test"]
        baseline_test = metrics["baseline"]["test"]
        comparison = metrics["comparison"]

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Training completed."))
        self.stdout.write(f"Trained at: {metrics['trained_at']}")
        self.stdout.write(
            f"Data counts -> products: {metrics['data']['products_count']}, "
            f"interactions: {metrics['data']['interactions_count']}, "
            f"train/val/test: {metrics['data']['train_count']}/"
            f"{metrics['data']['validation_count']}/{metrics['data']['test_count']}"
        )
        self.stdout.write("")
        self.stdout.write("Test metrics (model vs popularity baseline):")
        self.stdout.write(
            f"  {precision_key}: {model_test.get(precision_key, 0):.4f} vs {baseline_test.get(precision_key, 0):.4f}"
        )
        self.stdout.write(
            f"  {recall_key}: {model_test.get(recall_key, 0):.4f} vs {baseline_test.get(recall_key, 0):.4f}"
        )
        self.stdout.write(
            f"  {ndcg_key}: {model_test.get(ndcg_key, 0):.4f} vs {baseline_test.get(ndcg_key, 0):.4f}"
        )
        self.stdout.write(
            "  coverage: "
            f"{model_test.get('coverage', 0):.4f} vs {baseline_test.get('coverage', 0):.4f}"
        )
        self.stdout.write(
            "  cold_start_coverage: "
            f"{model_test.get('cold_start_coverage', 0):.4f} vs {baseline_test.get('cold_start_coverage', 0):.4f}"
        )
        self.stdout.write("")
        self.stdout.write(
            "Lift summary -> "
            f"precision: {comparison.get('test_precision_lift', 0):+.4f}, "
            f"recall: {comparison.get('test_recall_lift', 0):+.4f}, "
            f"ndcg: {comparison.get('test_ndcg_lift', 0):+.4f}"
        )
