from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from zlm import AutoApplyModel
from zlm.variables import LLM_MAPPING

app = FastAPI()

class ResumeRequest(BaseModel):
    resume_data: str
    job_description: str
    provider: str
    model: str
    api_key: str
    generate_cover_letter: bool = False

@app.get("/")
async def root():
    return {"message": "Resume Generator API is running"}

@app.post("/generate")
async def generate_resume(request: ResumeRequest):
    try:
        if request.provider not in LLM_MAPPING:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        if request.model not in LLM_MAPPING[request.provider]['model']:
            raise HTTPException(status_code=400, detail="Invalid model for selected provider")
        
        if not request.api_key and request.provider != "Llama":
            raise HTTPException(status_code=400, detail="API key is required")

        # Initialize the model
        resume_llm = AutoApplyModel(
            api_key=request.api_key,
            provider=request.provider,
            model=request.model
        )

        # Extract user data from the provided resume data
        user_data = resume_llm.user_data_extraction(
            resume_content=request.resume_data
        )

        if user_data is None:
            raise HTTPException(status_code=400, detail="Could not process resume data")

        # Extract job details
        job_details, _ = resume_llm.job_details_extraction(
            job_site_content=request.job_description
        )

        if job_details is None:
            raise HTTPException(status_code=400, detail="Could not process job description")

        response = {}

        # Generate resume
        resume_path, resume_details = resume_llm.resume_builder(
            job_details,
            user_data
        )
        
        if resume_path and resume_details:
            with open(resume_path, 'rb') as f:
                resume_content = f.read()
            response['resume'] = {
                'content': resume_content.decode('latin1'),
                'details': resume_details
            }

        # Generate cover letter if requested
        if request.generate_cover_letter:
            cv_details, cv_path = resume_llm.cover_letter_generator(
                job_details,
                user_data
            )
            
            if cv_path and cv_details:
                with open(cv_path, 'rb') as f:
                    cv_content = f.read()
                response['cover_letter'] = {
                    'content': cv_content.decode('latin1'),
                    'details': cv_details
                }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
