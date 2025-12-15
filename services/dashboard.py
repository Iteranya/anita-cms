# file: services/dashboard.py

from sqlalchemy.orm import Session
from typing import Dict, Any

from data import crud

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Orchestrates the retrieval of various statistics for the admin dashboard.
        This service calls multiple granular CRUD functions and assembles the results
        into a single, structured dictionary ready for the API layer.
        """
        
        # --- 1. Fetch Core Entity Counts ---
        # These are simple scalar values, no transformation needed.
        core_counts = {
            "pages": crud.get_total_pages_count(self.db),
            "forms": crud.get_total_forms_count(self.db),
            "submissions": crud.get_total_submissions_count(self.db),
            "users": crud.get_total_users_count(self.db),
            "tags": crud.get_total_tags_count(self.db),
        }

        # --- 2. Fetch Specific Page-Related Stats ---
        page_stats = {
            "public_count": crud.get_pages_count_by_tag(self.db, 'sys:public'),
            "blog_posts_count": crud.get_pages_count_by_tag(self.db, 'sys:blog'),
        }
        
        # --- 3. Fetch and Transform Activity Metrics ---
        # The CRUD layer returns a list of tuples. The service layer's job is to
        # transform this into a more API-friendly list of dictionaries.
        top_forms_raw = crud.get_top_forms_by_submission_count(self.db, limit=5)
        top_forms_formatted = [
            {"name": name, "slug": slug, "count": count} 
            for name, slug, count in top_forms_raw  # <-- Unpack all three items
        ]

        top_tags_raw = crud.get_top_tags_by_page_usage(self.db, limit=10)
        top_tags_formatted = [
            {"name": name, "count": count} for name, count in top_tags_raw
        ]

        activity = {
            "top_forms_by_submission": top_forms_formatted,
            "top_tags_on_pages": top_tags_formatted,
        }

        # --- 4. Fetch Lists of Recent Items ---
        # The CRUD functions return full SQLAlchemy model objects. These can be
        # passed directly to the API layer, which will serialize them using
        # your Pydantic schemas.
        recent_items = {
            "newest_pages": crud.get_recent_pages(self.db, limit=5),
            "latest_updates": crud.get_recently_updated_pages(self.db, limit=5),
            "latest_submissions": crud.get_recent_submissions(self.db, limit=5)
        }

        # --- 5. Assemble the Final Response ---
        # Combine all the fetched and transformed data into the final payload.
        return {
            "core_counts": core_counts,
            "page_stats": page_stats,
            "activity": activity,
            "recent_items": recent_items
        }