# -*- coding: utf-8 -*-
"""
Created on Sat May 16 13:43:40 2020

@author: Clare
"""
# Import modules
import arcpy
import numpy as np
from scipy import stats
import os

# Input parameters
inputRasters = arcpy.GetParameterAsText(0)
outputFolder = arcpy.GetParameterAsText(1)
timeValues = arcpy.GetParameterAsText(2)

# Split strings
inputRasters = inputRasters.split(";")
timeValues = timeValues.split(";")
arcpy.AddMessage ("Split parameter texts...")
#arcpy.AddMessage (timeValues)
for i in range(len(timeValues)):
    timeValues[i] = os.path.basename(timeValues[i])

arcpy.env.workspace = "C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0"
arcpy.env.overwriteOutput = True

# Get raster names from directory
inputRastName = []
for i in range(len(inputRasters)):
    inputRastName.append(os.path.basename(inputRasters[i]))
  
xTime = []
for i in range(len(inputRastName)):
    for j in range(len(timeValues)):
        if (str(inputRastName[i]) in timeValues[j]) == True:
            #print(inputRastName[i])
            #print(timeValues[j])
            xval = timeValues[j].replace(inputRastName[i] + ' ','')
            xTime.append(float(xval))


noData = 0
## Creating raster stack tif file
arcpy.CompositeBands_management(inputRasters,"stack.tif")
stack = "C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\stack.tif"
stackNP = arcpy.RasterToNumPyArray((arcpy.Raster(stack)),
                         (arcpy.Point((arcpy.Raster(stack)).extent.XMin,
                                      (arcpy.Raster(stack)).extent.YMin)),
                                      (arcpy.Raster(stack)).width,
                                      (arcpy.Raster(stack)).height,
                                      0)

arcpy.AddMessage ("Images stacked...")

def arcRast (inputRasterList,i):
    """
    function to convert raster to arcraster
    """
    listItem = inputRasterList[i]
    arcRaster = (arcpy.Raster(listItem))
    return arcRaster

# create empty numpy arrays
slope_rast = np.zeros((arcRast(inputRasters,1).width,arcRast(inputRasters,1).height)).astype(np.float)
dataCount_rast = np.zeros((arcRast(inputRasters,1).width,arcRast(inputRasters,1).height))
pvalue_rast = np.zeros((arcRast(inputRasters,1).width,arcRast(inputRasters,1).height))

#Iteration
row_no = -1
for row in stackNP[0]:
    row_no = row_no +1
    if row_no%100 == 0:
        arcpy.AddMessage ('Row number processed: ' + str(row_no))
    cell_no = -1
    for cell in row:
        cell_no = cell_no + 1
        cell_list = []
        rem = []
        x = xTime.copy()
        # Stack values for each pixel
        for i in range(len(inputRasters)):   
            cell_list.append(int(stackNP[i][row_no][cell_no]))
            if int(stackNP[i][row_no][cell_no]) == int(0):
                rem.append(int(i))

        # remove noData values
        rem.sort(reverse=True)  
        for j in range(len(rem)):
            remove = rem[j]
            del cell_list[remove]
            del x[remove]          
                
         # Linear Regression and count datapoints
        if len(cell_list) == 0:
            #print("No Data")
            slope_rast[row_no][cell_no] = -9999
            dataCount_rast[row_no][cell_no] = 0
            pvalue_rast[row_no][cell_no] = -9999
        else:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, cell_list)
            slope_rast[row_no][cell_no] = slope
            pvalue_rast[row_no][cell_no] = p_value
            dataCount_rast[row_no][cell_no] = len(cell_list)

## Output File creation
# Set Arc environment variables for output
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcRast(inputRasters,1)
arcpy.env.cellSize = arcRast(inputRasters,1)
lowerLeft = arcpy.Point(arcRast(inputRasters,1).extent.XMin,arcRast(inputRasters,1).extent.YMin)

# Output raster file names and locations
slopeOut = os.path.join(outputFolder,r"slope.tif")
dataCountOut = os.path.join(outputFolder,r"dataCount.tif")
pvalueOut = os.path.join(outputFolder,r"pvalue.tif")

#  (bands, rows, columns)
# change yvalue for band number - i.e. image number
output_r = arcpy.NumPyArrayToRaster(slope_rast,lowerLeft, arcRast(inputRasters,1).meanCellWidth, arcRast(inputRasters,1).meanCellHeight,noData)
output_r.save(slopeOut)
output_r = arcpy.NumPyArrayToRaster(dataCount_rast,lowerLeft, arcRast(inputRasters,1).meanCellWidth, arcRast(inputRasters,1).meanCellHeight,noData)
output_r.save(dataCountOut)
output_r = arcpy.NumPyArrayToRaster(pvalue_rast,lowerLeft, arcRast(inputRasters,1).meanCellWidth, arcRast(inputRasters,1).meanCellHeight,noData)
output_r.save(pvalueOut)


            

#arcpy.AddMessage (inputRasters)
