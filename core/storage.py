import asyncio
import json
import logging
from io import BytesIO

from minio import Minio

from core.settings import settings

logger = logging.getLogger(__name__)

_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


async def setup_bucket() -> None:
    def _setup() -> None:
        if not _client.bucket_exists(settings.MINIO_BUCKET):
            _client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Bucket MinIO créé : {settings.MINIO_BUCKET}")
        policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"],
            }],
        })
        _client.set_bucket_policy(settings.MINIO_BUCKET, policy)

    await asyncio.to_thread(_setup)


async def upload_file(object_name: str, content: bytes, content_type: str = "application/octet-stream") -> str:
    def _upload() -> None:
        _client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

    await asyncio.to_thread(_upload)
    return public_url(object_name)


async def delete_file(object_name: str) -> None:
    def _delete() -> None:
        _client.remove_object(settings.MINIO_BUCKET, object_name)

    await asyncio.to_thread(_delete)


def public_url(object_name: str) -> str:
    return f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET}/{object_name}"
