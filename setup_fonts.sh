#!/bin/bash
# Deployment script for Render - ensures fonts are available

echo "Setting up fonts for PDF generation..."

# Create fonts directory if it doesn't exist
mkdir -p /app/static/fonts/

# Download fonts if they don't exist
if [ ! -f "/app/static/fonts/NotoSans-Regular.ttf" ]; then
    echo "Downloading Noto Sans Regular..."
    curl -L -o /app/static/fonts/NotoSans-Regular.ttf "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
fi

if [ ! -f "/app/static/fonts/NotoSansBengali-Regular.ttf" ]; then
    echo "Downloading Noto Sans Bengali..."
    curl -L -o /app/static/fonts/NotoSansBengali-Regular.ttf "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf"
fi

# Copy to static root if available
if [ ! -z "$STATIC_ROOT" ] && [ -d "$STATIC_ROOT" ]; then
    cp -r /app/static/fonts/ "$STATIC_ROOT/" 2>/dev/null || true
fi

echo "Font setup complete!"
