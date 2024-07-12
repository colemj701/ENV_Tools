import sys, os, arcpy
from datetime import datetime
arcpy.SetProgressor("default","Initiating batch layout export tool...")

arcpy.env.overwriteOutput = True

locations = arcpy.GetParameterAsText(0)
samples_fc = arcpy.GetParameterAsText(1)
output_GDB = arcpy.GetParameterAsText(2)
jpg_folder = arcpy.GetParameterAsText(3)
report_date = arcpy.GetParameterAsText(4)

default_gdb = arcpy.env.scratchGDB

date_str = arcpy.GetParameterAsText(5)
report_date_formatted = report_date.replace("/","")
# Define the date to filter by (in this case, July 25, 2023)
filter_date = datetime.strptime(date_str, '%m/%d/%Y %I:%M:%S %p')

# Define the field name containing the "sample date" values
sample_date_field = "SampleDate"  # Replace with the actual field name

# define feature layer variables and filter them based on filter date parameter
loc_fl = arcpy.MakeFeatureLayer_management(locations,"loc_fl_{0}".format(report_date_formatted),f"{sample_date_field} > date '{filter_date}'")
samfc_fl = arcpy.MakeFeatureLayer_management(samples_fc,"Sample_Join_{0}".format(report_date_formatted),f"{sample_date_field} > date '{filter_date}'")
samfc_fl1 = arcpy.MakeFeatureLayer_management(samples_fc,"samfc_fl_{0}".format(report_date_formatted),f"{sample_date_field} > date '{filter_date}'")

# Create Filterted Feature Layers and copy the interim data to the scratch GDB 
fl_list = [loc_fl,samfc_fl,samfc_fl1]
fl_count = len(fl_list)
arcpy.SetProgressor("step","Converting Feature Layers...",0,fl_count,1)
for fl in fl_list:
    fl1 = arcpy.Describe(fl)
    arcpy.SetProgressorLabel("Creating Interim Data {0}{1}{2}...".format(fl1.name,"_",report_date_formatted))
    arcpy.conversion.ExportFeatures(fl,os.path.join(default_gdb,fl1.name+"_"+report_date_formatted))
    arcpy.SetProgressorPosition()
arcpy.ResetProgressor()

arcpy.env.workspace = default_gdb

# Define join variables
join_field = "LocID"
join_field1 = "LocIDFK"
loc_fl1 = default_gdb+"\\Locations_{0}".format(report_date_formatted)
samfc_fl2 = default_gdb+"\\Samples_FC_{0}".format(report_date_formatted)
Join_FC = arcpy.management.JoinField(samfc_fl2,join_field1,loc_fl1,join_field)
sample_join = default_gdb+"\\Samples_FC_{0}".format(report_date_formatted)

# Execute the Locations-Samples_FC join and export derived data to the output gdb
fc_list1 = [samfc_fl2,loc_fl1,sample_join]
fc_count = len(fc_list1)
arcpy.SetProgressor("step","Exporting Derived Features...",0,fc_count,1)
for fc in fc_list1:
    fc1 = arcpy.Describe(fc)
    arcpy.SetProgressorLabel("Exporting {0}...".format(fc1.name))
    arcpy.CopyFeatures_management(fc,os.path.join(output_GDB,fc1.name))
    arcpy.SetProgressorPosition()
arcpy.ResetProgressor()

# Add and caluclate the jpeg image file path field to the joined table - required to run report with embedded images
sample_join1 = os.path.join(output_GDB,"Samples_FC_{}".format(report_date_formatted))
arcpy.SetProgressor("default","Finalizing Derived Features...")
arcpy.management.AddField(sample_join1,"img_file","TEXT","","",255,"JPEG Path","NULLABLE")

edit = arcpy.da.Editor(output_GDB)
edit.startEditing(False,True)
fields = ["RoomNum","img_file"]

# Update the row values of the img_file field based on the values of the RoomNum field 
with arcpy.da.UpdateCursor(sample_join1,fields) as cursor:
    for row in cursor:
        jpg = ".jpg"
        row[1] = os.path.join(jpg_folder,row[0]+jpg)
        cursor.updateRow(row)
        print(cursor)
edit.stopEditing(True)



