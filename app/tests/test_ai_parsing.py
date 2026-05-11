import asyncio
import os
import json
import sys
from dotenv import load_dotenv
from app.services.resume_parser import ResumeParserService

# Load environment variables
load_dotenv()

async def test_real_pdf_parsing(test_file_path: str):
    service = ResumeParserService()
    
    if not os.path.exists(test_file_path):
        print(f"Error: {test_file_path} not found.")
        return

    print(f"Testing parsing for real PDF file: {test_file_path}")
    
    try:
        # Call the service
        result = await service.parse_resume(file_path=test_file_path)
        
        print("\n--- AI Parsed Results ---")
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        # Save output to a JSON file with a dynamic name
        base_name = os.path.splitext(os.path.basename(test_file_path))[0]
        output_file = f"parsed_{base_name}_output.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    # Get file path from command line arguments or use default
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = "resume.pdf"
        
    asyncio.run(test_real_pdf_parsing(target_file))
