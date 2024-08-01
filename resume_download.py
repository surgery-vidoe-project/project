import os
import requests
from tqdm import tqdm
from requests.exceptions import RequestException, ChunkedEncodingError, ConnectionError
from urllib3.exceptions import ProtocolError

def download_file(url, file_path, retries=1):
    headers = {}
    if os.path.exists(file_path):

        headers['Range'] = f'bytes={os.path.getsize(file_path)}-'

    attempt = 0
    while attempt < retries:
        try:
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0)) + os.path.getsize(file_path)
                mode = 'ab' if response.status_code == 206 else 'wb'

                with open(file_path, mode) as f:
                    initial_size = os.path.getsize(file_path)
                    with tqdm(total=total_size, initial=initial_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
            break
        except (ChunkedEncodingError, ConnectionError, ProtocolError, RequestException) as e:
            attempt += 1
            print(f"Error occurred: {e}. Retrying... ({retries - attempt} retries left)")
            if attempt == retries:
                print("Failed to download file after multiple retries.")
                raise

URL = 'https://s3.unistra.fr/camma_public/datasets/cholec80/cholec80.zip'
outfile = 'data/cholec80.zip'

os.makedirs(os.path.dirname(outfile), exist_ok=True)

download_file(URL, outfile, retries=1)

