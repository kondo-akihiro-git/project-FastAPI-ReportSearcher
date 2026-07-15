# backend/logic/register.py
import json
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# <ローカルディレクトリ>
# FILE_PATH = "data/login/login.json"

# <S3バケット>
S3_BUCKET = os.getenv("S3_LOGIN_BUCKET")
S3_KEY = os.getenv("S3_LOGIN_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")


def save(req, member_no: str):
    # <ローカルディレクトリ>
    # os.makedirs("data/login", exist_ok=True)

    # <S3バケット>
    s3 = boto3.client("s3", region_name=AWS_REGION)

    data = []
    # <ローカルディレクトリ>
    # if os.path.exists(FILE_PATH):
    #     with open(FILE_PATH, encoding="utf-8") as f:
    #         data = json.load(f)

    # <S3バケット>
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        data = json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "NoSuchKey":
            raise
        data = []
    except Exception:
        data = []

    new_login = {
        "basic_username": req.basic_username,
        "basic_password": req.basic_password,
        "portal_username": req.portal_username,
        "portal_password": req.portal_password,
        "member_no": member_no,
    }

    if new_login not in data:
        data.append(new_login)

    # <ローカルディレクトリ>
    # with open(FILE_PATH, "w", encoding="utf-8") as f:
    #     json.dump(data, f, indent=2, ensure_ascii=False)
    
    # <S3バケット>
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )