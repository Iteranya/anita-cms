import json
from sqlalchemy.orm import Session
from data import models, schemas
from .users import save_role
from .settings import save_setting
from .pages import get_page, create_page

def seed_default_roles(db: Session, json_path: str = "default_roles.json"):
    if db.query(models.Role).count() == 0:
        print("No roles found. Seeding default roles.")
        try:
            with open(json_path, "r") as f:
                defaults = json.load(f)
            for role_name, permissions in defaults.items():
                save_role(db, role_name=role_name, permissions=permissions)
            print("✓ Default roles seeded.")
        except Exception as e:
            print(f"❌ Role seeding error: {e}")

def seed_default_pages(db: Session):
    if db.query(models.Page).count() > 0:
        return
    print("No pages found. Seeding default pages...")
    try:
        with open("default_pages.json", "r") as f:
            default_pages_data = json.load(f)
        for page_dict in default_pages_data:
            if not get_page(db, slug=page_dict['slug']):
                page_schema = schemas.PageSeed(**page_dict)
                create_page(db, page=page_schema)
                print(f"  - Created page: '{page_dict['title']}'")
        print("✓ Default pages seeded.")
    except Exception as e:
        print(f"Error seeding pages: {e}")

def seed_initial_settings(db: Session, json_path: str = "default_config.json"):
    if db.query(models.Setting).filter_by(key="system_note").first():
        return
    print("No settings found. Seeding defaults.")
    try:
        with open(json_path, "r") as f:
            default_settings = json.load(f)
        for key, value in default_settings.items():
            save_setting(db, key=key, value=value)
        print("✓ Default settings seeded.")
    except Exception as e:
        print(f"❌ Settings seeding error: {e}")