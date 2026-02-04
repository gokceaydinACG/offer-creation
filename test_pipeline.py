"""
Test script for offer processing pipeline.

Tests both Excel and Image inputs with HPC and Food categories.
"""

from pathlib import Path
from runners import process_file

# Paths
INPUT_FOOD = Path("input_offers/food")
INPUT_HPC = Path("input_offers/hpc")
OUTPUT_DIR = Path("offer_outputs")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("🧪 OFFER PROCESSING PIPELINE - TEST")
print("=" * 70)

# Test 1: Image (PNG) → Food
print("\n📸 TEST 1: Screenshot (PNG) → Food Category")
print("-" * 70)
png_file = INPUT_FOOD / "Screenshot 2025-12-03 142332 (1).png"

if png_file.exists():
    try:
        output = process_file(png_file, "food", OUTPUT_DIR)
        print(f"✅ SUCCESS: {output.name}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print(f"⚠️  File not found: {png_file}")

# Test 2: Excel (XLSX) → HPC
print("\n📊 TEST 2: Excel (XLSX) → HPC Category")
print("-" * 70)
xlsx_file = INPUT_HPC / "end of year BEAUTY offer (1).xlsx"

if xlsx_file.exists():
    try:
        output = process_file(xlsx_file, "hpc", OUTPUT_DIR)
        print(f"✅ SUCCESS: {output.name}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print(f"⚠️  File not found: {xlsx_file}")

# Summary
print("\n" + "=" * 70)
print("📂 Check outputs in: offer_outputs/")
print("🔍 Verify:")
print("  1. Article numbers are sequential (AC00001000, AC00001001...)")
print("  2. Food output has BBD column, HPC output doesn't")
print("  3. All fields are properly extracted")
print("=" * 70)