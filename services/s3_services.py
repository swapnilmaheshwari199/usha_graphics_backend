import boto3
import os
import requests
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

# Credentials from Step 2
ACCOUNT_ID = os.environ.get("CLOUDFARE_ACCESS_KEY_ID")
ACCESS_KEY = os.environ.get("CLOUDFARE_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("CLOUDFARE_SECRET_ACCESS_KEY")
ENDPOINT = os.environ.get("CLOUDFARE_ENDPOINT")
BUCKET_NAME = "order-files"

class s3Service:
    def __init__(self):
        self.account_id = ACCOUNT_ID
        self.access_key = ACCESS_KEY
        self.secret_key = SECRET_KEY
        self.endpoint = ENDPOINT
        self.bucket_name = BUCKET_NAME
        self.s3_client =  boto3.client(
                            "s3",
                            endpoint_url=self.endpoint,
                            aws_access_key_id=self.access_key,
                            aws_secret_access_key=self.secret_key,
                            config=Config(signature_version="s3v4"),
                            region_name="auto" # R2 ignores region but needs this
                        )


    async def file_upload(self,filename, filecontent):
        try:
            print("Uplaoding File")
            upload_url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": BUCKET_NAME, "Key": filename},
                ExpiresIn=3600  # URL expires in 1 hour
            )           
            # Upload the file
            response = requests.put(
                upload_url, 
                data=filecontent,
                headers={"Content-Type": "application/pdf"},
                verify=False
            )

            if response.status_code == 200:
                print("Successfully uploaded to Cloudflare R2!")
                return True
            else:
                print(f"Upload failed: {response.status_code}")
                print(response.text)
                return False
            
        except Exception as e:
            print(e)

    
    async def downlaod_file(self, filename):
        try:
            download_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=3600
            )
            return download_url
        except Exception as e:
            print(e)
            return False