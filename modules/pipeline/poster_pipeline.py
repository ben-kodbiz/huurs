from modules.tools.facebook_scraper import extract_image
from modules.tools.image_downloader import download
from modules.tools.ocr import extract
from modules.tools.quran_parser import detect
from modules.tools.topic_classifier import classify
from modules.tools.embedding_generator import generate_embedding
from modules.tools.database import save

def run(url):

    img = extract_image(url)

    path = download(img,"data/images/poster.jpg")

    text = extract(path)

    verse = detect(text)

    topics = classify(text)

    embedding = generate_embedding(text)

    entry={
        "source":url,
        "text":text,
        "quran_reference":verse,
        "topics":topics,
        "embedding":embedding
    }

    save(entry)

    print("Entry saved")
