#!/usr/bin/env python3
"""
Cleanup Script - Remove Redundant Files
Backs up old files before removal
"""
import os
import shutil
from datetime import datetime

# Files to remove (made redundant by refactoring)
REDUNDANT_FILES = [
    'main.py',  # Replaced by analyze.py
    'data_fetcher.py',  # Replaced by data/fetcher.py
    'investment_agent.py',  # Replaced by agents/base_agent.py
    'valuation_engine.py',  # Replaced by valuation/dcf_calculator.py
]

# Documentation files to consolidate
REDUNDANT_DOCS = [
    'CHECKLIST.md',  # Project management doc
    'COMMANDS.md',  # Covered in README
    'FILE_STRUCTURE.md',  # Outdated
    'MODEL_UPDATE_NOTES.md',  # Historical notes
    'TROUBLESHOOTING_PRO_ERROR.md',  # Specific issue resolved
    'V2_COMPLETION_SUMMARY.md',  # Historical
    'V2_UPGRADE_GUIDE.md',  # Historical
]

DOCS_TO_KEEP = [
    'README.md',
    'README_NEW.md',  # New comprehensive README
    'ARCHITECTURE.md',
    'BUGFIX_NOTES.md',
    'QUICKSTART.md',
    'EXAMPLES.md',
]


def create_backup():
    """Create backup directory with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_and_remove(files: list, backup_dir: str, dry_run: bool = True):
    """Backup files to backup directory and optionally remove them"""
    for filename in files:
        if os.path.exists(filename):
            # Backup
            backup_path = os.path.join(backup_dir, filename)
            os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)
            shutil.copy2(filename, backup_path)
            print(f"✅ Backed up: {filename} -> {backup_path}")
            
            # Remove (if not dry run)
            if not dry_run:
                os.remove(filename)
                print(f"🗑️  Removed: {filename}")
        else:
            print(f"⚠️  Not found: {filename}")


def main():
    print("="*80)
    print("CLEANUP SCRIPT - Refactored Project Structure")
    print("="*80)
    print()
    
    # Ask for confirmation
    print("This script will:")
    print("1. Backup old files to backup_YYYYMMDD_HHMMSS/")
    print("2. Remove redundant files:")
    print()
    print("   Code Files to Remove:")
    for f in REDUNDANT_FILES:
        print(f"   - {f}")
    print()
    print("   Documentation Files to Remove:")
    for f in REDUNDANT_DOCS:
        print(f"   - {f}")
    print()
    print("   Documentation Files to Keep:")
    for f in DOCS_TO_KEEP:
        print(f"   ✓ {f}")
    print()
    
    response = input("Proceed with cleanup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    # Create backup
    print("\n📦 Creating backup...")
    backup_dir = create_backup()
    print(f"   Backup directory: {backup_dir}/")
    
    # Backup and remove redundant files
    print("\n🔧 Cleaning up code files...")
    backup_and_remove(REDUNDANT_FILES, backup_dir, dry_run=False)
    
    print("\n📚 Cleaning up documentation...")
    backup_and_remove(REDUNDANT_DOCS, backup_dir, dry_run=False)
    
    print("\n" + "="*80)
    print("✅ CLEANUP COMPLETE!")
    print("="*80)
    print()
    print(f"✅ Old files backed up to: {backup_dir}/")
    print("✅ Redundant files removed")
    print("✅ Project structure is now clean and modular")
    print()
    print("Next steps:")
    print("1. Review the new README: README_NEW.md")
    print("2. Test the refactored system: python analyze.py")
    print("3. If everything works, delete backup directory")
    print()


if __name__ == "__main__":
    main()
