import arcpy, traceback, os, sys, time, datetime, string, numpy, math

# Eventually you'll have more funtions up here.
#----------------------------------------------------------------------


def myCoolFunctionToDoOneSimpleThing(arg1, arg2, etc):
    
    try:

        SomeCoolResult = arg1 + arg2
        
        #etc....
        
        
        
        return SomeCoolResult

    except arcpy.ExecuteError: 

        msgs = arcpy.GetMessages(2) 
        arcpy.AddError(msgs)

        return None

    except:

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        return None



"""
========================================================================
B2H Site Isolate Query
========================================================================
Author: Mitchell Fyock
========================================================================
Date			Modifier	Description of Change
12/01/2016		MF			Created
12/07/2016		MF			Inserted header, extended functionality to include writing output to .txt file
========================================================================
This script was developed to automate the time-intensive task of performing
numerous attribute and location queries on Site and Isolate datasets for the
Boardman to Hemmingway Project in order to obtain a count of the number of 
archaeological sites and isolates located within each county in the project
area.  The script also identifies and removes duplicate feature entries 
from the total (combined county) count in order to maintain accurate metrics.
The ouput of the script is shapefiles containing Unique IDs, a .dbf containing
the duplicate feature Unique IDs, and a .txt file which contains the different
count values.
"""

# Main Function, this is the entry point for the program
if __name__ == '__main__':

    try:

        sVersionInfo = "12-08-16"
        arcpy.AddMessage("myScriptNameHere.py, {0}".format(sVersionInfo))
        
        #Validate all of your inputs, repeat this pattern for all of 
        #your feature classes.
        
        #This pattern allows you to use hard coded paths for development
        #and allows you to hook up to a script tool for production.
        
        #========================================================================
        myFcPath = arcpy.GetParameterAsText(0)
        # 
        #
        #======================================================================== 
        if myFcPath == "":
            myFcPath = r"I:\projects\NepalLrt\db\clipDem10b"

        if not arcpy.Exists(myFcPath):
            arcpy.AddWarning("Can not find input myFc")
            sys.exit(0)
       
            
        #--------------------------------------------------------------------------
        # Validation and setup above this   
        #--------------------------------------------------------------------------
        # Do the main part of your work here
        #--------------------------------------------------------------------------
            
            
            
            
            
            
            
            
            
 
            
            
        #----------------------------------------------------------------------
        #Done
        #----------------------------------------------------------------------      
        sys.exit(0)

    except SystemExit, e:

        arcpy.AddMessage("OK")

    except arcpy.ExecuteError:
        msgs = arcpy.GetMessages(2)
        arcpy.AddError(msgs)

    except Exception as emsg:
        m = emsg.args
        arcpy.AddError(m)

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "arcpy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)


