"""Test the poster pipeline with local images."""

from modules.tools.ocr import extract
from modules.tools.quran_parser import detect
from modules.tools.topic_classifier import classify
from modules.tools.embedding_generator import generate_embedding
from modules.tools.database import save

def run_test(image_path):
    """Run pipeline on a local test image."""
    print(f"Testing with: {image_path}")
    print("-" * 50)
    
    # OCR
    print("Extracting text (OCR)...")
    ocr_result = extract(image_path)
    
    # Handle dict response from OCR
    if isinstance(ocr_result, dict):
        text_data = ocr_result.get("text_extraction", ocr_result)
        text = f"{text_data.get('arabic_text', '')} {text_data.get('translation', '')}"
    else:
        text = ocr_result
    
    print(f"Text: {text}")
    print()
    
    # Quran detection
    print("Detecting Quran reference...")
    verse = detect(text)
    print(f"Verse: {verse}")
    print()
    
    # Topic classification
    print("Classifying topics...")
    topics = classify(text)
    print(f"Topics: {topics}")
    print()
    
    # Embedding
    print("Generating embedding...")
    embedding = generate_embedding(text)
    print(f"Embedding size: {len(embedding)} dimensions")
    print()
    
    # Save
    entry = {
        "source": image_path,
        "text": ocr_result,
        "quran_reference": verse,
        "topics": topics,
        "embedding": embedding
    }
    save(entry)
    print("Entry saved to wisdom_db.json")
    print("=" * 50)

if __name__ == "__main__":
    # Test with first image
    run_test("testimage/testLM01.jpg")
