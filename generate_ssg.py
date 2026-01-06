import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Configuration & Setup ---
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# 1. Load environment variables (Critical for Database connection)
load_dotenv(ENV_PATH)

# 2. Ensure project root is in python path so we can import 'data', 'services', etc.
sys.path.append(str(BASE_DIR))

def run_ssg():
    print("---------------------------------------------------------")
    print("   🔨 Anita CMS - Static Site Generator Tool")
    print("---------------------------------------------------------")

    # 3. Import Generator
    # We import inside the function or after sys.path setup to avoid ModuleNotFoundError
    try:
        from src.ssg_generator import SSGGenerator
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("   Make sure you are running this file from the project root directory.")
        return

    # 4. Check for Database (Optional sanity check for SQLite)
    db_path = BASE_DIR / "anita.db"
    if not db_path.exists():
        # Note: If you switch to PostgreSQL/MySQL later, you can remove this check.
        print(f"⚠️  Warning: 'anita.db' not found at {BASE_DIR}.")
        print("   If you haven't set up the CMS yet, run 'python main.py' first.")
        print("   Attempting to connect anyway (in case of external DB)...")

    # 5. Execute Generation
    try:
        # You can change "dist" to any output folder you prefer
        output_folder = "dist"
        
        generator = SSGGenerator(output_dir=output_folder)
        generator.generate()
        
        print("\n---------------------------------------------------------")
        print(f"✨ Success! Your static site is ready in: /{output_folder}")
        print("---------------------------------------------------------")
        
    except Exception as e:
        print(f"\n❌ Critical Error during generation: {e}")
        # Helpful debugging for database issues
        if "no such table" in str(e):
            print("   (Hint: It looks like the database isn't fully migrated.)")

if __name__ == "__main__":
    run_ssg()