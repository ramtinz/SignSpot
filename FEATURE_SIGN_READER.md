# 🔍 Sign Reader Feature (In Development)

## Branch: `feature/sign-reader`

### Overview
This feature adds the ability for users to upload photos of parking signs and have them analyzed on-device to extract text and provide simple explanations.

### Key Characteristics
- ✅ **Privacy First** - All processing happens on-device, no images stored on servers
- ✅ **Free** - Uses Tesseract OCR (open-source), no API costs
- ✅ **Lightweight** - No heavy ML models, just efficient OCR
- ✅ **Minimal UI** - Simple upload → extract → explain workflow

### How It Works
1. User uploads a parking sign photo
2. Tesseract OCR extracts all visible text from the image
3. Simple keyword-based analysis provides straightforward explanations
4. Image is never saved - only text extraction is used

### Supported Sign Types
The feature recognizes and explains:
- ❌ No parking/stopping/waiting restrictions
- 💰 Paid parking areas
- 🔐 Permit-required zones
- ⏱️ Time-limited parking
- 📅 Day-specific restrictions
- 🚨 Towing warnings
- ✅ Free parking areas

### Dependencies Added
```
pillow>=9.0.0       # Image processing
pytesseract>=0.3.10 # OCR engine wrapper
```

### Setup Requirements
Users need to have Tesseract installed on their system:
- **macOS**: `brew install tesseract`
- **Linux**: `apt-get install tesseract-ocr`
- **Windows**: Download installer from https://github.com/UB-Mannheim/tesseract/wiki

### Privacy & Legal
- No photos stored on servers
- No private data retention
- Images are processed and immediately discarded
- Complies with privacy requirements

### Future Enhancements (Not in scope for MVP)
- Integration with report submission (quick report sign issues)
- Multi-language support
- Handwriting recognition for digital signs
- Database of known confusing signs

### Testing
Branch is ready for:
1. Local testing with various parking sign photos
2. OCR accuracy testing on different image qualities
3. Explanation logic refinement
4. UX feedback from users

### Notes
- Tesseract accuracy varies with image quality (lighting, angle, distance)
- Works best with clear, well-lit photos
- Simple keyword matching keeps processing fast and local
- Designed to be a helper tool, not a definitive answer
