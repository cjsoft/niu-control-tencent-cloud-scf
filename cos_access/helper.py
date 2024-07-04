import io
import os
from qcloud_cos import CosConfig, CosS3Client


def default_client():
    secret_id = os.environ.get("COS_SECRET_ID")
    secret_key = os.environ.get("COS_SECRET_KEY")
    region = os.environ.get("COS_REGION")
    use_internal_cos_endpoint = os.environ.get("USE_INTERNAL_COS_ENDPOINT", "0") == "1"
    assert secret_id
    assert secret_key
    assert region

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=None, Scheme="https", EnableInternalDomain=use_internal_cos_endpoint)
    return CosS3Client(config)


class CosSpongeFile(io.BytesIO):
    def __init__(self, client: CosS3Client, bucket: str, key: str):
        self.client = client
        self.bucket = bucket
        self.key = key
        super().__init__()

    def close(self):
        self.client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=self.getvalue(),
        )
        super().close()


class BucketHelper:
    def __init__(self):
        self.client = default_client()
        self.bucket = os.environ.get("COS_BUCKET")
        assert self.bucket

    def sponge_file(self, key: str):
        return CosSpongeFile(self.client, self.bucket, key)

    def put_object(self, key: str, data):
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
        )

    def get_object(self, key: str):
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key,
        )
        return response["Body"].get_raw_stream()

    def object_exists(self, key: str):
        return self.client.object_exists(Bucket=self.bucket, Key=key)
