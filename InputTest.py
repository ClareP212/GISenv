# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:49:41 2020

@author: Clare
"""
import arcpy

outputFolder = arcpy.GetParameterAsText(0)
inputRasters = arcpy.GetParameterAsText(1)
linRegBool = arcpy.GetParameterAsText(2)
theilSenBool = arcpy.GetParameterAsText(3)

arcpy.AddMessage (outputFolder)
arcpy.AddMessage (inputRasters)
arcpy.AddMessage (linRegBool)
arcpy.AddMessage (theilSenBool)


if linRegBool == "false"and theilSenBool == "false":
    print ("error")
    arcpy.AddMessage ("error")
    arcpy.AddError("No Trend method found. Please tick one of the boxes") 