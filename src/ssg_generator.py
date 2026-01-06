import json
import shutil
from pathlib import Path
from typing import Any, List, Dict
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from jinja2 import Environment, BaseLoader

from data.database import SessionLocal
from services.pages import PageService
from data import models

class SSGGenerator:
    def __init__(self, output_dir: str = "dist"):
        self.db: Session = SessionLocal()
        self.page_service = PageService(self.db)
        self.output_dir = Path(output_dir)
        self.template_env = Environment(loader=BaseLoader(), autoescape=True)
        
        self.template_env.filters['tojson'] = self._to_json_filter

    def _to_json_filter(self, value: Any) -> str:
        return json.dumps(value, default=str)

    def _render_template(self, template_str: str, context: dict) -> str:
        """Renders the Jinja2 string template."""
        template = self.template_env.from_string(template_str)
        return template.render(**context)

    # ==========================================
    # 🔧 HELPER: MODEL SERIALIZER
    # ==========================================
    def _serialize_model(self, model_instance, exclude: List[str] = None) -> Dict[str, Any]:
        """
        Converts a SQLAlchemy model to a dictionary.
        Correctly handles cases where DB column name != Python attribute name.
        (e.g. Column("schema_json") -> model.schema)
        """
        if not model_instance:
            return {}
        
        if exclude is None:
            exclude = []

        data = {}
        
        # 1. Use Inspector to look up Python Attribute names (not just DB columns)
        inst_state = inspect(model_instance)
        
        # Iterate over mapped column attributes
        for attr in inst_state.mapper.column_attrs:
            key = attr.key  # This is the Python name (e.g. 'schema', 'data')
            
            if key not in exclude:
                # Safely get the value
                val = getattr(model_instance, key)
                data[key] = val

        # 2. Handle Relationships manually (Tags and Labels)
        if hasattr(model_instance, 'tags') and 'tags' not in exclude:
            data['tags'] = [t.name for t in model_instance.tags]
        
        if hasattr(model_instance, 'labels') and 'labels' not in exclude:
            data['labels'] = [l.name for l in model_instance.labels]

        return data

    # ==========================================
    # 🔧 PRE-PROCESSING HOOK
    # ==========================================
    def preprocess_content(self, content: str) -> str:
        if not content:
            return ""
        # Note: Add regex to tweak hikarin main import here
        return content

    # ==========================================
    # ⚙️ GENERATION LOGIC
    # ==========================================
    def generate(self):
        """Main execution function."""
        print(f"🚀 Starting SSG Generation into '{self.output_dir}'...")
        
        # 1. Clean/Create Output Directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1.5 COPY ASSETS (Skipped generic asset logic for brevity, kept structure)
        self._copy_static_assets()

        # 2. Fetch System Template
        print("🔍 Fetching system template...")
        sys_template = self.page_service.get_first_page_by_labels(['sys:template', 'any:read'])
        if not sys_template:
            print("❌ Critical: 'sys:template' not found. Cannot render dynamic pages.")
            return

        # 3. Fetch All Public Pages
        print("📚 Fetching all public pages...")
        all_pages = self.page_service.get_pages_by_label("any:read")
        
        # --- HTML GENERATION ---
        count = 0
        for page in all_pages:
            self._process_single_page(page, sys_template)
            count += 1
        print(f"✅ HTML complete. {count} pages generated.")

        # --- JSON API GENERATION ---
        print("💾 Generating JSON API files...")
        self._generate_page_index_json(all_pages)
        self._generate_collection_json() 
        
        self.db.close()

    def _copy_static_assets(self):
        """Helper to copy static/media folders."""
        for src, dest_name in [("static/hikarin-ssg", "static/hikarin"), ("uploads/media", "media")]:
            source = Path(src)
            dest = self.output_dir / dest_name
            if source.exists():
                print(f"📦 Copying: {source} -> {dest}")
                shutil.copytree(source, dest, dirs_exist_ok=True)

    # ==========================================
    # 📄 PAGE PROCESSING (HTML)
    # ==========================================
    def _process_single_page(self, page: models.Page, sys_template: models.Page):
        labels = {l.name for l in page.labels}
        
        if "any:read" not in labels:
            return

        output_path = None
        if "sys:home" in labels:
            output_path = self.output_dir / "index.html"
        elif "sys:head" in labels:
            output_path = self.output_dir / page.slug / "index.html"
        else:
            main_cat = next((l.split(":")[1] for l in labels if l.startswith("main:")), None)
            if main_cat:
                output_path = self.output_dir / main_cat / page.slug / "index.html"
            else:
                return

        processed_body = self.preprocess_content(page.markdown if page.type != 'html' else page.html)
        final_html = ""

        if page.type == 'html':
            final_html = processed_body
        else:
            context = {
                "title": page.title,
                "markdown_content": processed_body,
                "author": page.author,
                "published": str(page.created),
                "updated": str(page.updated),
                "description": page.content,
                "thumb": page.thumb
            }
            try:
                final_html = self._render_template(sys_template.html, context)
            except Exception as e:
                print(f"   ❌ Error rendering template for {page.slug}: {e}")
                return

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

    # ==========================================
    # 💾 JSON API GENERATION
    # ==========================================
    def _generate_page_index_json(self, pages: List[models.Page]):
        """Generates a single JSON file containing metadata for all pages."""
        print("   📄 Generating Pages Index JSON...")
        
        api_dir = self.output_dir / "static/data"
        api_dir.mkdir(parents=True, exist_ok=True)

        pages_data = []
        for page in pages:
            # Exclude heavy content fields
            p_data = self._serialize_model(page, exclude=['markdown', 'html', 'custom'])
            pages_data.append(p_data)

        output_file = api_dir / "pages.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pages_data, f, default=str) # indent=2 for debug, none for prod

    def _generate_collection_json(self):
        """Generates a single JSON file. Only includes collections with 'any:read'."""
        print("   🗂️  Generating Single Collections JSON...")

        api_data_dir = self.output_dir / "static/data"
        api_data_dir.mkdir(parents=True, exist_ok=True)

        # 1. Container for final JSON
        all_collections_data = []

        # 2. Fetch from DB
        # Optimization TODO: Move filtering to SQL query to avoid fetching unauthorized rows
        collections = self.db.query(models.Collection).all()
        
        # 3. Process 
        for col in collections:
            # --- FILTER LOGIC START ---
            # Get list of label names for this collection
            labels = {l.name for l in col.labels}
            
            # Skip if it doesn't have the public read label
            if "any:read" not in labels:
                continue
            # --- FILTER LOGIC END ---

            # Serialize Collection Metadata
            col_data = self._serialize_model(col, exclude=['submissions'])
            
            # Serialize Submissions (Handle empty submissions safely)
            submissions_data = []
            if hasattr(col, 'submissions'):
                for sub in col.submissions:
                    sub_data = self._serialize_model(sub)
                    submissions_data.append(sub_data)
            
            entry = {
                "meta": col_data,
                "items": submissions_data
            }
            all_collections_data.append(entry)

        # 4. Write Result
        output_file = api_data_dir / "collections.json"
        print(f"      -> {output_file.name} (Exported {len(all_collections_data)} collections)")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_collections_data, f, default=str)