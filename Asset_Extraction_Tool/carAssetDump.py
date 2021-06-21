#!/usr/bin/env python3
""" Helper program to convert all .max files as fbx and extract textures for resuse in a non-forza environment. This file also performs a data dump of a car in a json file
"""

__author__ = 'Sharanya Sudhakar'

import os
from pathlib import Path
import xml.etree.ElementTree as et
import subprocess
import json
import re
import shutil
import stat

MAXSCRIPT_PATH = c.SCRIPTS_MAX / 'MaxbatchScripts' / 'exportFbxs.ms'

class CarAssetDump:
        
    def __init__(self, carPath, outputFolder):

        if type(carPath) == Path:
            carPath = Path(carPath)

        if not carPath.exists():
            print (f'invalid path: {carPath}, asset file path is invalid')
            return

        self.carPath = carPath
        self.carname = carPath.stem
        self.output = outputFolder
        self.outFbxPath = self.output / self.carname / 'fbxs'
        self.outtifPath = self.output / self.carname / 'tifs'
        self.outPngPath = self.output / self.carname / 'png'

        self.scratchPath = c.SCRATCH_DIR / 'assetdumpScratch' / self.carname

        #'cars' in the relative path is removed and the carname changed to uppercase
        self.relOutputPath = lambda path: path[5:].replace(self.carname.lower(), self.carname.upper()) if 'cars' in path.lower() else path

        #syncFiles from the car folder
        p4.sync((c.MEDIA_CARS / self.carname))

        self.subcars = CarAssetDump.getSubcars(self.carname)

        #get all maxfiles and model files in car
        #walk the subcar for all associated .max files
        maxList1 = CarAssetDump.getMaxFilesFromSubcars(self.carname)

        #get all .max files not used in the car asset but exists
        maxList2 = CarAssetDump.getAllFilesOfType(self.carname,'max')

        #combine the lists and remove any duplicates.
        noDoupsList = list(set(maxList1 + maxList2))
        self.maxFilesList = noDoupsList
        self.modelFilesList = CarAssetDump.convertMaxToModel(self.maxFilesList)

        print(f'---LOG---:Retrived all .max and .model files from {self.carname}')
        #dictionary to store the data dump before being written to json
        self.data = {}
        self.errorLog = []

    @staticmethod
    def createFolder(folder):
        """
        creates folder for the path if one is not present.
        if the input is a str it will be converted to Path obj before fodlers are created.
        :param Path or Str folder: folder path to be created.
        """
        if not isinstance(folder,Path):
            folder = Path(folder)

        if not folder.is_dir():
            folder.mkdir(parents=True)

    def printErrorlog(self):
        """
        print all the error logs
        """
        for err in self.errorLog:
            print(err)

    def extractFbxFiles(self):
        """
        Function sends all .max paths to be written in a .txt file which is 
        then used by maxbatch to export all fbxes.
        """
        CarAssetDump.createFolder(self.outFbxPath)

        #path to temp txt files to store all max files
        self.txtpath_maxfiles = self.scratchPath / 'maxFilesList.txt'

        CarAssetDump.writeFilesToTxtFromList(self.maxFilesList,self.txtpath_maxfiles)
        print(f'---LOG---:Max files written to {self.txtpath_maxfiles}')

        #convert to fbx
        CarAssetDump.exportFbxFromMax(self.txtpath_maxfiles, self.outFbxPath)
        print(f'---LOG---:Max files successfully converted to fbx.')
        print(f'{len(self.maxFilesList)} max files converted.')

    def getModelDataDict(self, maxpath, onlyJSON):
        """
        given the maxpath, retrive the .model file information as a dictionary
        If onlyJSON param is true, then only the json file is generated with local paths.

        :param str maxpath: relative path of the max file.
        :param bool onlyJSON: outputs only the JSON file without extracting fbxes and tifs
        :return dict contained all .model information
        :rtype dict
        """
        modelPath = (c.MEDIA_CARS / self.relOutputPath(maxpath)).with_suffix('.model')

        #if .model doesnt exists (skeleton files for example dont have .models) return an empty dict
        if not modelPath.exists():
            msg = f'{modelPath} doesnt exist'
            print(msg)
            self.errorLog.append(msg)
            return {}

        modelXML = forza.metadata.ForzaXML(modelPath).root

        #dict to store information
        modelData = {}
        matkeys = modelXML.findall('MaterialRemap/MaterialKey')

        for matkey in matkeys:
            matname = matkey.attrib['UIName']

            #the UIName is unique and is used as a key for storing each matkey dict.
            modelData[matname] = {}
            modelData[matname]['value'] = matkey.attrib['Value']
            for matinstance in matkey:
                dotmaterial = matinstance.attrib['MaterialFile']

                #.material path is retieved and converted to a .png
                refFile = dotmaterial.replace('.material','.png')

                #the .png is also copied over to the output location for reference
                self.copypng(refFile)

                modelData[matname]['MaterialFile'] = refFile

                #get all shader paramters as its own dictionary
                modelData[matname]['ShaderParam'] = self.getDefaultShaderParams(dotmaterial, onlyJSON)

                #overwrite the original shaderparam values with the shaderparam found in the .model file  - these are replcaements of the default values
                for shaderparam in matinstance:
                    #shaderparamName is the dict key so information can be overwritten when needed by custom values
                    shaderparamName = shaderparam.attrib['ShaderPName']
                    modelData[matname]['ShaderParam'][shaderparamName] = shaderparam.attrib

                    #.swatch is changed as a .tif and the .tif is extracted from t10zip, renamed and moved to the output folder for a Texture
                    if '_Texture' in shaderparamName and not onlyJSON:
                        swatchPath = modelData[matname]['ShaderParam'][shaderparamName]['Value']
                        if '\\' in swatchPath:
                            tifPath = swatchPath.replace('.swatch','.tif')

                            print(f'---LOG---:Extracting .tif for {swatchPath}')
                            success = self.extractAndCopySwatch(swatchPath, tifPath)

                            if not success:
                                self.errorLog.append(f'Error Extracting .tif from {swatchPath}')

                            modelData[matname]['ShaderParam'][shaderparamName]['Value'] = self.outtifPath / Path(tifPath).name

        print(f'---LOG---: Model info added to dict for {modelPath}')
        return modelData

    def getDefaultShaderParams(self, dotmaterial, onlyJSON = False):
        """
        get default shader paramerters from the dotmaterial file
        from the .swatches with t10zip the .tif files are extraceted and moved to the output folder

        :param str dotmaterial: relative .material path
        :return shaderparam information from the .material
        :rtype dict
        """
        dotmaterial = c.MEDIA_CARS / self.relOutputPath(dotmaterial)

        if not dotmaterial.exists():
            msg = f'dotmaterial doesnt exist:{dotmaterial}'
            self.errorLog.append(msg)
            print(msg)
            return {}

        materialXML = forza.metadata.ForzaXML(dotmaterial).root
        shaderParamDict = {}
        shaderParams = materialXML.findall('ShaderP')

        for shaderParam in shaderParams:
            #shaderparamName is the dict key so information can be overwritten when needed by custom values
            shaderParamName = shaderParam.attrib['ShaderPName']
            shaderParamDict[shaderParamName] = shaderParam.attrib
            
            #.swatch is changed as a .tif and the .tif is extracted from t10zip, renamed and moved to the output folder for a Texture
            if '_Texture' in shaderParamName and not onlyJSON:
                swatchPath = shaderParamDict[shaderParamName]['Value']
                if '\\' in swatchPath:
                    tifPath = swatchPath.replace('.swatch','.tif')
                    print(f'---LOG---:Extracting .tif for {swatchPath}')
                    success = self.extractAndCopySwatch(swatchPath, tifPath)

                    if not success:
                        self.errorLog.append(f'Error Extracting .tif from {swatchPath}')

                    shaderParamDict[shaderParamName]['Value'] = self.outtifPath / Path(tifPath).name

        print(f'---LOG---: ShaderParam info added to dict for {dotmaterial}')
        return shaderParamDict

    def extractAndCopySwatch(self,swatchPath, tifPath):
        """
        extract .tif from the .zip, whose filepath is stored in the .swatch file
        move the extracted .tif to a new location
        The tif filename in the zip file and the filename in the tifpath dont match, when the file is copied over it will be renamed.

        :param str swatchPath: relative .swatch path
        :param str tifpath: rel destination and filename of tif file.
        :return ture/false for success
        :rtype bool
        """
        swatchPath = c.MEDIA_CARS / self.relOutputPath(swatchPath)
        tifPath = self.outtifPath / Path(tifPath).name
        p4.sync(swatchPath,verbose=False)

        if not swatchPath.exists():
            msg = 'Swatch not found {0}'.format(swatchPath)
            print(msg)
            self.errorLog.append(msg)
            return False

        swatchXML = forza.metadata.ForzaXML(swatchPath).root

        parent = 'TextureCompileParameter/TextureImageSources/TextureImageSource/ImageFilenames/ImageFilename'
        relimagepath = self.relOutputPath(swatchXML.find(parent).text)
        inputPath = (c.MEDIA_CARS / relimagepath).parent

        #extract to scratch as intermediary location
        imageScratchPath = (self.scratchPath / relimagepath) 

        #output folders setup
        #need only the directory for output
        outputPath = imageScratchPath.parent
        CarAssetDump.createFolder(outputPath)

        tifdir = tifPath.parent
        CarAssetDump.createFolder(tifdir)

        path = [str(c.zip_exe),'-d','-i',str(inputPath),'-o',str(outputPath)]

        # extract from T10Zip
        try:
            subprocess.check_call(path)
        except subprocess.CalledProcessError as err:
            msg = 'ERROR with ZIP: {0}'.format(err)
            print(msg)
            self.errorLog.append(msg)
            return False

        # move and rename .tif file
        try:
            #if dest exists dont move
            if not tifPath.exists():
                shutil.move(str(imageScratchPath),str(tifPath))
                print('SUCCESSFULLY MOVED .TIF')
        except:
            msg = 'failed to move and rename .tif file {0}'.format(outputPath)
            print(msg)
            self.errorLog.append(msg)
            return False

        return True

    def copypng(self, refFile):
        """
        given the relative path, copy file from src to output directory

        :param str refFile: relative path of any file in the media cars directory
        """
        refFilepath = c.MEDIA_CARS / self.relOutputPath(refFile)
        refFileOutputPath = self.outPngPath / Path(refFile).name

        CarAssetDump.createFolder(refFileOutputPath.parent)
        
        #sync files before it is copied file may exists in _library
        p4.sync(refFilepath, verbose=False)

        #if file is already copied or if the orig doesn't exist dont copy.
        if refFilepath.exists() and not refFileOutputPath.exists():
            shutil.copy(str(refFilepath),str(refFileOutputPath))

    def createDataDump(self, jsonFilepath = None, onlyJSON = False):
        """
        The fbxes are extracted and the data dump to json file is called here.
        The resulting JSON file contained the paths to the newly extracted location and will also be saved there.
        If onlyJSON param is true, then only the json file is generated with local paths.

        :param Path jsonFilepath: path to json file if outputting only the file
        :param bool onlyJSON: outputs only the JSON file without extracting fbxes and tifs
        """

        if not onlyJSON:
            CarAssetDump.createFolder(self.outPngPath)
            CarAssetDump.createFolder(self.outtifPath)
            self.extractFbxFiles()

        self.initiateCarDump(onlyJSON)
        self.writeJson(jsonFilepath)
        self.printErrorlog()

    def writeJson(self, jsonFilepath = None):
        """
        if path is provided, the json is written to this path.
        If one is not provided then a json file is created in the output folder location
        :param Path jsonFilepath: path to store json file
        """
        if jsonFilepath:
            self.jasonpath = jsonFilepath
        else:
            self.jasonpath = self.output / self.carname / (self.carname + '.json')

        CarAssetDump.createFolder(self.jasonpath.parent)

        with open(str(self.jasonpath), 'w+') as write_file:
            json.dump(self.data, write_file, indent=4)

    def initiateCarDump(self, onlyJSON = False):
        """
        reads the .car, .subcar, .model,.material and .swatch and stores all information in a dictionary to be written as json
        :param bool onlyJSON: if this is true, only the dictionary is created without the assets (fbxes, .tifs) being extracted
        """
        #.car dump
        carXML = forza.metadata.ForzaXML(self.carPath).root

        name = carXML.find('Description').text
        print(f'---LOG---: data dump for car {name}')

        self.data['car'] = name
        skel = carXML.find('Skeleton').attrib['path']
        skelfbxpath = self.outFbxPath / Path(skel).with_suffix('.fbx').name

        self.data['skeleton'] = str(skel) if onlyJSON else str(skelfbxpath)
        
        # extracting all .subcar from .car file
        subcars = carXML.findall('incl/Include')
        for subcar in subcars:
            subcar = subcar.attrib['path']
            subcarName = re.split('.subcar',subcar)[0]
            self.data[subcarName] = {}

        # .subcar dump
        subcars = CarAssetDump.getAllFilesOfType(self.carname, 'subcar')
        for subcar in subcars:
            subcarXML = forza.metadata.ForzaXML(subcar).root
            subcarName = subcarXML.find('Description').text
            instances = subcarXML.findall('i/Instance')
            for instance in instances:
                name = instance.find('Name')
                sname = name.attrib['shortname']
                print(f'writing subcar:{sname}')
                self.data[subcarName][sname] = {}

                self.data[subcarName][sname]['Instance'] = sname

                maxpath = instance.find('Model').attrib['value']
                if not maxpath:
                    continue
                print('maxpath', maxpath, subcar)
                finalMaxPath = self.outFbxPath / Path(maxpath).with_suffix('.fbx').name
                self.data[subcarName][sname]['Model'] = {}
                self.data[subcarName][sname]['Model']['path'] = str(maxpath) if onlyJSON else str(finalMaxPath)
                self.data[subcarName][sname]['Model']['Materials'] = self.getModelDataDict(maxpath, onlyJSON)

                transform = instance.find('Transform').attrib['value']
                self.data[subcarName][sname]['Transform'] = transform

                attribs = instance.find('Attributes')
                self.data[subcarName][sname][attribs.tag] = attribs.attrib

                aopath = instance.find('AOMap').attrib['DefaultPath']
                if '\\' in aopath:
                    tifpath = aopath.replace('.swatch','.tif')
                    self.extractAndCopySwatch(aopath, tifpath)
                    self.data[subcarName][sname]['AOMap'] = str(aopath) if onlyJSON else str(self.outtifPath / Path(tifpath).name)
                
                paintgrp = instance.find('paint')
                paintgrptags = [tag.attrib for tag in paintgrp]
                self.data[subcarName][sname]['paint'] = paintgrptags

                damagegrp = instance.find('DamageGroup')
                if damagegrp:
                    damagegrptags = [tag.attrib for tag in damagegrp]
                    self.data[subcarName][sname]['DamageGroup'] = damagegrptags

                assembly = instance.find('Assembly').attrib['value']
                self.data[subcarName][sname]['Assembly'] = assembly

    @staticmethod
    def getSubcars(carName):
        """
        method to retrive all subcars from the .car xml of the fiven carName
        This will return a list of all .subcars with their relative paths

        :param str carName: name of the car
        :return list of all .subcars
        :rtype list
        """
        carpath = c.MEDIA_CARS / carName / 'Scene'
        dotCarFile = carpath / (carName + '.car')
        xmlObj = forza.metadata.ForzaXML(dotCarFile)

        subcars=[]

        if not carpath.exists():
            print(f'{carName} car doesnt exist!')
            return

        for includeElem in xmlObj.root.findall('./incl/Include'):
            subcars.append(includeElem.attrib.get('path'))

        return subcars

    @staticmethod
    def getMaxFilesFromSubcars(carName):
        """
        given carname, find all .max files and return a list of .max paths.

        :param string carname: name of the car
        :returns list: .max paths
        """
        carpath = c.MEDIA_CARS / carName / 'Scene'
        dotSubcarsPath = carpath / (carName + '.subcars')

        if not carpath.exists():
            print(f'{carName} car doesnt exist!')
            return

        subcars = CarAssetDump.getSubcars(carName)

        #walk the subcars for all the .model files
        maxFiles=[]
        for subcar in subcars:
            subcarPath = dotSubcarsPath / subcar
            xmlObj = forza.metadata.ForzaXML(subcarPath)
            for instanceElem in xmlObj.root.findall('./i/Instance'):
                    modelElem = instanceElem.find('Model')
                    maxPath = c.MEDIA_CARS / modelElem.attrib.get('value')[5:]
                    if(maxPath.exists() and maxPath.suffix == '.max'):
                        maxFiles.append(str(maxPath))

        return maxFiles

    @staticmethod
    def getModelFilesFromSubcars(carName):
        """
        given carname, find all .max files and in turn find all .models
        return a list of .model paths

        :param string carname: name of the car
        :returns list: .model paths
        """
        if '\\' in carName or '.car' in carName:
            carName = Path(carName).stem

        maxfilesList = CarAssetDump.getMaxFilesFromSubcars(carName)
        return CarAssetDump.convertMaxToModel(maxfilesList)

    @staticmethod
    def getAllFilesOfType(carName, fileType):
        """
        given car name find all files  of type (fileType) in the cars/carName dir
        :param str carName
        :param str fileType without the '.'
        :return list of .(fileType) files
        :rtype: list
        """
        carpath = c.MEDIA_CARS / carName / 'Scene'

        p4.syncByType(carpath, fileType, verbose=False)
        if not carpath.exists():
            print(f'{carName} car doesnt exist!')
            return []

        fileList = []
        for carDir in carpath.iterdir():
            maxFiles = carDir.glob('**/*.'+ fileType)
            fileList.extend([str(max) for max in maxFiles])

        return fileList

    @staticmethod
    def convertMaxToModel(maxFilesList):
        """
        convert .max to .model suffix and return a list of .models only if they exist
        :param list maxFilesList: list of max files
        :return list of .model files
        :rtype list
        """
        substitute = lambda maxPath : str(Path(maxPath).with_suffix('.model'))
        modelFileList = [substitute(x) for x in maxFilesList ]

        #only return files if the .models exist
        exists = lambda modelFile: Path(modelFile).exists()
        finalList = filter(exists, modelFileList)
        return finalList

    @staticmethod
    def exportFbxFromMax(txtFilePath, output):
        """
        convert .max files to fbx
        this functions calls maxbatch and sends it a txtfiles path and an output path. the txtfiles holds all the .max files to be converted to fbx and the output path is a directory where these fbxes will be exported to
        :param Path txtFilePath: txt file spath that containes a list of all .max files to be exported
        :param Path output: output path is a directory where the fbxes will be exported to
        """
        #setup cmdline arguments for 3dsmax
        pathList = f"filesPathList:@\'{txtFilePath}\'"
        output = f"outputpath:@\'{output}\'"
        logpath = c.SCRATCH_LOGS_DIR / 'maxbatchcall.log'

        if not logpath.exists():
            logpath.parent.mkdir(parents=True)

        path = [str(c.MAXBATCH), str(MAXSCRIPT_PATH), '-v','5', '-dm', 'false', '-log', str(logpath), '-mxsValue', pathList, '-mxsValue', output]

        try:
            subprocess.check_call(path)
        except subprocess.CalledProcessError as err:
            if err.returncode == 200:
                msg = 'Custom Error code from maxscript: 200 \n.'
            else:
                msg = f"Error Code: {err.returncode}\nMax didn't save.\nCheck max listener log.\n\n3dsMax Batch Log -- {logpath}"

            print('Failed Saving 3ds Max File')
            print(msg)

    @staticmethod
    def writeFilesToTxtFromList(listToWrite, txtfilepath):
        """
        given a list write it to a textfile. each entry will be written to each file.
        if the file path doesnt exist one will be created
        :param listToWrite: list to be written to file
        :param txtfile path to be written to
        """
        CarAssetDump.createFolder(txtfilepath.parent)

        with open(str(txtfilepath), 'w+') as pathfiles:
            pathfiles.writelines((item + '\n') for item in listToWrite)