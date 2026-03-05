# 🔍 Sign Reader Feature (In Development)

## Branch: `feature/sign-reader`

### Overview
This feature adds AI-powered parking sign analysis using LLaVA vision model. Users can upload photos of parking signs to get intelligent, context-aware explanations that understand multilingual text and the nuances of parking regulations.

### Key Characteristics
- ✅ **Privacy First** - All processing happens on-device via Ollama, no images stored on servers
- ✅ **Free** - Uses LLaVA (open-source vision model), no API costs
- ✅ **Multilingual** - Understands text in multiple languages naturally
- ✅ **Context-Aware** - AI understands parking logic, not just keywords
- ✅ **Lightweight** - Efficient local inference on consumer hardware
- ✅ **Intelligent** - Provides nuanced explanations of complex parking rules

### How It Works
1. User uploads a parking sign photo
2. LLaVA AI analyzes the image and extracts text
3. AI generates context-aware explanation of the parking rules
4. Image is never saved - only analyzed in-memory
5. Can handle multiple languages in same image

### What It Can Understand
- Complex multi-part restrictions (e.g., "No parking Mon-Fri 8am-6pm except holidays")
- Time-based rules (specific hours, days, seasons)
- Permit requirements (resident permits, special permits)
- Paid parking configurations (hourly rates, daily maximums)
- Temporary restrictions (construction, events)
- Confusing or poorly formatted signs
- Signs in different languages
- Handwritten modifications or additions

### Dependencies Added
```
requests>=2.28.0    # HTTP client for Ollama API
pillow>=9.0.0       # Image processing (already had)
```

### System Requirements
- **Ollama**: Local LLM inference engine
  - Download from: https://ollama.ai
  - Start with: `ollama serve`
- **LLaVA Model**: Vision-capable LLM
  - Auto-installed: `ollama pull llava`
  - Size: ~4.1 GB
  - Inference: 10-30 seconds per image

### Setup Instructions

1. **Install Ollama** (if not already installed)
   ```bash
   brew install ollama
   ```

2. **Start Ollama service**
   ```bash
   ollama serve
   # OR run as background service:
   brew services start ollama
   ```

3. **Pull LLaVA model** (first time only)
   ```bash
   ollama pull llava
   ```

4. **Run SignSpot**
   ```bash
   streamlit run main.py
   ```

### Privacy & Legal
- No photos stored on servers
- No private data retention
- Completely local analysis
- Complies with privacy requirements
- No external API calls

### Performance Notes
- First inference: ~15-30 seconds (model loading)
- Subsequent inferences: ~10-15 seconds
- Works best with clear, direct photos of signs
- Can handle various angles and lighting conditions

### Advantages over OCR + Keyword Matching
- ✅ Understands context and logic
- ✅ Handles multiple languages
- ✅ Recognizes handwriting/modifications
- ✅ Explains complex rules intelligently
- ✅ Handles edge cases better
- ❌ Slower than simple OCR (but more accurate)

### Future Enhancements (Not in MVP)
- Integration with report submission (quick report sign issues)
- Caching of analyzed signs for faster repeat queries
- Batch processing for multiple sign photos
- Export explanation as PDF
- Multi-language output options

### Testing Scenarios
Good test cases:
- Clear, standard parking signs
- Complex multi-line restrictions
- Signs in different languages
- Damaged or faded signs
- Handwritten modifications
- Photos at various angles

### Troubleshooting
**"Ollama not running" error**
- Make sure Ollama service is started: `brew services start ollama`
- Or run manually: `ollama serve`

**Slow response**
- First run loads the model (~2-3 minutes)
- Subsequent runs are faster
- Normal inference: 10-30 seconds

**VRAM issues**
- LLaVA uses GPU acceleration by default
- Falls back to CPU if needed
- Consider using smaller model if issues persist

### Notes
- This is an experimental feature in active development
- Performance may vary based on hardware
- Designed to be a helper tool, not a definitive answer
- Users should always verify with actual parking signage
