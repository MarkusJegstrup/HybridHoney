import os
import subprocess
import requests

def fake_wget(args):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        # Parse the URL from the args
        url = args
        print("Url: " + url + "\n")

        # Extract the filename from the URL
        filename = url.split("/")[-1] or "index.html"
        download_path = os.path.join(BASE_DIR, "downloads", filename)
        print("Filename: " + filename + "\n")
        
        # Log the wget command and URL
        logs = open(os.path.join(BASE_DIR, "dlog.txt"), "a+", encoding="utf-8")
        logs.write(f"wget command: {' '.join(args)}\n")
        logs.write(f"Attempted URL: {url}\n")
        logs.close()    


        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the downloaded file
        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Ensure the file is owned by simon
        subprocess.run(["chown", "simon:simon", download_path], check=True)

        print(f"'{filename}' saved [{len(response.content)}/{len(response.content)}]")
    except Exception as e:
        print(f"wget: {str(e)}")