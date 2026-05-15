# ═══════════════════════════════════════════════════════════
# AI RECOMMENDATION ENGINE - COMPLETE ML CORE
# ═══════════════════════════════════════════════════════════
# DATA FLOW:
# USER ACTION → log_interaction() → UserInteraction table
#     ↓
# RecommendationEngine.get_hybrid_recommendations()
#     → Collaborative Filtering (cosine similarity between users)
#     → Content-Based Filtering (TF-IDF on product descriptions)
#     → Hybrid merge (60% collab + 40% content)
#     ↓
# Recommendation objects saved to database
#     ↓
# get_quick_recommendations() fetches from DB → Product queryset
#     ↓
# Template displays: {{ product.image.url }} → /media/products/image.jpg
#     (served by Django via MEDIA_URL config in main urls.py)
# ═══════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# Interaction weights - how much each action matters for ML
INTERACTION_WEIGHTS = {
    'view': 1,
    'search': 1,
    'like': 2,
    'cart': 3,
    'purchase': 5,
}


class RecommendationEngine:
    """
    Hybrid ML Recommendation Engine combining:
    - Collaborative Filtering (user-user similarity)
    - Content-Based Filtering (TF-IDF on product features)
    """
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.UserInteraction, self.Product, self.Recommendation, self.Category = self._get_models()
    
    def _get_models(self):
        """
        Lazy import to avoid circular dependencies
        Returns: UserInteraction, Product, Recommendation, Category models
        """
        from store.models import UserInteraction, Product, Recommendation, Category
        return UserInteraction, Product, Recommendation, Category
    
    def build_interaction_matrix(self):
        """
        Build user-item interaction matrix from UserInteraction records
        Returns: DataFrame with users as rows, products as columns, weighted scores as values
        """
        try:
            # Get all interactions
            interactions = self.UserInteraction.objects.all().values(
                'user_id', 'product_id', 'interaction_type', 'interaction_count'
            )
            
            if not interactions:
                logger.warning("No interactions found in database")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(interactions)
            
            # Apply interaction weights
            df['weighted_score'] = df.apply(
                lambda row: INTERACTION_WEIGHTS.get(row['interaction_type'], 1) * row['interaction_count'],
                axis=1
            )
            
            # Pivot to create user-item matrix
            matrix = df.pivot_table(
                index='user_id',
                columns='product_id',
                values='weighted_score',
                aggfunc='sum',
                fill_value=0
            )
            
            logger.info(f"Built interaction matrix: {matrix.shape[0]} users × {matrix.shape[1]} products")
            return matrix
            
        except Exception as e:
            logger.error(f"Error building interaction matrix: {e}")
            return pd.DataFrame()
    
    def get_collaborative_filtering_recommendations(self, user_id, n=10):
        """
        Collaborative Filtering: recommend products based on similar users
        Args:
            user_id: Target user ID
            n: Number of recommendations
        Returns: List of product_ids
        """
        try:
            matrix = self.build_interaction_matrix()
            
            if matrix.empty or user_id not in matrix.index:
                logger.info(f"User {user_id} not in matrix, using popular products")
                return self.get_popular_products(n)
            
            # Calculate user-user similarity
            user_similarity = cosine_similarity(matrix)
            user_similarity_df = pd.DataFrame(
                user_similarity,
                index=matrix.index,
                columns=matrix.index
            )
            
            # Get similar users (excluding self)
            similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:6]
            
            if similar_users.empty:
                return self.get_popular_products(n)
            
            # Get products interacted by similar users
            recommendations = {}
            user_products = set(matrix.columns[matrix.loc[user_id] > 0])
            
            for similar_user_id, similarity_score in similar_users.items():
                similar_user_products = matrix.columns[matrix.loc[similar_user_id] > 0]
                
                for product_id in similar_user_products:
                    if product_id not in user_products:
                        interaction_score = matrix.loc[similar_user_id, product_id]
                        score = similarity_score * interaction_score
                        recommendations[product_id] = recommendations.get(product_id, 0) + score
            
            # Sort and return top n
            sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
            return [product_id for product_id, score in sorted_recs[:n]]
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering for user {user_id}: {e}")
            return self.get_popular_products(n)
    
    def get_content_based_recommendations(self, user_id, n=10):
        """
        Content-Based Filtering: recommend products based on user's interaction history
        Uses TF-IDF on product features (name, category, description)
        Args:
            user_id: Target user ID
            n: Number of recommendations
        Returns: List of product_ids
        """
        try:
            # Get user's interaction history
            user_interactions = self.UserInteraction.objects.filter(
                user_id=user_id
            ).select_related('product', 'product__category')
            
            if not user_interactions.exists():
                logger.info(f"No interactions for user {user_id}, using popular products")
                return self.get_popular_products(n)
            
            # Build user preference profile
            user_profile_text = []
            interacted_product_ids = set()
            
            for interaction in user_interactions:
                product = interaction.product
                interacted_product_ids.add(product.product_id)
                
                # Weight by interaction type
                weight = INTERACTION_WEIGHTS.get(interaction.interaction_type, 1)
                text = f"{product.name} {product.category.name} {product.description}"
                
                # Repeat text based on weight
                user_profile_text.extend([text] * weight)
            
            user_profile = " ".join(user_profile_text)
            
            # Get all available products
            all_products = self.Product.objects.filter(
                is_available=True,
                stock_level__gt=0
            ).select_related('category')
            
            if not all_products.exists():
                return []
            
            # Build product feature texts
            product_texts = []
            product_ids = []
            
            for product in all_products:
                text = f"{product.name} {product.category.name} {product.description}"
                product_texts.append(text)
                product_ids.append(product.product_id)
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            product_vectors = vectorizer.fit_transform(product_texts)
            user_vector = vectorizer.transform([user_profile])
            
            # Calculate similarity
            similarities = cosine_similarity(user_vector, product_vectors)[0]
            
            # Create recommendations excluding already interacted products
            recommendations = []
            for idx, similarity_score in enumerate(similarities):
                product_id = product_ids[idx]
                if product_id not in interacted_product_ids and similarity_score > 0:
                    recommendations.append((product_id, similarity_score))
            
            # Sort and return top n
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return [product_id for product_id, score in recommendations[:n]]
            
        except Exception as e:
            logger.error(f"Error in content-based filtering for user {user_id}: {e}")
            return self.get_popular_products(n)
    
    def get_popular_products(self, n=10):
        """
        Cold-start fallback: return popular products
        Args:
            n: Number of products
        Returns: List of product_ids
        """
        try:
            popular = self.Product.objects.filter(
                is_available=True,
                stock_level__gt=0
            ).order_by('-rating', '-stock_level')[:n]
            
            return list(popular.values_list('product_id', flat=True))
            
        except Exception as e:
            logger.error(f"Error getting popular products: {e}")
            return []
    
    def get_hybrid_recommendations(self, user_id, n=10):
        """
        Hybrid approach: combine collaborative and content-based filtering
        Weight: 60% collaborative + 40% content-based
        Args:
            user_id: Target user ID
            n: Number of recommendations
        Returns: List of tuples [(product_id, score, reason), ...]
        """
        try:
            # Check if user has any interactions
            has_interactions = self.UserInteraction.objects.filter(user_id=user_id).exists()
            
            if not has_interactions:
                logger.info(f"User {user_id} has no interactions, using popular products")
                popular_ids = self.get_popular_products(n)
                return [(pid, 0.1, "Trending product") for pid in popular_ids]
            
            # Get recommendations from both methods
            collab_recs = set(self.get_collaborative_filtering_recommendations(user_id, n=15))
            content_recs = set(self.get_content_based_recommendations(user_id, n=15))
            
            # Merge with weighted scoring
            recommendations = {}
            
            # Products in BOTH lists get highest priority
            both = collab_recs & content_recs
            for product_id in both:
                recommendations[product_id] = (1.0, "Highly recommended for you")
            
            # Collaborative only
            collab_only = collab_recs - content_recs
            for product_id in collab_only:
                recommendations[product_id] = (0.6, "Based on similar shoppers")
            
            # Content-based only
            content_only = content_recs - collab_recs
            for product_id in content_only:
                recommendations[product_id] = (0.4, "Based on your browsing history")
            
            # If not enough, add popular products
            if len(recommendations) < n:
                popular_ids = self.get_popular_products(n)
                for product_id in popular_ids:
                    if product_id not in recommendations:
                        recommendations[product_id] = (0.1, "Trending product")
                        if len(recommendations) >= n:
                            break
            
            # Sort by score and return top n
            sorted_recs = sorted(
                [(pid, score, reason) for pid, (score, reason) in recommendations.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_recs[:n]
            
        except Exception as e:
            logger.error(f"Error in hybrid recommendations for user {user_id}: {e}")
            popular_ids = self.get_popular_products(n)
            return [(pid, 0.1, "Trending product") for pid in popular_ids]
    
    def generate_recommendations_for_user(self, user_id):
        """
        Generate and save recommendations for a specific user
        Args:
            user_id: Target user ID
        Returns: List of created Recommendation objects
        """
        try:
            # Get hybrid recommendations
            hybrid_recs = self.get_hybrid_recommendations(user_id, n=12)
            
            # Delete old recommendations
            self.Recommendation.objects.filter(user_id=user_id).delete()
            
            # Create new recommendations
            new_recs = []
            for product_id, score, reason in hybrid_recs:
                try:
                    product = self.Product.objects.get(product_id=product_id)
                    rec = self.Recommendation(
                        user_id=user_id,
                        product=product,
                        score=score,
                        reason=reason
                    )
                    new_recs.append(rec)
                except self.Product.DoesNotExist:
                    continue
            
            # Bulk create
            if new_recs:
                self.Recommendation.objects.bulk_create(new_recs)
                logger.info(f"Generated {len(new_recs)} recommendations for user {user_id}")
            else:
                logger.warning(f"No recommendations generated for user {user_id}")
            
            return new_recs
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return []
    
    def generate_all_recommendations(self):
        """
        Batch process: generate recommendations for all active users
        Returns: Total count of users processed
        """
        try:
            # Get all users who have interactions
            user_ids = self.UserInteraction.objects.values_list(
                'user_id', flat=True
            ).distinct()
            
            total = 0
            for user_id in user_ids:
                self.generate_recommendations_for_user(user_id)
                total += 1
                
                if total % 10 == 0:
                    logger.info(f"Processed {total} users...")
            
            logger.info(f"✅ Generated recommendations for {total} users")
            return total
            
        except Exception as e:
            logger.error(f"Error in batch recommendation generation: {e}")
            return 0


# ═══════════════════════════════════════════════════════════
# STANDALONE HELPER FUNCTION FOR VIEWS
# ═══════════════════════════════════════════════════════════

def get_quick_recommendations(user_id, n=6):
    """
    Fast function to get recommendations for a user
    Used in views to quickly fetch personalized products
    
    Args:
        user_id: Target user ID
        n: Number of recommendations
    
    Returns: Product queryset (ready for templates)
    """
    from store.models import Recommendation, Product
    
    try:
        # Check if recommendations exist
        recs = Recommendation.objects.filter(
            user_id=user_id
        ).select_related('product', 'product__category').order_by('-score')[:n]
        
        if recs.exists():
            # Return products from saved recommendations
            product_ids = [rec.product_id for rec in recs]
            products = Product.objects.filter(
                product_id__in=product_ids,
                is_available=True
            ).select_related('category')
            
            # Preserve order
            product_dict = {p.product_id: p for p in products}
            ordered_products = [product_dict[pid] for pid in product_ids if pid in product_dict]
            
            return ordered_products
        else:
            # Generate fresh recommendations
            logger.info(f"No saved recommendations for user {user_id}, generating...")
            engine = RecommendationEngine()
            engine.generate_recommendations_for_user(user_id)
            
            # Retry fetch
            recs = Recommendation.objects.filter(
                user_id=user_id
            ).select_related('product', 'product__category').order_by('-score')[:n]
            
            if recs.exists():
                product_ids = [rec.product_id for rec in recs]
                products = Product.objects.filter(
                    product_id__in=product_ids,
                    is_available=True
                ).select_related('category')
                
                product_dict = {p.product_id: p for p in products}
                ordered_products = [product_dict[pid] for pid in product_ids if pid in product_dict]
                
                return ordered_products
            else:
                # Final fallback: popular products
                return Product.objects.filter(
                    is_available=True,
                    stock_level__gt=0
                ).order_by('-rating')[:n].select_related('category')
    
    except Exception as e:
        logger.error(f"Error in get_quick_recommendations for user {user_id}: {e}")
        # Fallback to popular products
        return Product.objects.filter(
            is_available=True,
            stock_level__gt=0
        ).order_by('-rating')[:n].select_related('category')
