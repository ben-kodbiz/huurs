from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import base64
import uuid
import sys
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.tools.ocr import extract
from modules.tools.quran_parser import detect
from modules.tools.database import save
from modules.llm.llm_engine import LMStudioLLM

app = FastAPI()

# Create directories
Path("data/images").mkdir(parents=True, exist_ok=True)
Path("static").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

llm = LMStudioLLM()

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path("static/index.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Place index.html in static/ folder</h1>")

@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    """Process uploaded image through the pipeline"""
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    image_path = Path(f"data/images/{file_id}.jpg")
    
    # Save uploaded file
    content = await file.read()
    image_path.write_bytes(content)
    
    try:
        # Run OCR (LLM-based structured extraction)
        raw_output = extract(str(image_path))

        # extract() now returns a dict directly, not a string
        if isinstance(raw_output, dict):
            structured_data = raw_output
        else:
            # Fallback: try to parse as JSON
            try:
                structured_data = json.loads(raw_output)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if json_match:
                    structured_data = json.loads(json_match.group())
                else:
                    structured_data = {"text_extraction": {"arabic_text": raw_output}}
        
        # Save to database
        entry = {
            "id": file_id,
            "source": "uploaded_image",
            "structured_data": structured_data
        }
        save(entry)
        
        return JSONResponse({
            "success": True,
            "data": structured_data
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
