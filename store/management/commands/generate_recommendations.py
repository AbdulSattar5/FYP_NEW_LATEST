from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.recommendation_engine import RecommendationEngine


class Command(BaseCommand):
    help = "Generate recommendations from trained artifacts for active users/sessions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="Generate recommendations for specific user ID only.",
        )
        parser.add_argument(
            "--session-key",
            type=str,
            help="Generate recommendations for specific anonymous session key only.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=12,
            help="Maximum recommendations per actor (default: 12).",
        )
        parser.add_argument(
            "--active-days",
            type=int,
            default=90,
            help="Only actors active in the last N days are processed (default: 90).",
        )

    def handle(self, *args, **options):
        start_time = datetime.now()
        user_id = options.get("user_id")
        session_key = options.get("session_key")
        limit = options.get("limit") or 12
        active_days = options.get("active_days") or 90

        if user_id and session_key:
            self.stdout.write(self.style.ERROR("Use either --user-id or --session-key, not both."))
            return

        self.stdout.write(self.style.WARNING("Starting recommendation generation..."))
        self.stdout.write("")

        engine = RecommendationEngine()

        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user is None:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found."))
                return

            recs = engine.generate_recommendations_for_user(user_id=user_id, n=limit)
            self.stdout.write(self.style.SUCCESS(
                f"Generated {len(recs)} recommendations for {user.username}."
            ))
        elif session_key:
            recs = engine.generate_recommendations_for_session(session_key=session_key, n=limit)
            self.stdout.write(self.style.SUCCESS(
                f"Generated {len(recs)} recommendations for session {session_key}."
            ))
        else:
            self.stdout.write(
                f"Generating recommendations for active users/sessions in last {active_days} days..."
            )
            self.stdout.write("")
            total_actors = engine.generate_all_recommendations(n=limit, active_days=active_days)
            self.stdout.write(self.style.SUCCESS(
                f"Successfully processed {total_actors} actors."
            ))

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Completed in {duration:.2f} seconds"))
