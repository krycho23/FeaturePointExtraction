# Author: krycho23
# generate disparity maps for different windows

import subprocess

vmax = 300
vmin = 0
folders=["Pipes"]

methods = ["./sncc"]

filter_windows =  [11,21,31,51,101]
sum_windows=  [11,21,31,51,101]

for method in methods: 
    for folder in folders:
        for filter_window in filter_windows:
            for sum_window in sum_windows:
                subprocess.call([method,folder, str(vmax), str(vmin), str(filter_window), str(filter_window), str(sum_window), str(sum_window)]) 

   

