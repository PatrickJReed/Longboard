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
subject = "USD11" #sys.argv[1]  #subjectid
Cells = ["USD11A1_S105","USD11A2_S169","USD11A3_S97","USD11A4_S161","USD11A5_S113","USD11A6_S121","USD11B1_S106","USD11B2_S170","USD11B3_S98","USD11B4_S162","USD11B5_S114","USD11B6_S122","USD11C1_S107","USD11C2_S171","USD11C3_S99","USD11C4_S163","USD11C5_S115","USD11C6_S123","USD11D1_S108","USD11D2_S172","USD11D3_S100","USD11D4_S164","USD11D5_S116","USD11D6_S124","USD11E1_S109","USD11E2_S173","USD11E3_S101","USD11E4_S165","USD11E5_S117","USD11E6_S125","USD11F1_S110","USD11F2_S174","USD11F3_S102","USD11F4_S166","USD11F5_S118","USD11F6_S126","USD11G1_S111","USD11G2_S175","USD11G3_S103","USD11G4_S167","USD11G5_S119","USD11G6_S127","USD11H1_S112","USD11H2_S176","USD11H3_S104","USD11H4_S168","USD11H5_S120","USD11H6_S128"]
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


#    input_tensor = Input(shape=(512, 512, 3))
#    base_model = InceptionV3(input_tensor=input_tensor, weights='imagenet', include_top=False)

#    x=base_model.output
#    x = Flatten(name='flatten')(x)
#    x = Dense(4096, activation='relu', name='fc1')(x)
#    preds = Dense(1024, activation='sigmoid', name='predictions')(x)

#    feat_extractor = Model(inputs=base_model.input,outputs=preds)


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
