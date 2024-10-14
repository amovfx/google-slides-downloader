import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/presentations.readonly"]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def extract_presentation_id(url):
    match = re.search(r"/presentation/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Slides URL")


def download_slides_as_images(url, output_dir):
    presentation_id = extract_presentation_id(url)
    creds = get_credentials()
    service = build("slides", "v1", credentials=creds)

    # Get presentation details
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    presentation_title = presentation["title"]

    # Create output directory
    output_folder = os.path.join(output_dir, presentation_title)
    os.makedirs(output_folder, exist_ok=True)

    # Get the total number of slides
    slides = presentation.get("slides", [])

    # Download each slide as an image
    for i, slide in enumerate(slides):
        request_body = {
            "url": f"https://docs.google.com/presentation/d/{presentation_id}/export/png",
            "outputMimeType": "PNG",
            "pageObjectId": slide["objectId"],
        }
        response = (
            service.presentations()
            .pages()
            .getThumbnail(
                presentationId=presentation_id, pageObjectId=slide["objectId"]
            )
            .execute()
        )

        if "contentUrl" in response:
            image_url = response["contentUrl"]
            image_data = requests.get(image_url).content
            file_name = f"slide_{i+1}.png"
            file_path = os.path.join(output_folder, file_name)
            with open(file_path, "wb") as file:
                file.write(image_data)
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download slide {i+1}")

    print(f"All slides downloaded to: {output_folder}")


# /Users/andrew/Documents/Adobe/Premiere Pro/24.0/saga/01_Intro
if __name__ == "__main__":
    # slides_url = input("Enter the Google Slides URL: ")
    # output_directory = input("Enter the output directory path: ")
    download_slides_as_images(
        "https://docs.google.com/presentation/d/1ya7osQNDpotz94Ug4SLNi2Y_arY01BGlj_xeNC94_Ik/edit#slide=id.p",
        "/Users/andrew/Documents/Adobe/Premiere Pro/24.0/saga/01_Intro",
    )
