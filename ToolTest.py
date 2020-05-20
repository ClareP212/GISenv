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
inputRasters = ['C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2010.tif 2010',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2011.tif 2011',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2012.tif 2012',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2013.tif 2013',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2014.tif 2014',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2015.tif 2015',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2016.tif 2016',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2017.tif 2017',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2018.tif 2018',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2019.tif 2019',
                'C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0\\MOD_an\\2020.tif 2020']
outputFolder = "C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0"

arcpy.env.workspace = "C:\\Users\\Clare\\Documents\\ArcGIS_uni\\GISenv\\0"
arcpy.env.overwriteOutput = True

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
arcpy.CompositeBands_management(inputRastDir,"stack.tif") #.tif extension broke this in ArcPro?
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
#arcpy.AddMessage ((arcRast(inputRasters,1).height,arcRast(inputRasters,1).width))
slope_rast = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
dataCount_rast = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
pvalue_rast = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))
std_err_rast = np.zeros((arcRast(inputRastDir,1).height,arcRast(inputRastDir,1).width))


#Iteration
row_no = -1
for row in slope_rast:
    row_no = row_no +1
    if row_no%100 == 0:
        print('Row number processed: ' + str(row_no))
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
        if len(cell_list) == 0:
            #arcpy.AddMessage (row_no)
            #arcpy.AddMessage (cell_no)
            slope_rast[row_no][cell_no] = noData
            dataCount_rast[row_no][cell_no] = 0
            pvalue_rast[row_no][cell_no] = noData
        else:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, cell_list)
            medslope, medintercept, lo_slope, up_slope = stats.mstats.theilslopes(cell_list,x,0.95)
            slope_rast[row_no][cell_no] = slope
            pvalue_rast[row_no][cell_no] = p_value
            std_err_rast[row_no][cell_no] = std_err
            dataCount_rast[row_no][cell_no] = len(cell_list)

## Output File creation
# Set Arc environment variables for output
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcRast(inputRastDir,1)
arcpy.env.cellSize = arcRast(inputRastDir,1)
lowerLeft = arcpy.Point(arcRast(inputRastDir,1).extent.XMin,arcRast(inputRastDir,1).extent.YMin)

# Output raster file names and locations
slopeOut = os.path.join(outputFolder,r"slope.tif")
dataCountOut = os.path.join(outputFolder,r"dataCount.tif")
pvalueOut = os.path.join(outputFolder,r"pvalue.tif")

#  (bands, rows, columns)
# change yvalue for band number - i.e. image number
output_r = arcpy.NumPyArrayToRaster(slope_rast,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
output_r.save(slopeOut)
output_r = arcpy.NumPyArrayToRaster(dataCount_rast,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
output_r.save(dataCountOut)
output_r = arcpy.NumPyArrayToRaster(pvalue_rast,lowerLeft, arcRast(inputRastDir,1).meanCellWidth, arcRast(inputRastDir,1).meanCellHeight,noData)
output_r.save(pvalueOut)

        
"""
Error Handling
arcpy.AddError(“No ArcMap Documents found. Please check your input \    variables.”) 

IDEAS
- ## raster size test
- irregular shape handling
- if no data the same
"""