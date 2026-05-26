#!/usr/bin/env python3

import os
import sys
import argparse
import glob
import json
from datetime import datetime
import hashlib

import exiftool
from PIL import Image

def isfloat(n: str) -> bool:
     try:
         float(n)
         return True
     except ValueError:
         return False


def isinteger(n: str) -> bool:
     try:
         int(n)
         return True
     except ValueError:
         return False


def as_int_float_or_string(n: str):

    try:
        float(n)

        try:
            return int(n)
        except ValueError:
            return float(n)

    except:
         return n

# parse a value from text which is bracketed by start_token and stop_token
def parse_from_text( text, key, start_token, stop_token, result ):

    pos1= text.find(start_token)
    pos2= text.find(stop_token,pos1)
    print("    P ", pos1, pos2)
    if -1 != pos1 and -1 != pos2:
        val= text[pos1+len(start_token):pos2]
        print("    ", key, " --> ", val)
        result[key]= as_int_float_or_string( val.strip() )


def extract_from_jpg_file( dirname, prefix="JPG" ):

    data= {}
    data[prefix]= {}
    subset= data[prefix]

    # there should be exactly one PDF file in this dir
    list= glob.glob( os.path.join(dirname,'*.jpg'))

    # for l in list:
    #     print("   ", l)

    if 0 == len(list):
        print(f"No JPG index file in dir {dirname}, skip")
        return data

    if 1 < len(list):
        print(f"More than one JPG file in dir {dirname}, skip")
        return data

    # exaclty one PDF file found, good, let's use it
    try:
        with exiftool.ExifToolHelper() as et:
            for d in et.get_metadata(list[0]):
                for k, v in d.items():
                    # print(f"Dict: {k} = {v}")

                    if 'list' == type(v):
                        subset[k]= json.dumps(v)
                    else:
                        subset[k]= as_int_float_or_string(v)
    except:
        print("ERROR: most likely the 'exiftool' binary is missing. Make sure it can be found in $PATH. See https://exiftool.org/install.html, you can download binaries as a fallback.")
        sys.exit(-1)
    return data


# remove some keys according to manual decisions
def filter_keys( data ):

    remove= {
        "XMP:CreatorPostalCode",
        "XMP:SubjectCategory",
        "XMP:Description",
        "IPTC:Caption-Abstract",
    }

    for r in remove:
        data.pop(r,None)

    rename= { 
        "File:Comment": "EXIF:ImageDescription",
    }

    for r in rename:
        if r in data:
            data[ rename[r] ]= data[r]
            data.pop(r,None)

    return data

def extract_from_dir(d):

    ABORT= False

    data = {}

    # extract from JPG if avail
    ret= extract_from_jpg_file( d, prefix="EXIF" )
    data.update( ret )

    data["EXIF"]= filter_keys( data["EXIF"] )

    return data

### main

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='extract_metadata.py',
                    description='Extract metadata and training files from dataset subdirectories',
                    epilog='Tailored script for this datalad repository, ask a.knuepfer@hzdr.de')

    parser.add_argument('dirnames', help='Input directory names', nargs='+')
    parser.add_argument('-r', '--replace', action='store_true', help='Replace output file DATASET.json if it already exists')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    parser.add_argument('-n', '--no-convenience', action='store_true', help='Suppress additions for convenience')

    args = parser.parse_args()

    for d in args.dirnames:

        if os.path.isdir(d):
            print("processing %s" % d)
        else:
            print("%s not a dir, skip" % d)
            continue

        outputfilename= os.path.join(d,'DATASET.json')
        if os.path.isfile(outputfilename) and not args.replace:
            print(f"Output file for metadata {outputfilename} already present, skip")
            continue

        data= extract_from_dir(d)

        #print(json.dumps(data,indent=4))
        with open( os.path.join(d,"DATASET.json"), "w", encoding='utf8' ) as out:
            json.dump(data,out,indent=4, ensure_ascii=False)

        if not args.no_convenience:

            readme= f"# Preview of {data['EXIF']['XMP:ResourceID']}: \"{data['EXIF']['XMP:Title']}\"\n"
            readme+= f"[{data['EXIF']['XMP:ReferenceURL']}]({data['EXIF']['XMP:ReferenceURL']})\n\n"

            # make thunmnail image and show it in the README.md
            # "SourceFile"
            try:
                filename= data['EXIF']['SourceFile']
                im = Image.open( filename )
                im.thumbnail( (240,240) )
                thumbnail_filename= filename + ".png"
                im.save( thumbnail_filename )
            except Exception as e: 
                print("failed generating preview image, skip")

            thumbnail_filename=os.path.basename(thumbnail_filename)
            readme+= f"![{thumbnail_filename}]({thumbnail_filename})\n\n"

            readme+= f"{data['EXIF']['EXIF:ImageDescription']}"


            with open(os.path.join(d, "README.md"), 'w', encoding='utf-8') as outfile:
                outfile.write(readme)
