#!/home/ubuntu/miniconda2/bin/python
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
from PIL import Image
import shutil
import re
import xml.etree.ElementTree as ET
from boto3.session import Session
import boto3
import h5py
from keras.models import Model
from keras import optimizers
from keras.layers import Dense, Flatten
from keras.applications.inception_v3 import InceptionV3
from keras.layers import Input 
from keras import backend as K

##Path to Data
basepath = "/home/ubuntu/"
genome_regions = "hs37d5_15K_Windows.bed"
L1HS_bam = "-L1HS_mapped.bam"
L1HS_bam_bai = "-L1HS_mapped.bam.bai"
L1HS = "/home/ubuntu/longboard/rmask_L1HS_Correct.bed"
bam = "-ready.bam"
bai = "-ready.bam.bai"
igv = "-igv.xml"
bed = ".bed"
coverage15k = ".coverage15k"
coverage15k_gt100 = ".coverage15kgt100"
loci = ".loci"
IGV = "/home/ubuntu/longboard/IGV_template.xml"
subject = "USH12"
Cells = ["USH12_A1_S177","USH12_A2_S185","USH12_A3_S193","USH12_A4_S200","USH12_A5_S207","USH12_A6_S214","USH12_A7_S284","USH12_A8_S292","USH12_B1_S178","USH12_B2_S186","USH12_B3_S194","USH12_B4_S201","USH12_B5_S208","USH12_B6_S215","USH12_B7_S285","USH12_C1_S179","USH12_C2_S187","USH12_C3_S195","USH12_C4_S202","USH12_C5_S209","USH12_C6_S216","USH12_C7_S286","USH12_C8_S293","USH12_D1_S180","USH12_D2_S188","USH12_D3_S196","USH12_D4_S203","USH12_D5_S210","USH12_D6_S217","USH12_D7_S287","USH12_D8_S294","USH12_E1_S181","USH12_E2_S189","USH12_E3_S197","USH12_E4_S204","USH12_E5_S211","USH12_E6_S218","USH12_E7_S288","USH12_E8_S295","USH12_F1_S182","USH12_F2_S190","USH12_F3_S198","USH12_F4_S205","USH12_F5_S212","USH12_F6_S219","USH12_F7_S289","USH12_F8_S296","USH12_G1_S183","USH12_G2_S191","USH12_G3_S199","USH12_G4_S206","USH12_G6_S220","USH12_G7_S290","USH12_G8_S297","USH12_H1_S184","USH12_H2_S192","USH12_H5_S213","USH12_H6_S221","USH12_H7_S291","USH12_H8_S298"]
#cell = sys.argv[2] #input
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'

input_tensor = Input(shape=(512, 512, 3))
base_model = InceptionV3(input_tensor=input_tensor, weights='imagenet', include_top=False)

x=base_model.output
x = Flatten(name='flatten')(x)
x = Dense(4096, activation='relu', name='fc1')(x)
preds = Dense(1024, activation='sigmoid', name='predictions')(x)

feat_extractor = Model(inputs=base_model.input,outputs=preds)

for cell in Cells:
    ##Load Data
    session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
    s3 = session.resource('s3')
    your_bucket = s3.Bucket('longboard-sc')
    for s3_file in your_bucket.objects.all():
        s3 = boto3.client ('s3')
        s3.download_file('longboard-sc',s3_file.key,s3_file.key)
    #Bam
    s3.download_file('bsmn-data',os.path.join(subject, cell + bam),os.path.join(basepath,cell + bam))

    p0 = Popen(['samtools', 'index', os.path.join(basepath, cell + bam)])
    p0.wait()

    myoutput = open(os.path.join(basepath, cell + L1HS_bam), 'w')
    p1 = Popen(['java', '-jar', '/home/ubuntu/jvarkit/dist/samviewwithmate.jar', '-b', L1HS, '--samoutputformat', 'BAM', os.path.join(basepath, cell + bam)], stdout=myoutput)
    p1.wait()
    myoutput.close()

    p2 = Popen(['samtools', 'index', os.path.join(basepath, cell + L1HS_bam)])
    p2.wait()

    myoutput2 = open(os.path.join(basepath, cell + coverage15k), 'w')
    p3 = Popen(['bedtools', 'multicov', '-bams', os.path.join(basepath, cell + L1HS_bam), '-bed', os.path.join(basepath,genome_regions)], stdout=myoutput2)
    p3.wait()
    myoutput2.close()

    myinput3 = open(os.path.join(basepath, cell + coverage15k), 'r')
    myoutput3 = open(os.path.join(basepath, cell + coverage15k_gt100), 'w')
    awk_cmd = "{ if ($4 > 100) { print } }"
    proc = Popen(['awk', awk_cmd], stdin=myinput3, stdout=myoutput3)
    proc.wait()
    myoutput3.flush()

    tree = ET.parse(IGV)
    root = tree.getroot()
    root[0][0].set('path', os.path.join(basepath, cell + bam)) #sc bam
    root[0][1].set('path', os.path.join(basepath, cell + L1HS_bam)) #L1HS bam
    root[1][0].set('id', os.path.join(basepath, cell + bam)) #sc bam
    root[2][0].set('id', os.path.join(basepath, cell + L1HS_bam)) #L1HS bam
    tree.write(os.path.join(basepath, cell + igv))

    myinput_loci = os.path.join(basepath, cell + coverage15k_gt100)
    myoutput_loci = os.path.join(basepath, cell + loci)
    with open(myoutput_loci, 'w') as outfile:
        with open(myinput_loci, 'r') as infile:
                data = infile.readlines()
                for region in data:
                        row = [str(region.strip().split('\t')[0]),":",str(region.strip().split('\t')[1]),"-",str(region.strip().split('\t')[2])]
                        outfile.write("".join(row)+'\n')
    Popen(['split', '-l', '100', '-d', os.path.join(basepath, cell + loci), os.path.join(basepath, cell + ".locisplit")]).wait()





    print cell
    cell_ids = []
    locifile = os.path.join(basepath, cell + loci)
    worklist = glob.glob("*.locisplit*")
    batchsize = 16
    print len(worklist)
    session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
    s3 = session.resource('s3')
    for i in xrange(0, len(worklist), batchsize):
        batch = worklist[i:i+batchsize]
        print i
        index = 1
        procs = []
        for file in batch:
            print file
            with open(os.path.join(basepath, file)) as f0:
                first = f0.readline()# Read the first line.
                for last in f0: pass
                firstpic = cell+"_"+"*"+first.strip().split(':')[0]+"_"+first.strip().split(':')[1].split('-')[0]+"_"+first.strip().split(':')[1].split('-')[1]+".png"
                lastpic = cell+"_"+"*"+last.strip().split(':')[0]+"_"+last.strip().split(':')[1].split('-')[0]+"_"+last.strip().split(':')[1].split('-')[1]+".png"
                if not (glob.glob(os.path.join(basepath, firstpic)) or glob.glob(os.path.join(basepath, lastpic))):
                    p = Popen(['igv_plotter', '-o', cell+"_", '-L', file, '-v', '--max-panel-height', '1000', '--igv-jar-path', '/home/ubuntu/IGV_2.4.10/igv.jar', '-m', '6G', '-g', 'hg19', os.path.join(basepath, cell + igv)])
                    procs.append(p)
        for pp in procs:
            pp.wait()
        for file in glob.glob("*s*__*.png"):
            newfile = re.sub("_s\d+__", "-", file)
            shutil.move(file, newfile)
        for file in glob.glob("*.png"):
            if "mod" not in file:
                path = os.path.splitext(file)[0]
                basename = os.path.basename(path)
                outfile1 = basename + "_mod.png"
                if not os.path.isfile(os.path.join(basepath,outfile1)):
                    img = Image.open(file)
                    pixelMap = img.load()
                    img2 = Image.new(img.mode, img.size)
                    pixelsNew = img2.load()
                    for i in range(img2.size[0]):
                        for j in range(img2.size[1]):
                            if 250 in pixelMap[i,j]:
                                pixelMap[i,j] = (0,0,0,0)
                            else:
                                pixelsNew[i,j] = pixelMap[i,j]
                    img2.crop((174,130,img.size[0]-22,img.size[1])).resize((512,512)).save(outfile1)
        filelist = glob.glob("*_mod.png")
        x = np.array([np.array(Image.open(fname)) for fname in filelist])
        x = x / 255
        y = np.array([np.array(fname).astype(str) for fname in filelist])
        uid = uuid.uuid4()
        cell_ids.append(uid.hex)
        print(uid.hex)
        z = feat_extractor.predict(x, batch_size = 16)
        hf = h5py.File(cell+'_'+uid.hex+'.h5', 'w')
        hf.create_dataset('X', data=x)
        hf.create_dataset('Y', data=y)
        hf.create_dataset('Z', data=z)
        hf.close()
        s3.meta.client.upload_file(os.path.join(basepath,cell+'_'+uid.hex+'.h5'),'bsmn-data',os.path.join(subject, cell+'_'+uid.hex+'.h5'))
        for file in glob.glob("*.png"):
            os.remove(file)    
        os.remove(os.path.join(basepath,cell+'_'+uid.hex+'.h5'))
    hf = h5py.File(cell+'_IDs.h5', 'w')
    hf.create_dataset('ID', data=cell_ids)
    hf.close()
    s3.meta.client.upload_file(os.path.join(basepath,cell+'_IDs.h5'),'bsmn-data',os.path.join(subject, cell+'_IDs.h5'))
    print "Done with Sample: "+cell
    for file in glob.glob(subject+"*"):
        os.remove(file)    
call(['sudo', 'shutdown', '-h', 'now'])
