# Import everything from the sub-modules to expose them at package level
from .labels import (
    format_label_for_db,
    get_or_create_labels,
    parse_search_query,
    apply_label_filters,
    get_main_labels
)

from .pages import (
    get_page,
    list_pages,
    search_pages,
    get_pages_by_label,
    get_pages_by_labels,
    get_first_page_by_label,
    get_first_page_by_labels,
    get_pages_by_author,
    create_page,
    update_page,
    delete_page
)

from .collections import (
    get_collection,
    list_collections,
    create_collection,
    update_collection,
    delete_collection
)

from .submissions import (
    get_submission,
    list_submissions,
    search_submissions,
    create_submission,
    update_submission,
    delete_submission
)

from .users import (
    get_user_by_username,
    list_users,
    count_users,
    save_user,
    delete_user,
    get_role,
    get_all_roles,
    save_role,
    delete_role
)

from .settings import (
    get_setting,
    get_all_settings,
    save_setting
)

from .stats import (
    get_total_pages_count,
    get_total_collections_count,
    get_total_submissions_count,
    get_total_users_count,
    get_total_labels_count,
    get_pages_count_by_label,
    get_top_collections_by_submission_count,
    get_top_labels_by_page_usage,
    get_recent_pages,
    get_recently_updated_pages,
    get_recent_submissions
)

from .seed import (
    seed_default_roles,
    seed_default_pages,
    seed_initial_settings
)