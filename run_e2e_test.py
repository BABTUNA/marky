#!/usr/bin/env python3
"""
AdBoard AI - E2E Test (Drive Upload Only)

Uploads existing video + PDF to Google Drive. No pipeline - uses files already in output/.
Use this to verify Drive upload works without running image generation.

Usage:
    python run_e2e_test.py
"""

from pathlib import Path

from dotenv import load_dotenv

# Project root & load .env
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

def find_existing_files():
    """Find video(s) and PDF(s) in output folder."""
    files = []
    # Videos
    for d in ["output/veo3_videos", "output/viral_videos", "output/final"]:
        p = ROOT / d
        if p.exists():
            for f in p.glob("*.mp4"):
                files.append(str(f))
    # PDFs
    pdf_dir = ROOT / "output/pdfs"
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        if pdfs:
            files.append(str(max(pdfs, key=lambda x: x.stat().st_mtime)))
    return files


def main():
    print("\n" + "=" * 60)
    print("  🎬 AdBoard AI - Drive Upload Test")
    print("=" * 60)
    print("  Uploading existing files to Google Drive...")
    print("  (No pipeline - uses output/ folder as-is)\n")

    from agents.orchestrator import upload_file

    files = find_existing_files()
    if not files:
        print("  ⚠️ No video or PDF files found in output/")
        print("  Create some with: python run_example.py \"Create ad for my coffee shop\"\n")
        return

    for path in files:
        print(f"  📤 {Path(path).name} ...")
        url = upload_file(path)
        if url:
            print(f"     ✅ {url}")
        else:
            print(f"     ❌ Upload failed")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
