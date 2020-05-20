# -*- coding: utf-8 -*-
"""
Created on Sat May  9 13:16:42 2020

@author: Clare

Script tool for ArcGIS Pro which conducts a per pixel linear regression on a time series of single band rasters.

"""
# Import modules
import arcpy
import numpy as np
from scipy import stats
import os


# Input parameters
outputFolder = arcpy.GetParameterAsText(0)
inputRasters = arcpy.GetParameterAsText(1)
linRegBool = arcpy.GetParameterAsText(2)
theilSenBool = arcpy.GetParameterAsText(3)

# Trend check and error
if linRegBool == "false" and theilSenBool == "false":
    arcpy.AddError("No Trend method found. Please tick one of the boxes")
    exit
elif  linRegBool == "true":
    arcpy.AddMessage ("Simple Linear regression selected...")
elif  theilSenBool == "true":
    arcpy.AddMessage ("Theil-Sen estimator selected...")

# Split strings
inputRasters = inputRasters.split(";")
arcpy.AddMessage ("Split parameter texts...")

# Get raster file Directories
inputRastDir = []
for i in range(len(inputRasters)):
    inputRastDir.append(inputRasters[i].split(" ")[0])
    
# Get inputted X/time values
xTime = []
for i in range(len(inputRasters)):
    xTime.append(int(os.path.basename(inputRasters[i].split(" ")[1])))
    
# Get NoData values from input raster 
for i in inputRastDir :
    desc=arcpy.Describe(i)
    noData = desc.noDataValue
    
arcpy.AddMessage (" X Values = ") 
arcpy.AddMessage (xTime) 
    
## Creating raster stack tif file
arcpy.CompositeBands_management(inputRastDir,"stack") #.tif extension broke this?
stack = os.path.join(outputFolder,r"stack.tif")
stackNP = arcpy.RasterToNumPyArray((arcpy.Raster(stack)),
                         (arcpy.Point((arcpy.Raster(stack)).extent.XMin,
                                      (arcpy.Raster(stack)).extent.YMin)),
                                      (arcpy.Raster(stack)).width,
                                      (arcpy.Raster(stack)).height)
arcpy.AddMessage ("Images stacked...")


def arcRast (inputRasterList,i):
    """
    function to convert raster to arcraster, returns arc raster
    """
    listItem = inputRasterList[i]
    arcRaster = (arcpy.Raster(listItem))
    return arcRaster

# create empty numpy arrays
dataCount_rast = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))  
if linRegBool == "true":   
    linReg_slope = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
    linReg_pvalue = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
    linReg_std_err = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
if theilSenBool == "true":
    theilSen_slope = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
    theilSen_loSlope = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
    theilSen_upSlope = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))

# Pixel Iteration
row_no = -1
for row in dataCount_rast:
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
        for i in range(len(inputRastDir)):   
            cell_list.append(int(stackNP[i][row_no][cell_no]))
            if int(stackNP[i][row_no][cell_no]) == noData:
                rem.append(int(i))

        # remove noData values
        rem.sort(reverse=True)  
        for j in range(len(rem)):
            remove = rem[j]
            del cell_list[remove]
            del x[remove]          
                
         # Linear Regression and count datapoints
        if len(cell_list) == 0 or len(cell_list) == 1:
            dataCount_rast[row_no][cell_no] = 0       
            if linRegBool == "true":   
                linReg_slope[row_no][cell_no] = noData
                linReg_pvalue[row_no][cell_no] = noData
                linReg_std_err[row_no][cell_no] = noData
            if theilSenBool == "true":
                theilSen_slope[row_no][cell_no] = noData
                theilSen_loSlope[row_no][cell_no] = noData
                theilSen_upSlope[row_no][cell_no] = noData
    
        else:
            dataCount_rast[row_no][cell_no] = len(cell_list)            
            if linRegBool == "true":   
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, cell_list)
                linReg_slope[row_no][cell_no] = slope
                linReg_pvalue[row_no][cell_no] = p_value
                linReg_std_err[row_no][cell_no] = std_err
            if theilSenBool == "true":
                medslope, medintercept, lo_slope, up_slope = stats.mstats.theilslopes(cell_list,x)           
                theilSen_slope[row_no][cell_no] = medslope
                theilSen_loSlope[row_no][cell_no] = lo_slope
                theilSen_upSlope[row_no][cell_no] = up_slope
                

## Output File creation
# Set Arc environment variables for output
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcRast(inputRastDir,1)
arcpy.env.cellSize = arcRast(inputRastDir,1)
lowerLeft = arcpy.Point(arcRast(inputRastDir,1).extent.XMin,arcRast(inputRastDir,1).extent.YMin)

# Output raster file names and locations
dataCountOut = os.path.join(outputFolder,r"dataCount.tif")
if linRegBool == "true": 
    linReg_slopeOut = os.path.join(outputFolder,r"linReg_slope.tif")
    linReg_pvalueOut = os.path.join(outputFolder,r"linReg_pvalue.tif")
    linReg_stderrOut = os.path.join(outputFolder,r"linReg_std_err.tif")
if theilSenBool == "true":
    theilSen_slopeOut = os.path.join(outputFolder,r"theilSen_slope.tif")
    theilSen_loSlopeOut = os.path.join(outputFolder,r"theilSen_loSlope.tif")
    theilSen_upSlopeOut = os.path.join(outputFolder,r"theilSen_upSlope.tif")    
    
# Save outpu files
output_r = arcpy.NumPyArrayToRaster(dataCount_rast,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
output_r.save(dataCountOut)
if linRegBool == "true":   
    output_r = arcpy.NumPyArrayToRaster(linReg_slope,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(linReg_slopeOut)
    output_r = arcpy.NumPyArrayToRaster(linReg_pvalue,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(linReg_pvalueOut)
    output_r = arcpy.NumPyArrayToRaster(linReg_std_err,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(linReg_stderrOut)
if theilSenBool == "true":
    output_r = arcpy.NumPyArrayToRaster(theilSen_slope,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(theilSen_slopeOut)
    output_r = arcpy.NumPyArrayToRaster(theilSen_loSlope,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(theilSen_loSlopeOut)
    output_r = arcpy.NumPyArrayToRaster(theilSen_upSlope,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
    output_r.save(theilSen_upSlopeOut)
     
    
"""
Future Dev
- irregular shape handling
- pixel clustering/aggregation of multi-size pixels
"""
