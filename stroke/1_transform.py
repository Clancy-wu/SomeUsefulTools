import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# 1 rename
def dir_rename(dir, new_name):
    # dir is the basename
    old_dir = os.path.join(work_dir, dir)
    new_dir = os.path.join(target_dir, new_name)
    os.mkdir(new_dir)
    transfer_command = f'/home/clancy/MRIcroGL/Resources/dcm2niix -f "%t_%c_%d_%n" -p y -z y -ba n -o {new_dir} {old_dir}'
    os.system(transfer_command)
    return dir,new_name

def dir_rename_run(args):
    return dir_rename(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':

    curren_dir = os.getcwd()
    work_dir = os.path.join(curren_dir, 'DICOM')
    target_dir = os.path.join(curren_dir, 'org_data')
    old_dir = os.listdir(work_dir)
    # three type
    # "%02d"%i
    # "{0:0=2d}".format(i)
    # f"{i:02}"
    new_name = ['sub-'+"{0:0=2d}".format(i+1) for i in range(len(old_dir))]
    import itertools
    # itertools.produce
    # itertools.zip_longest
    this_iter = list(zip(old_dir, new_name))
    final_results = run(dir_rename_run, this_iter)

    with open('name_transform.txt', 'w') as rf:
        content_head = 'old_name new_name\n'
        rf.write(content_head)
        for result in final_results:
            dir, new_name = result
            conten_write = str(dir) + ' ' + str(new_name) + '\n'
            rf.write(conten_write)
        rf.close()
## end. @author: kangwu.
