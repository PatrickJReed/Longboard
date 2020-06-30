#!/home/ubuntu/miniconda2/bin/python

from __future__ import print_function
import glob, os, gc, sys
import os.path
import csv
import numpy as np
np.random.seed(1337)  # for reproducibility
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
from IPython.display import display
from PIL import Image
from IPython.display import Image as IPImage
import shutil
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import uuid
import pickle
from boto3.session import Session
import boto3
import h5py

##Path to Data
chunk = sys.argv[1]
basepath = "/home/ubuntu/"

hf = h5py.File(os.path.join(basepath,'Training_UMAP_HDB_Final.h5'),'r')
#Train_Z = hf['Z'][()] 
#Train_C = hf['C'][()]
Train_Y = hf['Y'][()]
#embedding_partialsupervised_1 = hf['embedding_partialsupervised_1'][()]
#embedding_partialsupervised_2 = hf['embedding_partialsupervised_2'][()]
#HDB_1 = hf['HDB_1'][()]
#HDB_2 = hf['HDB_2'][()]
set1 = hf['set1'][()]
set2 = hf['set2'][()]
New_1 = hf['New_1'][()]
New_2 = hf['New_2'][()]

##Path to Data
Training = ["USD15","usd19","USD3","USD30","USD36","USD37","USH15","USH19","USH3","USH30","USH36","USH37"]

Classes1 = len(set(New_1))

#pull all cells per sample from Train_Y
L1 = len(New_1)
T1={}

l = np.array_split(np.array(range(L1)),20)
for i in l[int(chunk)]:
    position_key = Train_Y[set1][i]
    Y_Class1 = str(New_1[i])
    T1[position_key] = Y_Class1
    
hf = h5py.File('Dict_'+chunk+'.h5', 'w')
hf.create_dataset('T1', data=T1)
hf.close()    