# AdBoard AI - Master Context Restore 🧠

> **Snapshot Date:** February 1, 2026
> **System Status:** 🟢 STABLE / GROUNDWORK COMPLETE
> **Critical Change:** Migration to Google Gemini + VEO 3 Groundwork

---

## 1. Project Overview & Mission
**AdBoard AI** is a multi-agent system that generates complete advertising campaigns for local businesses.
- **Input:** Business Name, Industry, City
- **Output:**
    1.  **PDF Campaign Package:** Strategy, scripts, budget, distribution plan.
    2.  **Storyboard Video:** Black & white hand-drawn sketches (concept validation).
    3.  **Viral Video (Mock/Ready):** Photorealistic VEO 3 video + music + voiceover (infrastructure ready).

---

## 2. Recent Critical Architecture Changes

### 🟢 Switched to Google Gemini (Vertex AI)
- **Why:** To utilize $410 Google Cloud credits and avoid Groq rate limits.
- **Status:** **COMPLETE & ACTIVE**.
- **Key File:** [`core/gemini_client.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/core/gemini_client.py)
- **All Agents Updated:** Script writer, social media, trend analyzer, etc. all use `GeminiClient`.

### 🟢 PDF Campaign Package Overhaul
- **Enhancement:** Shifted from simple output to "Complete Campaign Strategy".
- **New Sections:**
    - Strategy Overview & distribution plan
    - A/B Testing Recommendations
    - Budget Allocation & Timeline
- **Key File:** [`agents/campaign_strategy_content.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/agents/campaign_strategy_content.py)

### 🟢 Storyboard Aesthetics
- **Change:** Adjusted Imagen prompts for **Hand-Drawn Disney/Pixar Style**.
- **Fixed:** Eliminated borders, frames, and collages. Images are now single, fullscreen sketches.
- **Key File:** [`agents/image_generator.py`](file:///Users/tomalmog/programming/Febuary%202026/Brown/agents/image_generator.py) (lines 253-269)

### 🟡 Viral Video System (Groundwork Complete)
- **New Agents:** VEO 3 (Video), Lyria (Music), Video Assembler (Merge).
- **Status:** **Infrastructure Ready but DISABLED** (Commented out to save credits/wait for access).
- **Key Files:** `agents/veo3_agent.py`, `agents/lyria_agent.py`, `agents/viral_video_assembler.py`.

---

## 3. Current File Manifest (Critical Files)

| File Path | Purpose | Status |
|-----------|---------|--------|
| `agents/orchestrator.py` | Main entry point. Handles flow & final output formatting. | ✅ Updated for Viral Video |
| `core/pipeline.py` | Defines agent execution order. | ✅ Updated with `viral_video` config |
| `core/gemini_client.py` | LLM Backend (Vertex AI). | ✅ Active |
| `agents/veo3_agent.py` | Google VEO 3 video generation. | ⏸️ Groundwork (Disabled) |
| `agents/lyria_agent.py` | Google Lyria music generation. | ⏸️ Groundwork (Disabled) |
| `agents/viral_video_assembler.py` | Merges Video + Audio + TTS. | ⏸️ Groundwork (Disabled) |
| `agents/image_generator.py` | Storyboard images (Imagen). | ✅ Active (Hand-Drawn) |
| `agents/pdf_builder.py` | Generates final PDF package. | ✅ Active (Updated) |

---

## 4. How to Resume Work (The "Don't Break It" Guide)

### 🅰️ To Run Standard Storyboard Pipeline (Current Default)
Just run the orchestrator. It uses the default "storyboard" or "full" pipeline which **excludes** VEO 3.
```bash
python agents/orchestrator.py
```
*Result: Hand-drawn storyboard video + PDF Package.*

### 🅱️ To Enable Viral Video (The "Flip Switch" Method)
When ready to generate real viral videos (costing ~$2.00/video):

1.  **Uncomment Code in Agents:**
    -   `agents/veo3_agent.py`: Uncomment `_generate_video` call.
    -   `agents/lyria_agent.py`: Uncomment `_generate_music` call.
    -   `agents/viral_video_assembler.py`: Uncomment TTS and moviepy assembly.

2.  **Uncomment Pipeline in `core/pipeline.py`:**
    ```python
    # In PIPELINES dict:
    "viral_video": [ ... ] # Uncomment this block
    ```

3.  **Install Dependencies:**
    ```bash
    pip install moviepy google-cloud-texttospeech
    ```

---

## 5. Configuration & Environment

**Required Env Vars (`.env`):**
- `GCP_PROJECT_ID`: (Your Project ID)
- `GCP_REGION`: `us-central1`
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to JSON key
- `TMPFILES_API_KEY`: (Optional, handles uploads)

**APIs in Use:**
- **LLM:** Vertex AI (Gemini Pro)
- **Image:** Vertex AI (Imagen 3)
- **Video:** Vertex AI (VEO 3) [Disabled]
- **Music:** Vertex AI (Lyria) [Disabled]
- **Search:** Google Custom Search / SerpAPI

---

## 6. What's Left to Do?

1.  **VEO 3 Access:** Confirm your Google Cloud project has access to `veo-3` and `lyria` models.
2.  **Enable Pipeline:** Follow the "Flip Switch" method above.
3.  **Demo Mode:** If you want to show the *flow* without generating, you can modify `viral_video_assembler.py` to return a static mock video path instead of `None`.

**Current State:** The code is clean, modular, and ready. **No immediate coding is required** unless you are activating the VEO pipeline.

---
*Created by Antigravity | February 1, 2026*
