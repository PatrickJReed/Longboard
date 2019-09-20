#!/usr/local/share/bcbio/anaconda/bin/python

from __future__ import division
import sys
import glob, os, gc
import uuid
import os.path
import csv
import numpy as np
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
import shutil
import re
import pickle
from boto3.session import Session
import boto3
import h5py
import umap
import hdbscan


##Path to Data
basepath = "/raidixshare_log-g/longboard/"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'

Training = ["USD22","USD01","USD11","USD25","USD30","USD37","USH12","USD3","USH11","USD41"]
#Training = ["USD01", "USD11"]

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
count = 0
for subject in Training:
    print(subject)
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'_new.h5'),os.path.join(basepath,subject+'_new.h5'))
    hf = h5py.File(os.path.join(basepath,subject+'_new.h5'), 'r')
    if count == 0:
        Train_Y = hf['Y']
        Train_Z = hf['Z']
        count+=1
    else:
        Train_Y = np.append(Train_Y,hf['Y'], axis=0)
        Train_Z = np.append(Train_Z,hf['Z'], axis=0)

hf = h5py.File('Training_All_new.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.close()                

s3.meta.client.upload_file(os.path.join('Training_All_new.h5'),'bsmn-data',os.path.join('Training_All_new.h5'))

#call(['sudo', 'shutdown', '-h', 'now'])