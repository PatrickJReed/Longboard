d#!/home/ubuntu/miniconda2/bin/python

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
basepath = "/home/ubuntu/"
session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
Cells_USD22 = ["USD22_F7_S171","USD22_F8_S178","USD22_G1_S124","USD22_G2_S132","USD22_G3_S140","USD22_G4_S148","USD22_G5_S156","USD22_G6_S164","USD22_G7_S172","USD22_G8_S179","USD22_H1_S125","USD22_H2_S133","USD22_H3_S141","USD22_H4_S149","USD22_H5_S157","USD22_H6_S165"]
Cells_USD25 = ["USD25A1_S65","USD25A2_S73","USD25A3_S198","USD25A5_S81","USD25A6_S89","USD25B1_S66","USD25B2_S74","USD25B3_S199","USD25B5_S82","USD25B6_S90","USD25C1_S67","USD25C2_S75","USD25C3_S200","USD25C5_S83","USD25C6_S91","USD25C8_S217","USD25D1_S68","USD25D2_S76","USD25D3_S201","USD25D4_S209","USD25D5_S84","USD25D6_S92","USD25D7_S214","USD25D8_S218","USD25E1_S69","USD25E2_S77","USD25E3_S202","USD25E5_S85","USD25E6_S93","USD25E7_S215","USD25E8_S219","USD25F1_S70","USD25F2_S78","USD25F3_S203","USD25F5_S86","USD25F6_S94","USD25G1_S71","USD25G2_S79","USD25G3_S204","USD25G5_S87","USD25G6_S95","USD25H1_S72","USD25H2_S80","USD25H3_S205","USD25H5_S88","USD25H6_S96"]
Cells_USD3 = ["USD3_A1_S133","USD3_A2_S139","USD3_A3_S146","USD3_A4_S153","USD3_A5_S161","USD3_A6_S169","USD3_A7_S268","USD3_A8_S276","USD3_B1_S134","USD3_B2_S140","USD3_B3_S147","USD3_B4_S154","USD3_B5_S162","USD3_B6_S170","USD3_B7_S269","USD3_B8_S277","USD3_C1_S135","USD3_C2_S141","USD3_C4_S155","USD3_C6_S171","USD3_C7_S270","USD3_C8_S278","USD3_D1_S136","USD3_D2_S142","USD3_D3_S149","USD3_D4_S156","USD3_D5_S164","USD3_D6_S172","USD3_D7_S271","USD3_D8_S279","USD3_E2_S143","USD3_E4_S157","USD3_E5_S165","USD3_E6_S173","USD3_E7_S272","USD3_E8_S280","USD3_F1_S137","USD3_F2_S144","USD3_F4_S158","USD3_F5_S166","USD3_F6_S174","USD3_F7_S273","USD3_F8_S281","USD3_G1_S138","USD3_G2_S145","USD3_G4_S159","USD3_G5_S167","USD3_G6_S175","USD3_G7_S274","USD3_G8_S282","USD3_H4_S160","USD3_H5_S168","USD3_H6_S176","USD3_H7_S275","USD3_H8_S283"]
Cells_USH11 = ["USH11_A1_S45","USH11_A2_S53","USH11_A3_S60","USH11_A4_S67","USH11_A5_S75","USH11_A6_S82","USH11_B1_S46","USH11_B2_S54","USH11_B3_S61","USH11_B4_S68","USH11_B5_S76","USH11_B6_S83","USH11_C1_S47","USH11_C2_S55","USH11_C3_S62","USH11_C4_S69","USH11_C5_S77","USH11_C6_S84","USH11_D1_S48","USH11_D2_S56","USH11_D3_S63","USH11_D4_S70","USH11_D5_S78","USH11_D6_S85","USH11_E1_S49","USH11_E2_S57","USH11_E4_S71","USH11_E5_S79","USH11_E6_S86","USH11_F1_S50","USH11_F4_S72","USH11_F6_S87","USH11_G1_S51","USH11_G2_S58","USH11_G3_S65","USH11_G4_S73","USH11_G5_S80","USH11_G6_S88","USH11_H1_S52","USH11_H2_S59","USH11_H4_S74","USH11_H5_S81"]
Data_Sets = []
Data_Sets.append(["USD22",Cells_USD22])
Data_Sets.append(["USD25",Cells_USD25])
Data_Sets.append(["USD3",Cells_USD3])
Data_Sets.append(["USH11",Cells_USH11])

img_width, img_height = 512,512
nb_epochs = 50
batch_size = 32

#download training_data_all
s3.meta.client.download_file('bsmn-data',os.path.join('Training_Keras_Final.h5'),os.path.join('Training_Keras_Final.h5'))

hf = h5py.File(os.path.join('Training_Keras_Final.h5'), 'r')
Y_All = hf['Y_All'][()]
Final_Labels = hf['Final_Labels'][()]
Classes = len(set(Final_Labels))

#pull all cells per sample from Train_Y
L = len(Final_Labels)
T={}

#cell_id = Train_Y[i].strip().split('-')[0]
for i in range(0, L):
    position_key = Y_All[i]
    Y_Class = Final_Labels[i].astype(str)
    T[position_key] = Y_Class
    
for dset in Data_Sets:
    subject = dset[0]
    print(subject)
    for cell in dset[1]:
        print(cell)
        cell_ids = []
        s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_IDs.h5'),os.path.join(basepath,cell+'_IDs.h5'))
        f = h5py.File(os.path.join(basepath,cell+'_IDs.h5'), 'r')
        os.remove(os.path.join(basepath,cell+'_IDs.h5'))
        cell_ids = f['ID']
        count = 0
        for cid in cell_ids:
            s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_'+cid+'.h5'),os.path.join(basepath,cell+'_'+cid+'.h5'))
            xyz = h5py.File(os.path.join(basepath,cell+'_'+cid+'.h5'), 'r')
            os.remove(os.path.join(basepath,cell+'_'+cid+'.h5'))
            if count == 0:
                X = xyz['X'][()]
                Y = xyz['Y'][()]
                count+=1
            else:
                X = np.append(X,xyz['X'][()], axis=0)
                Y = np.append(Y,xyz['Y'][()], axis=0)
        print(X.shape)
        Labels = [None] * len(Y)
        for i in range(0,len(Y)):
            if Y[i] in Y_All:
                Labels[i] = T[Y[i]]
            else:
                Labels[i] = "NotClassified"                    
        rm=[]
        for i in range(0,len(Labels)):               
            if Labels[i] == "NotClassified": 
                rm=np.append(rm,i)
        X = np.delete(X,rm,0)
        Labels = np.delete(Labels,rm,0)
        Y = np.delete(Y,rm,0)
        for l in Labels:
            if not os.path.exists(os.path.join(basepath,"Images",l)):
                os.makedirs(os.path.join(basepath,"Images",l),0755)           
        for i in range(0,len(Labels)):
            im = Image.fromarray(np.uint8(X[i,:,:,:]*255),mode='RGB')
            im.save(os.path.join(basepath,"Images",Labels[i],Y[i]))    
