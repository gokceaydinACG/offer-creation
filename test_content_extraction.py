"""Debug: Test content extraction from description."""

import re

def extract_content_from_description(description):
    """Extract content from description."""
    if not description:
        return None
    
    # Pattern: number (with optional decimal) + unit (GR, KG, ML, L)
    pattern = r'\b(\d+(?:\.\d+)?)\s*(GR|KG|ML|L)\b'
    
    match = re.search(pattern, description.upper())
    if match:
        number = match.group(1)
        unit = match.group(2)
        return f"{number}{unit}"
    
    return None

# Test cases
test_descriptions = [
    "LU PRINCE MINISTAR 187GR MILK 60 PACK",
    "LU PRINCE MINISTAR MILK",  # Already cleaned
    "COCA COLA 330ML ZERO",
    "NIVEA 200 ML SHAVING FOAM",
    "WATER 1.5L BOTTLE",
]

print("="*70)
print("TESTING CONTENT EXTRACTION FROM DESCRIPTIONS")
print("="*70)

for desc in test_descriptions:
    result = extract_content_from_description(desc)
    status = "✓" if result else "✗"
    print(f"\n{status} '{desc}'")
    print(f"   → Result: {result}")

print("\n" + "="*70)
print("\nNow test with YOUR actual output:")
print("="*70)

# Ask user to paste their actual description
print("\nPaste the Product Description from your screenshot output here:")
print("(or press Ctrl+C to skip)")

try:
    user_desc = input("> ")
    if user_desc:
        result = extract_content_from_description(user_desc)
        print(f"\n✓ Extracted: {result if result else 'NOTHING FOUND'}")
except KeyboardInterrupt:
    print("\n\nSkipped.")