#!/usr/bin/env python
# __BEGIN_LICENSE__
#  Copyright (c) 2009-2013, United States Government as represented by the
#  Administrator of the National Aeronautics and Space Administration. All
#  rights reserved.
#
#  The NGT platform is licensed under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# __END_LICENSE__

import os, glob, optparse, re, shutil, subprocess, sys, string, time, urllib, urllib2
from BeautifulSoup import BeautifulSoup

#TODO: Clean this up!
sys.path.append('/home/smcmich1/programs/mechanize-0.2.5/')
#sys.path.append('/home/smcmich1/splinter/')
#sys.path.append('/home/smcmich1/selenium-2.35.0')


import mechanize
#import selenium
#import splinter

job_pool = [];

def man(option, opt, value, parser):
    print >>sys.stderr, parser.usage
    print >>sys.stderr, '''\
This program operates on LRO (.IMG) files, and performs the

'''

    sys.exit()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def add_job( cmd, num_working_threads=4 ):
    if ( len(job_pool) >= num_working_threads):
        job_pool[0].wait();
        job_pool.pop(0);
    print cmd;
    job_pool.append( subprocess.Popen(cmd, shell=True) );

def wait_on_all_jobs():
    print "Waiting for jobs to finish";
    while len(job_pool) > 0:
        job_pool[0].wait();
        job_pool.pop(0);


#--------------------------------------------------------------------------------


#TODO: Get an automated way to do this
if False:
    """
    def retrieveLolaFile(minLat, maxLat, minLon, maxLon):

        lolaUrl = 'http://ode.rsl.wustl.edu/moon/lrololadataPointSearch.aspx'


        browser = Browser()
        browser.visit(lolaUrl)
        
        browser.find_by_name('txtMaxLatitude'  ).fill(str(maxLat))
        browser.find_by_name('txtMinLatitude'  ).fill(str(minLat))
        browser.find_by_name('txtWestLongitude').fill(str(minLon))
        browser.find_by_name('txtEastLongitude').fill(str(maxLon))
        
        browser.find_by_id('btnPreviewCountPoints').click()


        time.sleep(4) #TODO: Wait until form is ready

        browser.find_by_id('btnGenerateCSV').click()

        time.sleep(30) #TODO: Wait until form is ready

        fileRef = browser.find_by_id('hlPointPerRowCsvCsv')
        print fileRef


    #    data= {'txtMaxLatitude':str(maxLat), 'txtMinLatitude':str(minLat), 'txtWestLongitude':str(minLon), 'txtEastLongitude':str(maxLon)}
    #    request = urllib2.Request(lolaUrl, urllib.urlencode(data))
    #    response = urllib2.urlopen(request)


        # Open browser object to ASU data search page 
     #   br = mechanize.Browser()
     #   br.open(lolaUrl)

    #    for form in br.forms():
    #      print '--------------'
    #       print form

    #	# Get unnamed form handle, set product ID filter
    #	br.form = list(br.forms())[0]
    #	control = br.form.find_control("txtMaxLatitude")
    #	control.value = str(maxLat)
    #	control = br.form.find_control("txtMinLatitude")
    #	control.value = str(minLat)
    #	control = br.form.find_control("txtWestLongitude")
    #	control.value = str(minLon)
    #	control = br.form.find_control("txtEastLongitude")
    #	control.value = str(maxLon)
    #
    #	control = br.form.find_control("txtEastLongitude")
    #	control.value = str(maxLon)

	    # Submit the form, then parse the response of the form submission
    #	response = br.submit()
        parsedResponse = BeautifulSoup(response.read())

        f = open('response.txt', 'w')
        f.write(parsedResponse.prettify())
        f.close()


    #    page = BeautifulSoup(urllib2.urlopen((lolaUrl)).read())
    #    f = open('debug.txt', 'w')
    #    f.write(page.prettify())
    #    f.close()
    """

#TODO: Probably don't need this!
# Reads in the results of a DEM alignment operation
def readPcAlignResults(outputFolder, prefix):

    # Output transform is in this format (excepting whitespace):
    #  0.9999968710678928    0.002478390929168969 0.0003397540659725261 -1024.133917521918
    # -0.002477949646550771  0.9999960937499494  -0.001293155207595954   4739.357603680983
    # -0.0003429576829447021 0.001292309267933415 0.9999991061579924      124.7476123821689
    #  0                     0                    0                         1

    # File locations (PREFIX = align_ASU and align_LOLA):
    # outputFolder/PREFIX-transform.txt
    # outputFolder/PREFIX-beg_errors.txt
    # outputFolder/PREFIX-end_errors.txt

    # Get the file paths
    transformPath    = outputFolder + '/' + prefix + '-transform.txt'
    initialErrorPath = outputFolder + '/' + prefix + '-beg_errors.txt'
    finalErrorPath   = outputFolder + '/' + prefix + '-end_errors.txt'
    
#TODO: Make sure to pull in ASP update which inverts output matrix if needed!
    # Read in the transform matrix
    transformMatrix = []
    transformFile = open(transformPath, 'r')
    for line in transformFile:
        transformMatrix.append(float, line.split(' '))

    # For now just return the matrix
    return transformMatrix


# Gets the download links to the LE and RE parts of a given LRONAC ID
def getLinksForImgFile(productId):

	pdsUrl = 'http://wms.lroc.asu.edu/lroc/search'

	# Open browser object to ASU data search page 
	br = mechanize.Browser()
	br.open(pdsUrl)
 
	# Get unnamed form handle, set product ID filter
	br.form = list(br.forms())[0]
	control = br.form.find_control("filter[product_id]")
	control.value = productId #'M112646261'

	# Submit the form, then parse the response of the form submission
	response = br.submit()
	parsedResponse = BeautifulSoup(response.read())


	# Get the links to the LE and RE file pages
	resultsNode = parsedResponse.find(id="table")

	leftRegex  = "M[0-9]*LE$"
	rightRegex = "M[0-9]*RE$"
	leftLink  = 'NOT_FOUND'
	rightLink = 'NOT_FOUND'
	for line in resultsNode.findAll('a'):
		if re.search( leftRegex, line.get('href')):
			leftLink = 'http://wms.lroc.asu.edu' + line.get('href')
		if re.search( rightRegex, line.get('href')):
			rightLink = 'http://wms.lroc.asu.edu' + line.get('href')

	# Extract the left and right EDR paths
	leftEdrPath  = 'NOT_FOUND'
	rightEdrPath = 'NOT_FOUND'
	if (leftLink != 'NOT_FOUND'):
		leftPage  = BeautifulSoup(urllib2.urlopen(leftLink).read())
		for link in leftPage.findAll('a'):
			if link.string == 'Download EDR':
				leftEdrPath = link.get('href')
	if (rightLink != 'NOT_FOUND'):
		rightPage = BeautifulSoup(urllib2.urlopen(rightLink).read())
		for link in rightPage.findAll('a'):
			if link.string == 'Download EDR':
				rightEdrPath = link.get('href')

	# Return the output
	results = (leftEdrPath, rightEdrPath)
	return results


# Obtains the full list of files required to replicate ASU's DEMs from their webpage
def getDataList():
    baseUrl     = "http://wms.lroc.asu.edu/lroc/dtm_select?page="
    currentPage = 1

    # Get URL to current page
    currentPageUrl = baseUrl + str(currentPage)

    # Parse the current page
    parsedIndexPage = BeautifulSoup(urllib2.urlopen((currentPageUrl)).read())


    # Figure out how many pages in total
    largestPage = 1
    pageNavNode = parsedIndexPage.find(id="dtm_select_pagenav")
    for line in pageNavNode.findAll('a'):
        index = line.get('href').find("page=")
        if ( index >= 0 ):  
            if (line.string.find("Next") < 0):
                page = int(line.string)
                if (page > largestPage):
                    largestPage = page
    print "Found " + str(largestPage) + " pages of DEMs"

	# Loop through all index pages and collect DEM pages
    dtmPageList = []
    for currentPage in range(1,largestPage+1):
        currentPageUrl  = baseUrl + str(currentPage)
        parsedIndexPage = BeautifulSoup(urllib2.urlopen((currentPageUrl)).read())
        tableNode       = parsedIndexPage.find(id="dtm_select_selectiontable")
        for line in tableNode.findAll('a'):	
            if (line.get('href').find("dtm_detail")	> 0):
                dtmPageList.append('http://wms.lroc.asu.edu/' + line.get('href'))
		
    print "Found " + str(len(dtmPageList)) + " DEM pages"

    outputFilePath = 'logFile.txt'
    outputFile = open(outputFilePath, 'w')

	# Loop through all individual pages and get download links
    for p in dtmPageList:

#		print p
        thisPage        = BeautifulSoup(urllib2.urlopen((p)).read())
        downloadSection = thisPage.find(id="dtm_downloads")	

        # Find the two input files (the links are not here but we can get the names)
        firstImgFile  = "NOT_FOUND"
        secondImgFile = "NOT_FOUND"
        imgFileRegex  = "_M[0-9]*_[a-zA-Z0-9]*.IMG$"
        for line in downloadSection.findAll('a'):

            matchObj = re.search( imgFileRegex, line.get('href'))
            if matchObj:
                    startIndex = line.string.rfind("_M")  + 1
                    stopIndex  = line.string.find("_", startIndex) 
                    imgFile    = line.string[startIndex:stopIndex]
                    if (firstImgFile  == "NOT_FOUND"):
                        firstImgFile = imgFile
                    else:
                        if imgFile != firstImgFile:
                            secondImgFile = imgFile
                            break

		# Find the ASU DEM	
        demLink = "NOT_FOUND"
        for line in downloadSection.findAll('a'):
            if  line.get('href').find(".TIF") >= 0:
                demLink = line.get('href')
                break

        # Get the lat/lon boundaries
        positionNode = thisPage.find(id="detailtable")
        rows         = positionNode.findAll('tr')
   		
        cols   = rows[0].findAll('td')
        minLat = cols[1].string
        maxLat = cols[3].string
   		
        cols   = rows[1].findAll('td')
        minLon = cols[1].string
        maxLon = cols[3].string

		# Track down the links to the input files
        if (firstImgFile != "NOT_FOUND"):
        	print 'Finding links for image ' + firstImgFile
        	firstImgDownloadPaths  = getLinksForImgFile(firstImgFile)
        if (secondImgFile != "NOT_FOUND"):
        	print 'Finding links for image ' + secondImgFile
        	secondImgDownloadPaths = getLinksForImgFile(secondImgFile)

        # Log the results
        outputFile.write('----------------------------------------------\n')
        outputFile.write('ASU DTM = ' + demLink + '\n')
        outputFile.write('Min lat = ' + minLat + '\n')
        outputFile.write('Max lat = ' + maxLat + '\n')
        outputFile.write('Min lon = ' + minLon + '\n')
        outputFile.write('Max lon = ' + maxLon + '\n')
        if (firstImgFile != "NOT_FOUND"):
            outputFile.write(firstImgDownloadPaths[0] + '\n')
            outputFile.write(firstImgDownloadPaths[1] + '\n')
        if (secondImgFile != "NOT_FOUND"):
            outputFile.write(secondImgDownloadPaths[0] + '\n')
            outputFile.write(secondImgDownloadPaths[1] + '\n')

    # Done obtaining data, close the file.
    outputFile.close()

# Fetches all of the files listed in the log folder and puts them in different directories
def retrieveDataFiles(logPath, outputDir):
	
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    currentOutputFolder = outputDir
    for line in open(logPath, 'r'):
        if (line.find('ASU') >= 0):
            # Create new folder for this DEM
            eqPos       = line.find('=')
            asuUrl	    = line[eqPos+2:]
            asuFileName = os.path.basename(asuUrl)
            noExt       = os.path.splitext(asuFileName)[0]
            demName     = noExt[8:]
            currentOutputFolder = outputDir           + demName + '/'
            asuDemPath          = currentOutputFolder + asuFileName
            if not os.path.exists(currentOutputFolder):
                os.makedirs(currentOutputFolder)

            # wget DEM
            #			print "wget --directory-prefix=" + currentOutputFolder + "  " + asuUrl
            if not os.path.exists(asuDemPath.strip()):
                os.system("wget -P " + currentOutputFolder + "  " + asuUrl)

            #TODO: Download the LOLA data file
  
        elif (line.find('.IMG') >= 0):
            # wget image
            imgUrl	    = line
            imgFileName = os.path.basename(imgUrl)
            imgCopyPath = currentOutputFolder + '/' + imgFileName
            #			print "wget -P " + currentOutputFolder + "  " + imgUrl
            print imgCopyPath
            if not os.path.exists(imgCopyPath):
                os.system("wget -P " + currentOutputFolder + "  " + imgUrl)



# Calls caminfo on a mosaic and returns the CenterLatitude value
def getMosaicCenterLatitude(mosaicPath):
  
    # Call caminfo (from ISIS) on the input mosaic to find out the CenterLatitude value
    outputFolder     = os.path.dirname(mosaicPath)
    camInfoOuputPath = outputFolder + "/camInfoOutput.txt"
    if not os.path.exists(camInfoOuputPath):
        cmd = 'caminfo from=' + mosaicPath + ' to=' + camInfoOuputPath
        add_job(cmd, 2)    
        wait_on_all_jobs()

    # Read in the output file to extract the CenterLatitude value
    centerLatitude = -9999
    infoFile       = open(camInfoOuputPath, 'r')
    for line in infoFile:
        if (line.find('CenterLatitude') >= 0):
            eqPt   = line.find('=')
            numStr = line[eqPt+2:]
            centerLatitude = float(numStr)
            break
    # Make sure we found the desired value
    if (centerLatitude == -9999):          
        raise Exception("Unable to find CenterLatitude in file " + camInfoOuputPath)
        
    return str(centerLatitude) # Convert back to string since it will be used as a cmd line argument


# Make a stereo DEM in a single sub folder
def makeDem(demFolder):

    # Get list of files in the folder
    # - There should be the ASU DEM (.TIF extension) and 0-4 .IMG files
    fileList = os.listdir(demFolder)
    
    if (len(fileList) < 6):
        raise Exception("Unable to form DEM from directory " + demFolder + " -> Not enough input files!")
    
    # Sort the file list so .IMG pairs come one after the other
    fileList.sort() 

    asuDem    = 'NOT_FOUND'
    lolaData  = 'NOT_FOUND'
    leftImgA  = 'NOT_FOUND'
    leftImgB  = 'NOT_FOUND'
    rightImgA = 'NOT_FOUND'
    rightImgB = 'NOT_FOUND'            
    filesFound = 0
        
    for f in fileList:
        # Determine the file type
        fullPath     = demFolder + '/' + f
        justFileName = f
        ext = os.path.splitext(justFileName)[1]
        
        if (ext == '.TIF'): # This is the ASU DEM
            asuDem     = fullPath
            filesFound = filesFound + 1
            
        if (ext == '.csv'): # This is the LOLA data
            lolaData   = fullPath
            filesFound = filesFound + 1

        if (ext == '.IMG'): # This is an LRONAC input file, figure out which one
            if (justFileName.find('LE') >= 0):
                if (leftImgA  == 'NOT_FOUND'):
                    leftImgA = fullPath
                else:
                    leftImgB = fullPath
            else:
                if (rightImgA  == 'NOT_FOUND'):
                    rightImgA = fullPath
                else:
                    rightImgB = fullPath
            filesFound = filesFound + 1

    #TODO: Operate with incomplete input files?
    # If we don't have all the input files quit
    if (filesFound != 6):
        raise Exception("Unable to form DEM from directory " + demFolder + " -> Not enough input files!")

    print 'found all files'

    #TODO: Allow more simultaneous jobs!
    numThreads = 2

    #TODO: These should be passed into lronac2mosaic.py!
    mosaicNameA = os.path.splitext(leftImgA)[0] + '.lronaccal.lronacecho.noproj.mosaic.norm.cub'
    mosaicNameB = os.path.splitext(leftImgB)[0] + '.lronaccal.lronacecho.noproj.mosaic.norm.cub'

    # Merge the two LRONAC pairs 
    if not os.path.exists(mosaicNameA):
        cmd = 'lronac2mosaic.py ' + leftImgA + ' ' + rightImgA + ' --keep'
        add_job(cmd, numThreads)
    if not os.path.exists(mosaicNameB):
        cmd = 'lronac2mosaic.py ' + leftImgB + ' ' + rightImgB + ' --keep'        
        add_job(cmd, numThreads)
    
    wait_on_all_jobs()

    # Quit if either mosaic was not successfully created
    if not os.path.exists(mosaicNameA):
        raise Exception("Failed to form mosaic " + mosaicNameA + " , cannot proceed in folder " + demFolder)
    if not os.path.exists(mosaicNameA):
        raise Exception("Failed to form mosaic " + mosaicNameB + " , cannot proceed in folder " + demFolder)

    outputPrefix = demFolder + '/stereo'

    # This is the location of the output point cloud from the stereo process
    outputPcPath = outputPrefix + '-PC.tif'

    # Now feed the two merged images into the stereo function    
    if not os.path.exists(outputPcPath):
#        cmd ='stereo --alignment affineepipolar --subpixel-mode 1 --disable-fill-holes ' + mosaicNameA +' '+ mosaicNameB +' '+ outputPrefix
        cmd ='parallel_stereo --alignment affineepipolar --subpixel-mode 1 --disable-fill-holes ' + mosaicNameA +' '+ mosaicNameB +' '+ outputPrefix
        add_job(cmd, numThreads)
        wait_on_all_jobs()
#--nodes-list PBS_NODEFILE --processes 4 --threads-multiprocess 16 --threads-singleprocess 32


      
    # Now convert from point cloud to DEM
    outputDemPrefix = demFolder + '/stereo'
    outputDemPath   = outputDemPrefix + '-DEM.tif'
    centerLatitude = getMosaicCenterLatitude(mosaicNameA)
    if not os.path.exists(outputDemPath):
      # Find out the center latitude of the mosaic
      optionsText = ' --t_srs "+proj=eqc +lat_ts='+centerLatitude+' +lat_0=0 +a=1737400 +b=1737400 +units=m" --nodata -32767'
      cmd         = 'point2dem -r moon -o ' + outputDemPrefix +' '+ outputPcPath + optionsText
      add_job(cmd, numThreads)
      wait_on_all_jobs()

    return [outputDemPath, asuDem, lolaData, centerLatitude]

# Computes the best transform to align the LRONAC DEM with the ASU and LOLA data
# - Also writes out the transformed mosaic as a point cloud aligned with the reference input
def computeDemTransforms(mosaicPath, asuDemPath, lolaDataPath):

    # Quit if the mosaic was not formed
    if not os.path.exists(mosaicPath):
        raise Exception("Missing file " + mosaicPath + " , cannot run pc_align.")

    # Determine the output locations
    intputFolder              = os.path.dirname(mosaicPath)
    outputAsuPrefix           = intputFolder + '/align_ASU_PC'
    outputLolaPrefix          = intputFolder + '/align_LOLA_PC'
    asuAlignedPointCloudPath  = intputFolder + '/align_ASU_PCtrans_reference.tif'
    lolaAlignedPointCloudPath = intputFolder + '/align_LOLA_PCtrans_reference.tif'

    # Larger DEM should be the first (reference) input
    numThreads = 2
    if (os.path.exists(asuDemPath)) and (not os.path.exists(asuAlignedPointCloudPath)):
        cmd = 'pc_align --max-displacement 250 --max-num-reference-points 25000000 --save-inv-transformed-reference-points -o ' + outputAsuPrefix  + ' ' + mosaicPath + ' ' + asuDemPath
        add_job(cmd, numThreads)
    if (os.path.exists(lolaDataPath)) and (not os.path.exists(lolaAlignedPointCloudPath)):
        cmd = 'pc_align --max-displacement 250 --max-num-reference-points 25000000 --save-inv-transformed-reference-points -o ' + outputLolaPrefix + ' ' + mosaicPath + ' ' + lolaDataPath
        add_job(cmd, numThreads)

#    # ASU-LOLA sanity check
#    asuLolaOutputPath = intputFolder + '/test_ASU_LOLA_PC'
#    cmd = 'pc_align --max-displacement 250 --max-num-reference-points 25000000 --save-inv-transformed-reference-points -o ' + asuLolaOutputPath + ' ' + asuDemPath + ' ' + lolaDataPath
#    add_job(cmd, numThreads)

    wait_on_all_jobs()

def rerenderDem(mosaicPath, centerLatitude):

    # Get paths to aligned point clouds and create output paths
    outputFolder = os.path.dirname(mosaicPath)
    asuAlignedPointCloudPath  = outputFolder + '/align_ASU_PCtrans_reference.tif'
    lolaAlignedPointCloudPath = outputFolder + '/align_LOLA_PCtrans_reference.tif'
    asuAlignedDemPrefix       = outputFolder + '/align_ASU'
    lolaAlignedDemPrefix      = outputFolder + '/align_LOLA'
    asuAlignedDemPath         = outputFolder + '/align_ASU-DEM.tif'
    lolaAlignedDemPath        = outputFolder + '/align_LOLA-DEM.tif'
    
    numThreads = 2
    optionsText = ' --t_srs "+proj=eqc +lat_ts='+centerLatitude+' +lat_0=0 +a=1737400 +b=1737400 +units=m" --nodata -32767'
  
    # ASU registered point cloud to DEM
    if ( (os.path.exists(asuAlignedPointCloudPath)) and (not os.path.exists(asuAlignedDemPath)) ):
        cmd = 'point2dem -r moon -o ' + asuAlignedDemPrefix +' '+ asuAlignedPointCloudPath + optionsText
        add_job(cmd, numThreads)

    # LOLA registered point cloud to DEM
    if ( (os.path.exists(lolaAlignedPointCloudPath)) and (not os.path.exists(lolaAlignedDemPath)) ):
        cmd = 'point2dem -r moon -o ' + lolaAlignedDemPrefix +' '+ lolaAlignedPointCloudPath + optionsText
        add_job(cmd, numThreads)

    wait_on_all_jobs()

# Performs comparisons between our aligned dems and the ASU/LOLA data
def compareDems(demPath, asuDemPath, lolaDataPath):

    # Get paths to aligned point clouds and create output paths
    outputFolder         = os.path.dirname(demPath)
    asuAlignedDemPath    = outputFolder + '/align_ASU-DEM.tif'
    lolaAlignedDemPath   = outputFolder + '/align_LOLA-DEM.tif'
    geodiffPrefixOut     = outputFolder + '/geodiff_ASU'
    geodiffOutputPath    = outputFolder + '/geodiff_ASU-diff.tif'
    asuDiffStatsPath     = outputFolder + '/ASU_diff_stats.txt'
    lolaDiffStatsPath    = outputFolder + '/LOLA_diff_stats.txt'
    lolaAsuDiffStatsPath = outputFolder + '/LOLA_ASU_diff_stats.txt'
    

    numThreads = 2
    
    # The geodiff tool can compare two geotif DEMs and produce a difference image
    print asuAlignedDemPath
    print asuDemPath
    print geodiffOutputPath
    if ( (os.path.exists(asuAlignedDemPath)) and (os.path.exists(asuDemPath)) and (not os.path.exists(geodiffOutputPath)) ):
#        cmd = 'geodiff --absolute -o ' + geodiffPrefixOut +' '+ asuAlignedDemPath +' '+ asuDemPath
        cmd = 'geodiff --absolute -o ' + geodiffPrefixOut +' '+ asuDemPath +' '+ asuAlignedDemPath
        add_job(cmd, numThreads)    
        wait_on_all_jobs()

    #TODO: Fix paths!
    # Open up the difference image to build statistics
    if (os.path.exists(geodiffOutputPath)) and (not os.path.exists(asuDiffStatsPath)):
        cmd = '~/repot/visionworkbench/src/vw/tools/imagestats --limit-hist=1 -i ' + geodiffOutputPath + ' -o ' + asuDiffStatsPath
        add_job(cmd, numThreads)       
    
    # Call script to compare LOLA data with the DEM
    if (os.path.exists(lolaDataPath)) and (os.path.exists(lolaAlignedDemPath)) and (not os.path.exists(lolaDiffStatsPath)):
        cmd = '~/repot/visionworkbench/src/vw/tools/lola_compare --limit-hist=2 -l ' + lolaDataPath + ' -d ' + lolaAlignedDemPath + ' -o ' + lolaDiffStatsPath
        add_job(cmd, numThreads)    

    # Call script to compare LOLA data with the ASU DEM
    if (os.path.exists(lolaDataPath)) and (os.path.exists(asuDemPath)) and (not os.path.exists(lolaAsuDiffStatsPath)):
        cmd = '~/repot/visionworkbench/src/vw/tools/lola_compare --limit-hist=2 -l ' + lolaDataPath + ' -d ' + asuDemPath + ' -o ' + lolaAsuDiffStatsPath
        add_job(cmd, numThreads)    


    wait_on_all_jobs()        
 
def generateDebugImages(demPath, asuDemPath, lolaDataPath):

    # Get paths to aligned point clouds and create output paths
    outputFolder       = os.path.dirname(demPath)
    asuAlignedDemPath  = outputFolder + '/align_ASU-DEM.tif'
    lolaAlignedDemPath = outputFolder + '/align_LOLA-DEM.tif'
    geodiffOutputPath  = outputFolder + '/geodiff_ASU-diff.tif'

    ourDemPathColor         = outputFolder + '/stereo-DEM_COLORIZED.tif'
    asuDemPathColor         = outputFolder + '/ASU-DEM_COLORIZED.tif'    
    asuAlignedDemPathColor  = outputFolder + '/align_ASU-DEM_COLORIZED.tif'
    lolaAlignedDemPathColor = outputFolder + '/align_LOLA-DEM_COLORIZED.tif'
    geodiffOutputPathColor  = outputFolder + '/geodiff_ASU-diff_COLORIZED.tif'

    numThreads = 5

    redoDem            = (os.path.exists(demPath           )) and (not os.path.exists(ourDemPathColor        ))
    redoAsuDem         = (os.path.exists(asuDemPath        )) and (not os.path.exists(asuDemPathColor        ))
    redoAsuAlignedDem  = (os.path.exists(asuAlignedDemPath )) and (not os.path.exists(asuAlignedDemPathColor ))
    redoLolaAlignedDem = (os.path.exists(lolaAlignedDemPath)) and (not os.path.exists(lolaAlignedDemPathColor))
    redoGeoDiff        = (os.path.exists(geodiffOutputPath )) and (not os.path.exists(geodiffOutputPathColor ))

    # Generate colorized version of all the DEMs
    print "Building colorized images..."
    if redoDem:
        cmd = '~/repot/visionworkbench/src/vw/tools/colormap -o ' + ourDemPathColor +' '+ demPath
        add_job(cmd, numThreads)    

    if redoAsuDem:
        cmd = '~/repot/visionworkbench/src/vw/tools/colormap -o ' + asuDemPathColor +' '+ asuDemPath
        add_job(cmd, numThreads)    

    if redoAsuAlignedDem:
        cmd = '~/repot/visionworkbench/src/vw/tools/colormap -o ' + asuAlignedDemPathColor +' '+ asuAlignedDemPath
        add_job(cmd, numThreads)    

    if redoLolaAlignedDem:
        cmd = '~/repot/visionworkbench/src/vw/tools/colormap -o ' + lolaAlignedDemPathColor +' '+ lolaAlignedDemPath
        add_job(cmd, numThreads)    

    if redoGeoDiff:
        cmd = '~/repot/visionworkbench/src/vw/tools/colormap -o ' + geodiffOutputPathColor +' '+ geodiffOutputPath
        add_job(cmd, numThreads)    
        
    wait_on_all_jobs()    


#    # Build KML overlays for each map
#    print "Building KML overlays..."
#    if redoDem:
#        cmd = '~/repot/visionworkbench/src/vw/tools/image2qtree -m kml ' + ourDemPathColor
#        add_job(cmd, numThreads)    

#    if redoAsuDem:
#        cmd = '~/repot/visionworkbench/src/vw/tools/image2qtree -m kml ' + asuDemPathColor
#        add_job(cmd, numThreads)    
        
#    if redoAsuAlignedDem:
#        cmd = '~/repot/visionworkbench/src/vw/tools/image2qtree -m kml ' + asuAlignedDemPathColor
#        add_job(cmd, numThreads)    
        
#    if redoLolaAlignedDem:
#        cmd = '~/repot/visionworkbench/src/vw/tools/image2qtree -m kml ' + lolaAlignedDemPathColor
#        add_job(cmd, numThreads)    
#        
#    if redoGeoDiff:
#        cmd = '~/repot/visionworkbench/src/vw/tools/image2qtree -m kml ' + geodiffOutputPathColor
#        add_job(cmd, numThreads)                            


# Removes temporary files we are no longer interested in
#def cleanTempFiles():



# Makes a stereo DEM in each sub folder
def makeDems(outputDir):

    # Call subfunction for each folder
    for f in os.listdir(outputDir):
	
        folderPath = os.path.join(outputDir, f)
		
        try:
    		# Make a DEM out of the IMG files
            [ourDemPath, asuDemPath, lolaDataPath, centerLat] = makeDem(folderPath)

            # Now compare the DEMs with the reference data sets
            computeDemTransforms(ourDemPath, asuDemPath, lolaDataPath)
            
            # Convert the aligned point clouds back into DEMs
            rerenderDem(ourDemPath, centerLat)
  
            # Compute the error between the aligned DEMs            
            compareDems(ourDemPath, asuDemPath, lolaDataPath)
            
            
            generateDebugImages(ourDemPath, asuDemPath, lolaDataPath)
            
            #Final reports
            
        
        except Exception,e: # Catch any errors, the program will move on to the next folder
            print "Caught: ", e
            print "Unable to process data in folder " + folderPath


#--------------------------------------------------------------------------------

#TODO: Support for file based logging of results

def main():

    try:
        try:
            usage = "usage: lronacPipeline.py [--help][--manual]\n  "
            parser = optparse.OptionParser(usage=usage)
            parser.set_defaults(delete =True)
            parser.set_defaults(threads=4)
            parser.set_defaults(fakePvl=True)
            parser.add_option("--manual", action="callback", callback=man,
                              help="Read the manual.")
            (options, args) = parser.parse_args()

#            if not args: parser.error("need .IMG files")

        except optparse.OptionError, msg:
            raise Usage(msg)

        print "Beginning processing....."

#        retrieveLolaFile(12.8, 13, 10.8, 11)


        dataDirectory = '/home/smcmich1/repot/lronacPipeline/testData2/'

#        getDataList()
	
        # Download all of the data we need 
        print 'Retrieving data files'
#        retrieveDataFiles('logFileSingle.txt', dataDirectory)

        # Process all of the data!
        print 'Making DEMs'
        makeDems(dataDirectory)


#TODO: Add GIT login name/email


        print "Finished"
        return 0

    except Usage, err:
        print >>sys.stderr, err.msg
        return 2

	# To more easily debug this program, comment out this catch block.
    # except Exception, err:
    #     sys.stderr.write( str(err) + '\n' )
    #     return 1


if __name__ == "__main__":
    sys.exit(main())
