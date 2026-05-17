import os
import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str

class PresignedUrlResponse(BaseModel):
    url: str
    key: str

def get_s3_client():
    # R2 configuration requires specific endpoint URL and explicit region setup for boto3
    return boto3.client(
        service_name='s3',
        endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="auto" # Cloudflare R2 standard
    )

@router.post("/upload/presigned-url", response_model=PresignedUrlResponse)
def generate_presigned_url(body: PresignedUrlRequest):
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="Bucket name not configured")

    s3_client = get_s3_client()
    
    import uuid
    # Create a unique key for the file
    file_extension = body.filename.split('.')[-1] if '.' in body.filename else 'jpg'
    key = f"condition-reports/{uuid.uuid4()}.{file_extension}"
    
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': body.content_type
            },
            ExpiresIn=3600 # 1 hour
        )
        return PresignedUrlResponse(url=response, key=key)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
