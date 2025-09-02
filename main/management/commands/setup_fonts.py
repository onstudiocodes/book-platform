"""
Django management command to setup fonts for PDF generation
Usage: python manage.py setup_fonts
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import requests
from pathlib import Path


class Command(BaseCommand):
    help = 'Setup fonts for multilingual PDF generation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download of fonts even if they exist',
        )

    def handle(self, *args, **options):
        """Setup fonts for PDF generation"""
        self.stdout.write(self.style.SUCCESS('Setting up fonts for PDF generation...'))
        
        # Create fonts directory
        static_dir = Path(settings.BASE_DIR) / 'static'
        fonts_dir = static_dir / 'fonts'
        fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Fonts to download
        fonts = [
            {
                'name': 'Noto Sans Regular',
                'url': 'https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf',
                'filename': 'NotoSans-Regular.ttf'
            },
            {
                'name': 'Noto Sans Bengali',
                'url': 'https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf',
                'filename': 'NotoSansBengali-Regular.ttf'
            }
        ]
        
        for font in fonts:
            font_path = fonts_dir / font['filename']
            
            if font_path.exists() and not options['force']:
                self.stdout.write(f"✅ {font['name']} already exists: {font_path}")
                continue
            
            try:
                self.stdout.write(f"📥 Downloading {font['name']}...")
                response = requests.get(font['url'], stream=True, timeout=30)
                response.raise_for_status()
                
                with open(font_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Downloaded {font['name']}: {font_path}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to download {font['name']}: {str(e)}")
                )
        
        # Also copy to static root if available
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            static_root_fonts = Path(settings.STATIC_ROOT) / 'fonts'
            static_root_fonts.mkdir(parents=True, exist_ok=True)
            
            for font in fonts:
                src_path = fonts_dir / font['filename']
                dst_path = static_root_fonts / font['filename']
                
                if src_path.exists():
                    try:
                        import shutil
                        shutil.copy2(src_path, dst_path)
                        self.stdout.write(f"📁 Copied to STATIC_ROOT: {dst_path}")
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️ Failed to copy to STATIC_ROOT: {str(e)}")
                        )
        
        self.stdout.write(self.style.SUCCESS('🎉 Font setup complete!'))
        
        # Test font availability
        self.stdout.write('\n🔍 Font availability check:')
        test_paths = [
            fonts_dir / 'NotoSans-Regular.ttf',
            fonts_dir / 'NotoSansBengali-Regular.ttf',
            static_dir / 'NotoSans-Regular.ttf',  # Legacy location
        ]
        
        for path in test_paths:
            if path.exists():
                size_kb = path.stat().st_size // 1024
                self.stdout.write(f"✅ {path} ({size_kb} KB)")
            else:
                self.stdout.write(f"❌ {path}")
