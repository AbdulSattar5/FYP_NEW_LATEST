from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.recommendation_engine import RecommendationEngine
from datetime import datetime


class Command(BaseCommand):
    help = 'Generate AI recommendations for users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Generate recommendations for specific user ID only',
        )
    
    def handle(self, *args, **options):
        start_time = datetime.now()
        self.stdout.write(self.style.WARNING('🤖 Starting AI Recommendation Generation...'))
        self.stdout.write('')
        
        engine = RecommendationEngine()
        user_id = options.get('user_id')
        
        if user_id:
            # Generate for specific user
            self.stdout.write(f'Generating recommendations for user ID: {user_id}')
            try:
                user = User.objects.get(id=user_id)
                recs = engine.generate_recommendations_for_user(user_id)
                
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Generated {len(recs)} recommendations for {user.username}'
                ))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ User with ID {user_id} not found'))
                return
        else:
            # Generate for all users
            self.stdout.write('Generating recommendations for ALL users with interactions...')
            self.stdout.write('')
            
            total_users = engine.generate_all_recommendations()
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                f'✅ Successfully processed {total_users} users'
            ))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'⏱️  Completed in {duration:.2f} seconds'))
        self.stdout.write('')
        self.stdout.write('📊 Recommendations are now available in:')
        self.stdout.write('   - Home page "Recommended For You" section')
        self.stdout.write('   - Product detail pages')
        self.stdout.write('   - /recommendations/ page')
