# Import everything from the sub-modules to expose them at package level
from .tags import (
    format_tag_for_db,
    get_or_create_tags,
    parse_search_query,
    apply_tag_filters,
    get_main_tags
)

from .pages import (
    get_page,
    list_pages,
    search_pages,
    get_pages_by_tag,
    get_pages_by_tags,
    get_first_page_by_tag,
    get_first_page_by_tags,
    get_pages_by_author,
    create_page,
    update_page,
    delete_page
)

from .forms import (
    get_form,
    list_forms,
    create_form,
    update_form,
    delete_form
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
    get_total_forms_count,
    get_total_submissions_count,
    get_total_users_count,
    get_total_tags_count,
    get_pages_count_by_tag,
    get_top_forms_by_submission_count,
    get_top_tags_by_page_usage,
    get_recent_pages,
    get_recently_updated_pages,
    get_recent_submissions
)

from .seed import (
    seed_default_roles,
    seed_default_pages,
    seed_initial_settings
)