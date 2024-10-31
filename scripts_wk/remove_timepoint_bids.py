from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
def run(f, file):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, file), total=len(file)))
    return results
    
from nilearn import image
def time_remove(func_nii, remove_time):
    func_img = image.load_img(func_nii)
    func_img_remove = image.index_img(func_img, slice(int(remove_time), func_img.shape[3]) )
    return func_img_remove
