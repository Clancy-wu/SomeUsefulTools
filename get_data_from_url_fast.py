#!/bin/python39
import pandas as pd
import requests
import time
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def get_data_from_url(url):
    response = requests.get(url)
    try:
        content_disposition = response.headers['content-disposition']
        filename = content_disposition.split('filename=')[1]
        print(f'Downloaded file {filename}')
        with open(filename, mode='wb') as file:
            file.write(response.content)
    except:
        time.sleep(180)
        get_data_from_url(url)
    
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    url_file = 'article_url.txt'
    url_all = pd.read_csv(url_file, header=None)[0].values # 4748
    url_all_t1 = [x for x in url_all if 'T1w.nii.gz' in x] # 216
    url_all_bold = [x for x in url_all if 'rest_bold.nii.gz' in x] # 215

    #iter_t1 = list(url_all_t1)
    #run(get_data_from_url, iter_t1)
    # finished

    #iter_bold = list(url_all_bold)
    #run(get_data_from_url, iter_bold)
    # finished

    url_all_t1_json = [x for x in url_all if 'T1w.json' in x] # 216
    url_all_bold_json = [x for x in url_all if 'rest_bold.json' in x] # 216

    run(get_data_from_url, list(url_all_t1_json))
    run(get_data_from_url, list(url_all_bold_json))

    # dwi
    url_all_dwi = [x for x in url_all if 'dwi.nii.gz' in x] # 216
    url_all_dwi_json = [x for x in url_all if 'dwi.json' in x] # 216
    url_all_dwi_bvec = [x for x in url_all if 'dwi.bvec' in x] # 216
    url_all_dwi_bval = [x for x in url_all if 'dwi.bval' in x] # 216

    run(get_data_from_url, list(url_all_dwi))
    run(get_data_from_url, list(url_all_dwi_json))
    run(get_data_from_url, list(url_all_dwi_bvec))
    run(get_data_from_url, list(url_all_dwi_bval))




## end. author@kangwu
