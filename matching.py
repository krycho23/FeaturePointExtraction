# Author: krycho23

# this file i used to create error map and error map histogram
# it reads disparity maps with use of regex for different windows
# then it creates error map and error map histogram
# it also calcualte bad2.0, bad0.5, bad4.0, mae, rmse matching factors by comparing disp map
# with ground truth from pfm file
# everything can be calculated for all points - dense method or for only feature points - sparse method
# images are loaded from https://vision.middlebury.edu/stereo/data/scenes2014/

import cv2
import numpy as np
import json
import math
import os
from os import listdir
from os.path import isfile, join
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import re
import csv
from PIL import Image
import matplotlib as mpl
from matplotlib.colors import ListedColormap
from matplotlib import pylab as pl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata
from scipy.interpolate import RectBivariateSpline
from scipy.interpolate import interp2d


json_path = "paths.json"

def readJson():
    with open(json_path) as json_conf:
        conf = json.load(json_conf)
    return conf


def addNoise(image, gmean, gvar):
    row, col, ch = image.shape
    mean = gmean
    var = gvar
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noisy = image + gauss
    return noisy


def read_calib(calib_file_path):
    with open(calib_file_path, 'r') as calib_file:
        calib = {}
        csv_reader = csv.reader(calib_file, delimiter='=')
        for attr, value in csv_reader:
            calib.setdefault(attr, value)

    return calib


def read_pfm(pfm_file_path):
    with open(pfm_file_path, 'rb') as pfm_file:
        header = pfm_file.readline().decode().rstrip()
        channels = 3 if header == 'PF' else 1

        dim_match = re.match(r'^(\d+)\s(\d+)\s$', pfm_file.readline().decode('utf-8'))
        if dim_match:
            width, height = map(int, dim_match.groups())
        else:
            raise Exception("Malformed PFM header.")

        scale = float(pfm_file.readline().decode().rstrip())
        if scale < 0:
            endian = '<'  # littel endian
            scale = -scale
        else:
            endian = '>'  # big endian

        dispariy = np.fromfile(pfm_file, endian + 'f')
    #

    img = np.reshape(dispariy, newshape=(height, width))
    
    img = np.flipud(img).astype('uint16')
    return img

def create_depth_map(pfm_file_path, calib=None):
    dispariy, [shape, scale] = read_pfm(pfm_file_path)

    if calib is None:
        raise Exception("Loss calibration information.")
    else:
        fx = float(calib['cam0'].split(' ')[0].lstrip('['))
        base_line = float(calib['baseline'])
        doffs = float(calib['doffs'])

        # scale factor is used here
        depth_map = fx * base_line / (dispariy / scale + doffs)
        depth_map = np.reshape(depth_map, newshape=shape)
        depth_map = np.flipud(depth_map).astype('uint8')

        return depth_map


class MyMatching:

    def __init__(self, folder_name, kernel_size, filename):

        self.scale = 1

        self.kernel_size = kernel_size
        self.folder_name = folder_name + "/"
        self.filename = filename
        self.conf = readJson()
        left_img = self.conf["base_path"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            1] + self.folder_name + self.conf["left_image"]
        right_img = self.conf["base_path"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            1] + self.folder_name + self.conf["right_image"]
        self.disp_name = self.conf["base_path"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            2] + self.folder_name + self.conf["ground_truth"]
        self.calib_name = self.conf["base_path"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            1] + self.folder_name + self.conf["calib"]
       
        # Load source image
        self.img1 = cv2.imread(left_img, 0)  # Load an image

        # # Check if image is loaded fine
        if self.img1 is None:
            print('Error opening image1')
            exit(-1)


        self.img2 = cv2.imread(right_img,0)  # Load an image

        # Check if image is loaded fine
        if self.img2 is None:
            print('Error opening image2')
            exit(-1)

        self.left_corners = self.calculateCorners(self.img1)

        self.total_rows = len(self.img1)
        self.total_cols = len(self.img1[0])

        self.disparity = np.multiply(np.ones((self.total_rows, self.total_cols), np.uint8), -1)
        self.error_map = np.zeros((self.total_rows, self.total_cols), np.uint8)

        self.ground_truth = read_pfm(self.disp_name)
        
        self.disparity = self.readdm_16png(self.filename)

        matchObj = re.match(r'(.*)disp_map.*', self.filename)
        
        self.filename = matchObj.group(1)

        self.log_file = open(self.conf["base_path2"] + self.conf["disp"], "a+")
        self.error = open(self.conf["base_path2"] + self.conf["relative_error"], "a+")
        self.ground = open(self.conf["base_path2"] + self.conf["ground"], "a+")
        
        self.match_factor05 = open(self.conf["base_path2"] + "my_matching_bad_05_" + self.folder_name[:-1] + "_" + str(self.scale) + ".txt", "a+")
        self.match_factor20 = open(self.conf["base_path2"] + "my_matching_bad_20_"  + self.folder_name[:-1] + "_" + str(self.scale) + ".txt", "a+")
        self.match_factor40 = open(self.conf["base_path2"] + "my_matching_bad_40_"  + self.folder_name[:-1] + "_"  + str(self.scale) + ".txt", "a+")
        self.mae_factor = open(self.conf["base_path2"] + "my_matching_mae_"  + self.folder_name[:-1] + "_" + str(self.scale) + ".txt", "a+")
        self.rmse_factor = open(self.conf["base_path2"] + "my_matching_rmse_"  + self.folder_name[:-1] + "_" + str(self.scale) + ".txt", "a+")

        self.error.write(
            self.folder_name + self.conf["scale"][str(self.scale)] + "_" + self.conf["method"][2] + self.conf["measure"][
                0] + str(self.kernel_size) + "\n")

        self.ground.write(
            self.folder_name + self.conf["scale"][str(self.scale)] + "_" + self.conf["method"][2] + self.conf["measure"][
                0] + str(self.kernel_size) + "\n")

        self.log_file.write(
            self.folder_name + self.conf["scale"][str(self.scale)] + "_" + self.conf["method"][2] + self.conf["measure"][
                0] + str(self.kernel_size) +  "\n")


    def readdm_png(self, filename):
      filename = self.conf["base_path3"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            1] + self.folder_name + filename
      print(filename)
      dm = cv2.imread(filename,-1)
      if dm is None:
            print('Error opening disparity map')
            exit(-1) 
      return dm

    def readdm_16png(self, filename):
      filename = self.conf["base_path3"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][
            1] + self.folder_name + filename[:-3] + "yml"
      fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)
      fn = fs.getNode("dispMap")
      dm = fn.mat()
      return dm

    def calculateCorners(self, src):

        blockSize = self.kernel_size
        ksize = 3
        k = 0.04

        dst = cv2.cornerHarris(src, blockSize, ksize, k)
        ret, final = cv2.threshold(dst, 0.01 * dst.max(), 255, 0)

        corner_value = 0
        corners = []

        for i in range(len(final)):
            for j in range(len(final[0])):
                if corner_value == final[i, j]:
                    corners.append([j, i])

        return corners

    def calculateMatchFactorSparse(self, sparse_list, delta):
        # calculate bad pixels that exceeds 2 pixels/scale
        sparse_counter = 0
        for error in sparse_list:
            if error > delta and math.isnan(error) == False:
                sparse_counter += 1

        sparse_factor = sparse_counter / len(sparse_list)
        # calculate factor, return sparse and dense error
        return sparse_factor

    def calculateMatchFactorDense(self, dense_list, delta):
      all_pixels = self.total_rows * self.total_cols
      counter = 0
      for error in dense_list:
            if error > delta and math.isnan(error) == False:
                counter += 1

      assert len(dense_list) == all_pixels

      dense_factor = counter / all_pixels
      return dense_factor

    def calculateMAESparse(self, sparse_list):
      sum = 0
      for error in sparse_list:
        sum += error
      mae_sparse = sum / len(sparse_list)
      return mae_sparse
        
    def calculateMAEDense(self, dense_list):
      sum = 0
      for error in dense_list:
        sum += error
      mae_dense = sum / len(dense_list)
      return mae_dense

    def calculateRMSESparse(self, sparse_list):
      sum = 0
      for error in sparse_list:
        sum += error**2
      rmse_sparse = math.sqrt(sum / len(sparse_list))
      return rmse_sparse
    
    def calculateRMSEDense(self, dense_list):
      sum = 0
      for error in dense_list:
        sum += error**2
      rmse_dense = math.sqrt(sum / len(dense_list))
      return rmse_dense

    def computeGroundtruth(self):
      self.ground_truth = read_pfm(self.disp_name)
      return self.ground_truth

    # compare calculated values with ground-truth values
    def compareGroundtruthSparse(self):
        error_list = []

        for left_corner in self.left_corners:

            y = left_corner[1]
            x = left_corner[0]

            if self.disparity[y, x] == -1:
              continue

            self.ground.write(str(self.ground_truth[y, x]) + "\n")

            # absolute difference of exact value and calculated divided by exact value
            error = abs(int(self.disparity[y, x]) - int(self.ground_truth[y, x]))
            self.error.write(str(error) + "\n")

            error_list.append(error)
            self.error_map[y, x] = error

        print(self.filename + " SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 2 / self.scale)) + "\n")
        self.match_factor20.write( self.folder_name +self.filename)
        self.match_factor20.write("SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 2 / self.scale)) + "\n")

        print(self.filename + " SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 0.5 / self.scale)) + "\n")
        self.match_factor05.write( self.folder_name +self.filename)
        self.match_factor05.write("SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 0.5 / self.scale)) + "\n")

        print(self.filename + " SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 4 / self.scale)) + "\n")
        self.match_factor40.write( self.folder_name +self.filename)
        self.match_factor40.write("SparseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 4 / self.scale)) + "\n")

        print(self.filename + " SparseMatchFactor= " + str(self.calculateMAESparse(error_list)) + "\n")
        self.mae_factor.write( self.folder_name + self.filename)
        self.mae_factor.write(" SparseMatchFactor= " + str(self.calculateMAESparse(error_list)) + "\n")

        print(self.filename + " SparseMatchFactor= " + str(self.calculateRMSESparse(error_list)) + "\n")
        self.rmse_factor.write(self.folder_name + self.filename)
        self.rmse_factor.write(" SparseMatchFactor= " + str(self.calculateRMSESparse(error_list)) + "\n")
        

    def compareGroundtruthDense(self):

      error_list = []

      for row in range(self.total_rows):
        for col in range(self.total_cols):
            
            if self.disparity[row,col] == -1:
              continue

            self.ground.write(str(self.ground_truth[row,col]) + "\n")

            # absolute difference of exact value and calculated divided by exact value
            error = abs(int(self.disparity[row,col]) - int(self.ground_truth[row,col]))
            self.error.write(str(error) + "\n")
            error_list.append(error)
            self.error_map[row ,col] = error
            
      
      print(self.filename + " DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 2 / self.scale)) + "\n")
      self.match_factor20.write( self.folder_name +self.filename)
      self.match_factor20.write("DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 2 / self.scale)) + "\n")

      print(self.filename + " DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 0.5 / self.scale)) + "\n")
      self.match_factor05.write( self.folder_name +self.filename)
      self.match_factor05.write("DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 0.5 / self.scale)) + "\n")

      print(self.filename + " DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 4 / self.scale)) + "\n")
      self.match_factor40.write( self.folder_name +self.filename)
      self.match_factor40.write("DenseMatchFactor= " + str(self.calculateMatchFactorSparse(error_list, 4 / self.scale)) + "\n")

      print(self.filename + " DenseMatchFactor= " + str(self.calculateMAESparse(error_list)) + "\n")
      self.mae_factor.write(self.folder_name +self.filename)
      self.mae_factor.write(" DenseeMatchFactor= " + str(self.calculateMAESparse(error_list)) + "\n")

      print(self.filename + " DenseMatchFactor= " + str(self.calculateRMSESparse(error_list)) + "\n")
      self.rmse_factor.write(self.folder_name +self.filename)
      self.rmse_factor.write(self.filename + " DenseMatchFactor= " + str(self.calculateRMSESparse(error_list)) + "\n")
     
      
    def doMatching(self):

        max_disp = np.max(self.ground_truth)
        min_disp = np.min(self.ground_truth)
        print(max_disp)
        print(min_disp)

        print(self.disparity.shape)
        print(self.ground_truth.shape)
        assert(len(self.disparity) == len(self.ground_truth))
        assert(len(self.disparity[0]) == len(self.ground_truth[0]))

        self.compareGroundtruthDense()
        self.compareGroundtruthSparse()

        # error-map
        threshold =  2 / self.scale
        rows, cols = self.error_map.shape
        # error_map_color = np.zeros((self.total_rows, self.total_cols, 3), np.uint8)
        error_map_q = np.zeros((self.total_rows, self.total_cols), np.uint8)

        # counters of values
        reds=0
        yellows=0
        greens=0

        significant = 5
        # error-map histogram

        for row in range(self.total_rows):
          for col in range(self.total_cols):

            if self.error_map[row, col] > significant * threshold:
                error_map_q[row, col] = 3 #red
                reds += 1
            elif self.error_map[row, col] > threshold:
                error_map_q[row, col] = 2 #yellow
                yellows += 1
            else:
                error_map_q[row, col] = 1 #green
                greens += 1
       
        np.save(self.conf["base_path2"] + "ErrorMapData/" + self.filename + "_errormap_" + self.folder_name[:-1], self.error_map)
        
        customCmap = mpl.colors.ListedColormap([ 'green', 'yellow', 'red'])

        data = error_map_q

        fig, ax = plt.subplots(figsize=(20, 10))
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)

        im = ax.imshow(data, cmap=customCmap)

        fig.colorbar(im, cax=cax, orientation='vertical')

        # error map
        plt.savefig(
            self.conf["base_path3"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][1] + self.folder_name +
            self.filename + self.conf["image_type"][1])
            
        print("Error map done")

        #error map histogram
        all_features = reds + yellows + greens
        

        labels_feature = ["red", "yellow", "green"]
        values_feature = np.array([reds, yellows, greens]) * 100 / all_features
        
        plt.figure(figsize=(20, 10))
        plt.bar(labels_feature, values_feature), plt.title("Error map histogram ")
        plt.savefig(
            self.conf["base_path3"] + self.conf["scale"][str(self.scale)] + self.conf["dataset"][1] + self.folder_name +
            self.filename + self.conf["image_type"][3] )        

        labels = np.arange(max_disp*16)
        
        print("Error map histogram done")
        


if __name__ == '__main__':

    folder_names = ["Vintage"]                     
                                
    for folder_name in folder_names:
      path_to_folder = "OutputImages/FullSize/training/" + folder_name
      filenames = [f for f in listdir(path_to_folder) if isfile(join(path_to_folder, f)) and re.match("sncc.*disp_map.png", f) != None]

      for filename in filenames:
        print(filename)
        matching = MyMatching(folder_name,5, filename)
        matching.doMatching()