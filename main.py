#! /usr/bin/env python
import urllib2
import re
import json
import argparse
import StringIO
import gzip
import tarfile
import sys
from os import listdir, mkdir
import os
from os.path import isfile, join
import cv2
from xml.dom.minidom import parse
import xml.dom.minidom
import shutil


from xml.etree import ElementTree as ET


class Synset:

    def __init__(self):

        id = ""
        name = ""
        # This is without the .xml
        annotationfilenames = []

        # This is with .xml
        annotationfullfilenames = []

        annotation_path = ""

        annotation_urls = []




def download_bbox_file(synsetid):

    baseURL = "http://image-net.org/downloads/bbox/bbox/"

    outFilePath = synsetid+".tar.gz"

    #print baseURL+synsetid

    response = urllib2.urlopen(baseURL + synsetid+".tar.gz")

    f = open(outFilePath, 'wb')
    meta = response.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (outFilePath, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = response.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        #print status,

    f.close()


    tar = tarfile.open(outFilePath, "r:gz")
    tar.extractall()
    os.remove(outFilePath)



def get_annotation_image_urls(filenames,synsetid):

    urls = dict()

    baseURL = "http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid="

    response = urllib2.urlopen(baseURL + synsetid)

    data = response.read()

    rows = data.split("\n")


    #print rows

    for row in rows:
        # remove /r at the end
        arow = row[:-1]
        keyvalue = arow.split(" ")
        matching = [s for s in filenames if keyvalue[0]  == s]
        #print matching
        if len(matching) == 1:
            #print keyvalue[0]
            urls[matching[0]] = keyvalue[1]

    return urls

def download_images(urls,synsetid,filenames,fullfilenames):

    basePath = "Images/"
    fullPath = basePath+"/"+synsetid+"/"

    if not os.path.exists(fullPath):
        os.makedirs(fullPath)


    remainingfilenames = []
    remainingurls = []
    remainingfullfilenames = []

    for key in urls.keys():

        imagePath = fullPath+str(key)+".jpg"
        #print key
        #print urls[key]
        try:
            response = urllib2.urlopen(urls[key])
            data = response.read()
        except Exception as ex:
            print ex
            data = []


        # This means that the image does not exist in flickr so we should remove the xml and also delete the array elements
        if(len(data) == 0 or  data[:8] == '\x89PNG\x0d\x0a\x1a\x0a'):
            basePath = "Annotation/"
            path = basePath+synsetid+"/"
            path +=str(key)+".xml"
            print "Deleting bbox ",path
            os.remove(path)
            #del fullfilenames[i]
            #del filenames[i]
        else:

            remainingurls.append(urls[key])
            remainingfilenames.append(str(key))
            ff = str(key)+".xml"
            remainingfullfilenames.append(ff)

            f = open(imagePath, 'wb')

            f.write(data)

            f.close()


    return remainingurls,remainingfilenames,remainingfullfilenames


def check_xmls(fullfilenames,synsetid):

    for fullfilename in fullfilenames:
        basePath = "Annotation/"
        path = basePath+synsetid+"/"
        path += fullfilename

        baseImagePath= "Images/"+synsetid
        impath = baseImagePath+"/"
        impath += fullfilename[:-3]
        impath += "jpg"

        try:
            img = cv2.imread(impath)
        except Exception as ex:
            print ex
            continue
        '''
        if img.shape[0] == 0:
            print "Image %s cannot be read "%impath
            return
        '''
        destPath = "Annotations/"+synsetid
        destpath = destPath+"/"
        destpath += fullfilename

        if not os.path.exists(destPath):
            os.makedirs(destPath)

        tree = ET.parse(path)
        rootElement = tree.getroot()

        for subelement in rootElement:

            width = img.shape[1]
            height = img.shape[0]

            #print "Tag: ",subelement.tag
            #print "Text: ",subelement.text
            #print "Attribute:",subelement.attrib,"\n"
            #print "Items:",subelement.items(),"\n"

            if subelement.tag == 'size':
                for item in subelement:
                    if item.tag == 'width':
                        item.text = str(width)
                    elif item.tag=='height':
                        item.text = str(height)


            if subelement.tag == 'object':
                for item in subelement:
                    #print item.tag
                    if item.tag == 'bndbox':
                        #print item.attrib
                        for bbox_item in item:
                            if bbox_item.text == '0':
                                bbox_item.text = '1'
                            elif int(bbox_item.text) == width:
                                pos = width-1
                                bbox_item.text = str(pos)
                            elif int(bbox_item.text) == height:
                                pos = height-1
                                bbox_item.text = str(pos)

            tree.write(destpath)



def change_synsetsids_to_names_in_xmls(fullfilenames,synsetid,synsetname):

    for fullfilename in fullfilenames:
        basePath = "Annotation/"
        path = basePath+synsetid+"/"
        path += fullfilename

        destPath = "Annotations/"
        destpath = destPath+"/"
        destpath += fullfilename

        if not os.path.exists(destPath):
            os.makedirs(destPath)

        tree = ET.parse(path)
        rootElement = tree.getroot()

        for subelement in rootElement:

            width = 0
            height = 0

            #print "Tag: ",subelement.tag
            #print "Text: ",subelement.text
            #print "Attribute:",subelement.attrib,"\n"
            #print "Items:",subelement.items(),"\n"

            if subelement.tag == 'size':
                for item in subelement:
                    if item.tag == 'width':
                        width = int(item.text)
                    elif item.tag=='height':
                        height = int(item.text)


            if subelement.tag == 'object':
                for item in subelement:
                    #print item.tag
                    if item.tag == 'bndbox':
                        #print item.attrib
                        for bbox_item in item:
                            if bbox_item.text == '0':
                                bbox_item.text = '1'
                            elif int(bbox_item.text) == width:
                                pos = width-1
                                bbox_item.text = str(pos)
                            elif int(bbox_item.text) == height:
                                pos = height-1
                                bbox_item.text = str(pos)

            tree.write(destpath)


def get_filenames_from_xmls(synsetid):

    filenames = []
    fullfilenames = []

    basePath = "Annotation/"
    path = basePath+synsetid+"/"

    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    #print onlyfiles

    for afile in onlyfiles:
        filename = afile.split(".")[0]
        filenames.append(filename)


    return filenames, onlyfiles


def get_imagenet_synsets_with_bbox():

    # the dictionary will have the synset as the key code and the name as the value
    returnlist = dict()

    # the link for the synsets with bbox
    link = "http://image-net.org/api/text/imagenet.bbox.obtain_synset_wordlist"


    # get the data
    req = urllib2.Request(link)
    response = urllib2.urlopen(req)

    data = response.read()

    # extract the rows. Each row has the format <a href="../../api/download/imagenet.bbox.synset?wnid=n02119789">kit fox, Vulpes macrotis</a><br/>
    rows = data.split("\n")
    # extract the synset id and word
    for row in rows:
        wnidpos = row.find("wnid=")

        if(wnidpos > 0):

            endpos = row.find("\">",wnidpos)

            key = row[wnidpos+5:endpos]

            endpos2 = row.find("</",endpos)

            value = row[endpos+2:endpos2]

            #print key," ",value

            returnlist[key] = value

    return returnlist;

def write_synset_list(list):
    homedir = os.getenv("HOME")
    filepath = homedir+"/imagenet_synset_list.txt";

    try:
        text_file = open(filepath, "w")
    except Exception as ex:
        print "File could not be opened for writing... ",ex
        return


    for key,value in list.iteritems():
        line = "{} {} \n".format(str(key),str(value))
        text_file.write(line)

    text_file.close()

    print "Output saved to ",filepath



if __name__ == '__main__':
    #"n04314914"
    argparser = argparse.ArgumentParser(description="This script downloads bbox annotations from imagenet for a given synset id")
    argparser.add_argument('--synset_id', help='The imagenet synset id for downloading the bbox annotations',default="")
    argparser.add_argument('--get_synset_list',type=bool,default = False, help="Parameter for downloading the imagenet synset list with bbox annotations")

    args = argparser.parse_args()

    if(args.get_synset_list):
        print "Getting the synset list..."
        annotationdict = get_imagenet_synsets_with_bbox()
        write_synset_list(annotationdict)

    synset_id = args.synset_id

    if(synset_id == ""):
        print "No synset id is given. Quitting..."
        sys.exit(0)

    download_bbox_file(synset_id)

    filenames, fullfilenames = get_filenames_from_xmls(synset_id)

    urls = get_annotation_image_urls(filenames,synset_id)

    assert len(urls) == len(filenames) , "Length of urls does not match to the length of filenames"

    urls, filenames, fullfilenames = download_images(urls,synset_id,filenames,fullfilenames)

    check_xmls(fullfilenames,synset_id)

    shutil.rmtree("./Annotation")
