import os
import requests

def fake_wget(args):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:

        # Exttract url
        url = next((element for element in args if element.startswith("http")), None)

        # Extract the filename from the URL
        filename = url.split("/")[-1] or "index.html"
        download_path = os.path.join(BASE_DIR, "downloads", filename)

        # Log the URL
        logs = open(os.path.join(BASE_DIR, "downloads/dlog.txt"), "a+", encoding="utf-8")
        logs.write(f"Attempted URL: {url}\n")
        logs.close()    

        # Dowload the file
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the downloaded file
        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    except Exception as e:
        ""