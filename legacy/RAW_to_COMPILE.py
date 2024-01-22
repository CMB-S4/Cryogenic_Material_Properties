import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import h5py
import sys

os.chdir(f"{sys.path[0]}\\FITS")
mat_directories = [x[0] for x in os.walk(os.getcwd())]
mat_directories = [os.path.split(path)[-1] for path in mat_directories]
mat_directories = mat_directories[1:]
print(f"Found {len(mat_directories)} material directories: {mat_directories}")

for mat in mat_directories:
    all_files = os.listdir(mat)
    extension = ".csv"
    raw_files = [file for file in all_files if file.endswith(extension)]
    print(f"For material {mat}, found {len(raw_files)} measurements.")

    # for raw_file in raw_files:
    #     # print(raw_file)
    #     file1 = np.loadtxt(f"{mat}/{raw_file}", dtype=str, delimiter=',')
    #     ref = file1[0,:]
    #     headers = file1[1,:]
    #     data_RAW = np.asarray(file1[2:,:], dtype=float)



    file_name = f"{mat}.lh5"

    with h5py.File(file_name, "w") as material_file:
        counter = 0
        for raw_file in raw_files:
            # print(raw_file)
            file1 = np.loadtxt(f"{mat}/{raw_file}", dtype=str, delimiter=',')
            ref = file1[0,:]
            ref_encode = [s.encode('utf-8') for s in ref]
            headers = file1[1,:]
            data_RAW = np.asarray(file1[2:,:], dtype=float)
            group = material_file.create_group(f"ref{counter}")
            ref_set = material_file[f"ref{counter}"].create_dataset("ref_info", (3,), data=ref_encode)
            raw_set = material_file[f"ref{counter}"].create_dataset("raw_data", data=data_RAW)
            counter += 1
    print(f"Material lh5 file has been saved with filename {file_name}")

    with h5py.File(file_name, "r") as f:
        # print(f.keys())
        # print(f["ref0"].keys())
        # print(f["ref0/ref_info"])
        # print(f["ref0/raw_data"])
        data = np.array(f["ref0/raw_data"])
        # print(data)
        # .decode('latin-1')
