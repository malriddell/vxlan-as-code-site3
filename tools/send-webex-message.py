import os
import sys
import argparse
import requests
import zipfile

def zip_artifacts(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, start=source_dir)
                zipf.write(filepath, arcname)

def send_webex_file(token, room_id, file_path, message_text=None):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    files = {
        'files': open(file_path, 'rb')
    }
    data = {
        "roomId": room_id
    }
    if message_text:
        data["text"] = message_text

    response = requests.post(url, headers=headers, data=data, files=files)
    if response.status_code not in (200, 202):
        print(f"Failed to send file: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Send zipped artifacts to Webex Teams")
    parser.add_argument("--room-id", required=True, help="Webex Teams Room ID")
    parser.add_argument("--token", required=True, help="Webex Bot Access Token")
    parser.add_argument("--artifacts-dir", required=True, help="Directory containing artifacts to zip")
    parser.add_argument("--zip-name", default="artifacts.zip", help="Name of the zip file to create")
    parser.add_argument("--message", default=None, help="Optional message text to send with the file")
    args = parser.parse_args()

    zip_artifacts(args.artifacts_dir, args.zip_name)
    send_webex_file(args.token, args.room_id, args.zip_name, args.message)

if __name__ == "__main__":
    main()