# file_uploader.py MinIO Python SDK example
from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import ResponseError
import datetime

# Create a client with the MinIO server playground, its access key
# and secret key.
client = Minio("192.168.3.56:9000",
               access_key="qfgn123456",
               secret_key="qfgn123456",
               secure=False
               )

def upload():
    source_file = r"C:\Users\13018\Desktop\数据.xlsx"
    bucket_name = "other"
    destination_file = "数据.xlsx"

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )


def download():
    remote_file = "-22.jpg"
    # The destination bucket and filename on the MinIO server
    bucket_name = "midasplat"
    destination_file = "-22.jpg"
    try:
        data = client.get_object(bucket_name, destination_file)
        with open(remote_file, 'wb') as file_data:
            for d in data.stream(32 * 1024):
                file_data.write(d)
        print("Sussess")
    except ResponseError as err:
        print(err)

def share():
    remote_file = "-22.jpg"
    bucket_name = "midasplat"
    response = client.presigned_get_object(bucket_name, remote_file, datetime.timedelta(seconds=10))
    print(response)


if __name__ == "__main__":
    try:
        upload()
        # download()
        # share()
    except S3Error as exc:
        print("error occurred.", exc)