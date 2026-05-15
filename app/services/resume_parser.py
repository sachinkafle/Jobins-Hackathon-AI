import os
import json
import logging
import httpx
import boto3
from typing import Dict, Any, Optional
from pypdf import PdfReader
from io import BytesIO
from urllib.parse import urlparse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.services.prompts import RESUME_PARSER_SYSTEM_PROMPT, RESUME_PARSER_USER_PROMPT
from app.models.schemas import ResumeData

logger = logging.getLogger(__name__)

class ResumeParserService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    async def download_file(self, file_path: str) -> bytes:
        # 1. Check if it's an S3 URI (s3://bucket/key)
        parsed_url = urlparse(file_path)
        if parsed_url.scheme == 's3':
            bucket = parsed_url.netloc or os.getenv("AWS_S3_BUCKET") or os.getenv("AWS_BUCKET")
            key = parsed_url.path.lstrip('/')
            logger.info(f"Downloading from S3: bucket={bucket}, key={key}")
            s3 = boto3.client('s3', region_name=os.getenv("AWS_REGION", "ap-northeast-1"))
            response = s3.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        
        # 2. Check if it's an HTTP/HTTPS URL
        elif parsed_url.scheme in ['http', 'https']:
            logger.info(f"Downloading from URL: {file_path}")
            async with httpx.AsyncClient() as client:
                response = await client.get(file_path)
                response.raise_for_status()
                return response.content
        
        # 3. Handle as a potential filename or local path
        else:
            # If AWS_S3_BUCKET or AWS_BUCKET is set, try S3 first
            bucket = os.getenv("AWS_S3_BUCKET") or os.getenv("AWS_BUCKET")
            if bucket:
                try:
                    logger.info(f"Attempting S3 download for filename '{file_path}' using bucket '{bucket}'")
                    s3 = boto3.client('s3', region_name=os.getenv("AWS_REGION", "ap-northeast-1"))
                    response = s3.get_object(Bucket=bucket, Key=file_path)
                    return response['Body'].read()
                except Exception as e:
                    logger.warning(f"S3 download failed for '{file_path}', falling back to local: {e}")
            
            # Finally, check local filesystem
            if os.path.exists(file_path):
                logger.info(f"Loading local file from {file_path}")
                with open(file_path, 'rb') as f:
                    return f.read()
            
            raise ValueError(f"File not found locally or in S3: {file_path}")

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    async def parse_resume(self, file_path: str, file_name: Optional[str] = None, upload_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Default names if not provided
            if not file_name:
                file_name = os.path.basename(file_path)
            if not upload_name:
                upload_name = file_name

            file_bytes = await self.download_file(file_path)
            
            # Detect PDF
            if file_path.lower().endswith('.pdf') or file_bytes.startswith(b'%PDF'):
                logger.info("Extracting text from PDF")
                resume_text = self.extract_text_from_pdf(file_bytes)
            else:
                logger.info("Treating file as plain text")
                resume_text = file_bytes.decode('utf-8', errors='ignore')
            
            if not resume_text.strip():
                raise ValueError("Could not extract any text from the file.")

            logger.info("Sending text to AI for parsing")
            prompt = ChatPromptTemplate.from_messages([
                ("system", RESUME_PARSER_SYSTEM_PROMPT),
                ("user", RESUME_PARSER_USER_PROMPT)
            ])
            
            chain = prompt | self.llm
            response = await chain.ainvoke({"resume_text": resume_text})
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            data_dict = json.loads(content)
            
            # Use Pydantic model to ensure all keys are present and have default values
            # This replaces the manual 'default_schema' dictionary
            resume_data = ResumeData(**data_dict)
            
            # Add file info (overriding whatever AI might have guessed)
            resume_data.file = {
                "url": file_path,
                "file_name": file_name,
                "upload_name": upload_name,
                "uuid": False
            }
            
            # Ensure document_parsed_id is at least 0
            if not resume_data.document_parsed_id:
                resume_data.document_parsed_id = 0

            return resume_data.model_dump()

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise e

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise e
