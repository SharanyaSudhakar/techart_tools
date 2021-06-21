#!/usr/bin/env python3
# Helper program to convert all .max files as fbx and extract textures for resuse in a non-forza environment
# this programs runs the command line input and is the start of the asset dump process.
#acts like a factory for asset dump

__author__ = 'Sharanya Sudhakar'

from pathlib import Path
import argparse

CAR = 'car'
TRACK = 'track'

assetList = [CAR, TRACK]

# using argparse to enable commandline execution of the this script
# to use script run with command line argument

parser = argparse.ArgumentParser(description='Asset dump for the input car or track asset. exports fbxes, .png material references and .tifs with a json dump of all asset references and param values.')
parser.add_argument('-a', metavar='Asset Name', type=str, nargs=1, required=True,
                    help ='name of the car/track asset -- NOTE: Track Asset Dump is not supported yet. --')
parser.add_argument('-t', metavar='Asset Type', type=str, nargs=1, required=True, 
                    help="Asset type: 'car' / 'track' only", choices = assetList)
parser.add_argument('-o', metavar='Output Path', type=Path, nargs=1, 
                    help='absolute path of the folder where assets need to be dumped.')
parser.add_argument('--onlyjson', help='will export only a json file containing all of the car asset info in one documnet from .car to .swatch',
                    action='store_true')
parser.add_argument('-jsonpath', metavar='JSON output Path', type=Path, nargs=1,
                    help='absolute path of the .json file where assets info needs to be exported.')
parser.add_argument('--onlyfbx', help='will export only the fbxes of the carasset in the output folder',
                    action='store_true')

args = parser.parse_args()
asset = args.a[0]
assetType = args.t[0]
outputFolder = args.o
onlyJson = args.onlyjson
onlyFBX = args.onlyfbx
jsonPath = args.jsonpath
jsonPath = jsonPath[0] if jsonPath else None

if assetType == CAR:
    assetPath = config.MEDIA_CARS / asset / 'Scene' / (asset + '.car')
elif assetType == TRACK:
    dottrack = asset + '.track'
    assetPath = config.MEDIA_TRACKS / asset / 'Scene' / dottrack / dottrack

if not assetPath.exists():
    print (f'invalid path: {assetPath}, asset files path is invalid')

elif not outputFolder and not jsonPath:
    print('-o or -jsonpath is needed')
else:
    print(f'Asset path found: {assetPath}\n')
    print(f'asset type: {assetType}')

    if assetType == CAR:
        carObj = car.CarAssetDump(assetPath, outputFolder[0])
        if not onlyFBX:
            pass
            #carObj.createDataDump(jsonFilepath=jsonPath, onlyJSON=onlyJson)
        else:
            pass
            #carObj.extractFbxFiles()
    else:
        print(f'asset type ({assetType}) not supported.')