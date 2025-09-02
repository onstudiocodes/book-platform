# Multilingual PDF Generation

This document explains the multilingual PDF generation feature that supports Bengali, English, and other languages.

## Overview

The book platform includes a robust PDF generation system that can handle:
- Bengali/Bangla text with proper Unicode support
- Mixed language content (Bengali + English)
- Complex script rendering
- Custom page sizes and formatting

## Technical Implementation

### Font Support

The system uses Noto Sans fonts which provide excellent coverage for:
- **Noto Sans Regular**: Latin scripts, numbers, punctuation
- **Noto Sans Bengali**: Bengali/Bangla scripts including complex ligatures

### Key Features

1. **Automatic font fallback**: If custom fonts aren't available, falls back to system fonts
2. **Multiple font paths**: Supports various deployment environments (local, Render, etc.)
3. **Robust error handling**: Graceful degradation if font loading fails
4. **Production optimized**: Fonts are automatically downloaded during deployment

## Setup Instructions

### Local Development

1. Fonts are automatically downloaded when you run the project
2. Test PDF generation with: `python test_pdf_bengali.py`

### Production Deployment (Render)

Fonts are automatically set up during the build process via `build.sh`. No manual intervention required.

### Manual Font Setup

If needed, you can manually set up fonts:

```bash
# Using Django management command
python manage.py setup_fonts

# Or using the shell script
./setup_fonts.sh
```

## Usage

```python
from main.utils import generate_book_pdf

# Generate PDF for a book
pdf_buffer = generate_book_pdf(book)

# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_buffer.read())
```

## Supported Languages

- **Primary**: Bengali/Bangla (বাংলা)
- **Secondary**: English and other Latin scripts
- **Mixed content**: Bengali + English in the same document
- **Numbers**: Both Western (1234) and Bengali (১২৩ৄ) numerals

## Troubleshooting

### PDF shows random symbols/boxes instead of Bengali

This usually means fonts aren't properly loaded. Check:

1. Font files exist in `static/fonts/`
2. Run `python manage.py setup_fonts`
3. Check server logs for font loading errors

### On deployment platforms

1. Ensure build script runs successfully
2. Check if fonts are downloaded during build
3. Verify `STATIC_ROOT` is properly configured

### Font file paths

The system checks multiple paths:
- `static/fonts/NotoSans-Regular.ttf`
- `static/fonts/NotoSansBengali-Regular.ttf`
- `static/NotoSans-Regular.ttf` (legacy)
- Production paths (`/app/static/`, etc.)

## Configuration

### Custom Font Sizes

```python
# Generate with custom dimensions
pdf_buffer = generate_book_pdf(book, width_px=300, height_px=500)
```

### CSS Customization

The PDF generation uses WeasyPrint with custom CSS. Key styles:

- Font size: 18px (optimized for readability)
- Line height: 1.7 (good for dense text)
- Text align: justified
- Page margins: 8px
- Font features: kerning, ligatures enabled

## Performance Notes

- Fonts are cached after first download
- PDF generation is memory-efficient using BytesIO
- Large books may take a few seconds to process
- Consider implementing background job processing for very large documents

## Dependencies

- `weasyprint`: PDF rendering engine
- `fonttools`: Font handling utilities
- `requests`: Font downloading (build time only)

## File Structure

```
static/
  fonts/
    NotoSans-Regular.ttf          # Primary font
    NotoSansBengali-Regular.ttf   # Bengali support
templates/
  components/
    pdf_template.html             # PDF layout template
main/
  utils.py                       # PDF generation logic
  management/
    commands/
      setup_fonts.py              # Font setup command
```
