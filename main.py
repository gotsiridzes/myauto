import argparse
import asyncio
import json
import aiohttp
import os
import zipfile
from os import getenv
from dotenv import load_dotenv
import boto3
from my_args import bucket_arguments

parser = argparse.ArgumentParser(
    description="CLI program that helps with S3 buckets.",
    prog='main.py',
    epilog='DEMO APP - 2 FOR BTU_AWS'
)

subparsers = parser.add_subparsers(dest='command')
bucket = bucket_arguments(subparsers.add_parser(
    "bucket", help="work with Bucket/s"))

# Specify the endpoint URL


def auto_page_n(
    nth_page): return f"https://api2.myauto.ge/ka/products?TypeID=0&ForRent=&Mans=&CurrencyID=3&MileageType=1&Page={nth_page}"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3"
}

load_dotenv()


async def download_image(session, url, save_directory):
    try:
        async with session.get(url) as response:
            response.raise_for_status()

            # Extract the filename from the URL
            filename = os.path.basename(url)

            # Save the image to the specified directory
            save_path = os.path.join(save_directory, filename)
            with open(save_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            print(f"Downloaded: {filename}")
    except aiohttp.ClientError as e:
        print(f"Error downloading image: {e}")


async def main():
    aws_s3_client = init_client()
    args = parser.parse_args()

    match args.command:
        case "bucket":
            if args.download_myauto_pictures:

                image_urls = []  # List to store image URLs

                async with aiohttp.ClientSession(headers=headers) as session:
                    for page_n in range(1):
                        response = await session.get(auto_page_n(page_n))
                        response.raise_for_status()

                        data = await response.json()

                        for item in data['data']['items']:
                            car_id = item['car_id']
                            photo = item['photo']
                            picn = item['pic_number']
                            print(f"Car ID: {car_id}")
                            print("Image URLs:")
                            for id in range(1, picn + 1):
                                image_url = f"https://static.my.ge/myauto/photos/{photo}/large/{car_id}_{id}.jpg"
                                image_urls.append(image_url)
                                print(image_url)
                            print()

                    # Create a folder to store downloaded images
                    save_directory = "downloaded_images"
                    os.makedirs(save_directory, exist_ok=True)

                    # Download images asynchronously
                    tasks = []
                    async with aiohttp.ClientSession() as session:
                        for url in image_urls:
                            task = asyncio.ensure_future(
                                download_image(session, url, save_directory))
                            tasks.append(task)

                        await asyncio.gather(*tasks)
                    print(f"\nAll images downloaded successfully.")

                    total_images = sum(len(files)
                                       for _, _, files in os.walk(save_directory))
                    print(f"Total number of downloaded images: {total_images}")

            if args.archive_myauto_pictures:
                zip_filename = "downloaded_images.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                    for root, _, files in os.walk(save_directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zip_file.write(file_path, arcname=file)

                print(f"\nAll images zipped successfully.")
                zip_file_size_mb = os.path.getsize(
                    zip_filename) / (1024 * 1024)
                print(f"ZIP file size: {zip_file_size_mb:.2f} MB")

            if args.upload_myauto_pictures:
                limit = 10
                for root, _, files in os.walk(save_directory):
                        for file_name in files:
                            if(limit > 0):
                                file_path = os.path.join(root, file_name)
                                # print(f"file_path: {file_path} file: {file_name}")
                                
                                with open(file_path, "rb") as file:
                                    aws_s3_client.upload_fileobj(
                                        file,
                                        args.name,
                                        file_name#,
                                        #ExtraArgs={'ContentType': content_type}
                                    )
                                print(f"Uploaded {file_name} to bucket `{args.name}`")
                                limit = limit - 1
                print(f"Finished uploading TOP {limit} pictures to aws s3 bucket `{args.name}`")
                                
            if args.assign_read_policy == "True":
                policy = json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{args.name}/*",
                        }
                    ],
                })

                if (not policy):
                    print('please provide policy')
                    return

                aws_s3_client.put_bucket_policy(
                    Bucket=args.name, Policy=policy
                )
                print("Bucket multiple policy assigned successfully")


def init_client():
    client = boto3.client("s3",
                          aws_access_key_id=getenv("aws_access_key_id"),
                          aws_secret_access_key=getenv(
                              "aws_secret_access_key"),
                          aws_session_token=getenv("aws_session_token"),
                          region_name=getenv("aws_region_name")
                          #  config=botocore.client.Config(
                          #      connect_timeout=conf.remote_cfg["remote_timeout"],
                          #      read_timeout=conf.remote_cfg["remote_timeout"],
                          #      region_name=conf.remote_cfg["aws_default_region"],
                          #      retries={
                          #          "max_attempts": conf.remote_cfg["remote_retries"]}
                          )
    # check if credentials are correct
    client.list_buckets()

    return client


asyncio.run(main())
