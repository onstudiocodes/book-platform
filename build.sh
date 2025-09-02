#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Set up fonts for PDF generation using Django management command
echo "Setting up fonts for multilingual PDF support..."
python manage.py setup_fonts || {
    echo "Management command failed, trying manual setup..."
    mkdir -p static/fonts/
    
    # Download Noto Sans fonts if they don't exist
    if [ ! -f "static/fonts/NotoSans-Regular.ttf" ]; then
        echo "Downloading Noto Sans Regular..."
        curl -L -o static/fonts/NotoSans-Regular.ttf "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf" || echo "Failed to download NotoSans-Regular.ttf"
    fi

    if [ ! -f "static/fonts/NotoSansBengali-Regular.ttf" ]; then
        echo "Downloading Noto Sans Bengali..."
        curl -L -o static/fonts/NotoSansBengali-Regular.ttf "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf" || echo "Failed to download NotoSansBengali-Regular.ttf"
    fi
}

echo "Font setup complete!"

python manage.py collectstatic --no-input
python manage.py migrate