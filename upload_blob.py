from azure.storage.blob import BlobServiceClient
import os

# Use GitHub Secret
AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")
CONTAINER_NAME = "blog-data"
BLOB_NAME = "fique_articles.json"
LOCAL_FILE = "fique_articles.json"

def upload():
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
    except Exception as e:
        print("Container likely exists, continuing...")

    with open(LOCAL_FILE, "rb") as data:
        container_client.upload_blob(name=BLOB_NAME, data=data, overwrite=True)
        print("✅ Upload successful.")

if __name__ == "__main__":
    upload()
