#!/bin/python39
## prepare your download_url.txt.
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import requests

def get_data_from_url(url):
    response = requests.get(url)
    if 'content-disposition' in response.headers:
        content_disposition = response.headers['content-disposition']
        filename = content_disposition.split('filename=')[1]
    else:
        filename = url.split('/')[-1]
    with open(filename, mode='wb') as file:
        file.write(response.content)
    print(f'Downloaded file {filename}')

def run(f, this_iter, n_threads):
    with ProcessPoolExecutor(max_workers=n_threads) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    url_file = 'download_url.txt'
    url_all = pd.read_csv(url_file, header=None)[0].values
    this_iters = list(url_all)
    n_threads = 10
    run(get_data_from_url, this_iters, n_threads)
## end. author@kangwu
