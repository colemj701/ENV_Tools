import sys, os, arcpy
arcpy.SetProgressor("default","Initiating batch layout export tool...")

arcpy.env.overwriteOutput = True

# Script Parameters
folder_path = arcpy.GetParameterAsText(0) # target folder path to export layouts

Project = arcpy.GetParameterAsText(1) # aprx containing map series layouts

# Set mapping module project object
aprx = arcpy.mp.ArcGISProject(Project)

# list layouts in project
lyts = aprx.listLayouts()
for lyt in lyts:
    lyt_name = lyt.name # retrieve layout name

    # Check if lyt has map series enabled and print each map series page as jpeg
    if not lyt.mapSeries is None:
        ms = lyt.mapSeries # define ms as layout map series object
        if ms.enabled: #if enabled export map series
            for pageNum in range(1, ms.pageCount + 1): # iterate over pages based on page numbers in map series (page number cannot be assigned by field value for this to work)
                ms.currentPageNumber = pageNum # retrieve page number
                page_name = ms.pageRow.RoomNum # retrieve page name based on map series field's attribute value assigned during series setup
                arcpy.SetProgressorLabel('Exporting Map Series Page "{0}" to JPEG...'.format(f"{page_name}"))
                lyt.exportToJPEG(os.path.join(folder_path, f"{page_name}"),96, "24-BIT_TRUE_COLOR", 100, True, False) # export page as jpeg with page number as file name
                arcpy.SetProgressorPosition()