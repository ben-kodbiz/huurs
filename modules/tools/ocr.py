from modules.llm.llm_engine import LMStudioLLM

llm = LMStudioLLM()

def extract(image):
    """Extract text from image using LLM vision capabilities"""
    
    return llm.extract_text_from_image(image)
