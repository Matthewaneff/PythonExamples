import arcpy, traceback, os, sys, time, datetime, string, xlwt

nFc = 0
nFcWithAttach = 0
nFcNoAttach = 0

nAttachments = 0

logfPath = ""


#----------------------------------------------------------------------
def writeToLog(s, isVerbose, n):
    
    #Trap for cases where s is a tuple or list object.
    
    try:
        
        sPad = ""
        
        for i in range(n):
            sPad += " "
            
        txt = sPad + s
        
    except:
        
        txt = s
        
    try:
        
        if isVerbose:
            arcpy.AddMessage(txt)

        #Trap for errors that appear before
        #the logfile has been setup.
        if logfPath != "":          
            logf = open(logfPath, "a")
            logf.write(str(txt) + "\n")
            logf.close()

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        arcpy.AddMessage(pymsg)

#=====================================================================================
def checkFieldExists(pFieldSrc, sField):

    try:

        flist = []
        srcfieldList = arcpy.ListFields(pFieldSrc)

        sFoundField = 'FALSE'
  
        for f in srcfieldList:
            s = str(f.name)
            s = s.upper()
            flist.append(s)

        if sField.upper() in flist:
            sFoundField = 'TRUE'

        return sFoundField

    except arcpy.ExecuteError: 

        msgs = arcpy.GetMessages(2) 

    except:

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        pymsg = tbinfo + ", " + str(sys.exc_info()[1])
        msgs = pymsg + ", " + arcpy.GetMessages(2)

        writeToLog("WARNING Error checking for existence of field {0} in {1} error: {2} ".format(sField, desc.baseName, msgs), True, 3)
        return 'ERROR'

#=====================================================================================
def exportAttachments(bOverwrite, nObjectId, sId, sGuid, sTargetFolder, sAttachTable, ws2, stylb, nRow):

    try:
        global nFcNoAttach, nFcWithAttach, nAttachments
        
        sql_exp = """{0} = '{1}'""".format( arcpy.AddFieldDelimiters(sAttachTable, 'REL_GLOBALID'), sGuid)
        
        try:
            arcpy.Delete_management("xxMyVu")
        except:
            pass
            
        arcpy.MakeTableView_management(sAttachTable, "xxMyVu", sql_exp)
        nRecs = int(arcpy.GetCount_management("xxMyVu").getOutput(0))
        
        if nRecs <= 0:
            writeToLog("No Attachments", True, 5)
            nFcNoAttach =  nFcNoAttach + 1
            return nRow
        
        nFcWithAttach = nFcWithAttach + 1
        
        sOutFolder = sTargetFolder + os.sep + sId
        if not os.path.exists(sOutFolder):
            os.mkdir(sOutFolder)
        
        
        #Here we search the attachments table based on the GlobalID == REL_GLOBALID
        with arcpy.da.SearchCursor(sAttachTable, ['DATA', 'ATT_NAME'], where_clause = sql_exp) as cursor:

            n = 0
            
            for item in cursor:
                
                n = n+1
                nAttachments = nAttachments + 1

                attachment = item[0]
                filename = sId + "_" +str(item[1])

                sOutPath = sOutFolder + os.sep + filename
                
                if os.path.exists(sOutPath):
                    
                    if bOverwrite == True:
                        os.remove(sOutPath)
                        open(sOutPath, 'wb').write(attachment.tobytes())
                        writeToLog('{0} of {1} File {2} overwritten'.format(n, nRecs, filename), True, 5)

                    else:
                        writeToLog('{0} of {1} File {2} already exists and overwrite is false'.format(n, nRecs, filename), True, 5)
                        
                else:
                    writeToLog('{0} of {1} File {2}'.format(n, nRecs, filename), True, 5)
                    open(sOutPath, 'wb').write(attachment.tobytes())
                    
                ws2.write(nRow,0,nObjectId, stylb)
                ws2.write(nRow,1,sId, stylb)
                ws2.write(nRow,2,sOutPath, stylb)
                
                del item
                del attachment
                
                #Increment XCEL Row
                nRow = nRow + 1
                
        return nRow
    
    except arcpy.ExecuteError: 

        msgs = arcpy.GetMessages(2) 

    except:

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        pymsg = tbinfo + ", " + str(sys.exc_info()[1])
        msgs = pymsg + ", " + arcpy.GetMessages(2)

        writeToLog("Error: {0} ".format(msgs), True, 5)
        return -1


#================================================================================
# BEGIN HERE
#================================================================================
# DPlume
#===============================================================================
# 10/15/2015 Created
#
#================================================================================
if __name__ == '__main__':

    try:

        sVersionInfo = "cutler_ExtractFcAttachToFolder.py, v20151019 1600"
        arcpy.AddMessage("Extract Photos, {0}".format(sVersionInfo))
        
        #========================================================================
        sPhotosFcPath = arcpy.GetParameterAsText(0)
        #======================================================================== 
        if sPhotosFcPath == "":
            sPhotosFcPath = r"I:\projects\CutlerAvianFatality\db\cutlerDb.gdb\Fatality_Point"
  
        #========================================================================
        sTargetPath = arcpy.GetParameterAsText(1) 
        #========================================================================

        if sTargetPath == "":
            sTargetPath = r"I:\projects\CutlerAvianFatality\testOutput" 
   
        #========================================================================
        pField = arcpy.GetParameter(2) 
        #========================================================================

        if pField == None:
            sIdFieldName = "PHOTO_ID"
        else:
            sIdFieldName = arcpy.GetParameterAsText(2)

        #========================================================================
        sUserComment = arcpy.GetParameterAsText(3) 
        #========================================================================

        #if sUserComment == "":
            #sUserComment = "No comment"
            

        #========================================================================
        # Overwrite
        # 
        bOverwrite = arcpy.GetParameter(4)
        
        if bOverwrite == None:
            bOverwrite = True

        if not arcpy.Exists(sPhotosFcPath):
            arcpy.AddWarning("Can not find Photos Feature Class")
            sys.exit(0)
         
        if not arcpy.Exists(sTargetPath):
            arcpy.AddWarning("Can not find target folder")
            sys.exit(0)
            
        sFieldExists = checkFieldExists(sPhotosFcPath, sIdFieldName)
        
        if sFieldExists != 'TRUE': 
            arcpy.AddWarning("Can not find Id Field in Photos FC")
            sys.exit(0)
            
        sFieldExists = checkFieldExists(sPhotosFcPath, 'GlobalID' )
        
        if sFieldExists != 'TRUE': 
            arcpy.AddWarning("Can not find Atttachments GlobalID Field in Photos FC")
            sys.exit(0)
            
        desc = arcpy.Describe(sPhotosFcPath)
        
        sPhotosFcBaseName = desc.baseName
        sPhotosFcCatPath = desc.catalogPath
        sPhotosFcPath  = desc.Path
        
        arcpy.env.workspace = sPhotosFcPath
        sAttachTable = sPhotosFcBaseName + '__ATTACH'

        if not arcpy.Exists(sAttachTable):
            arcpy.AddWarning("Can not find attachment table")
            sys.exit(0)

        d = datetime.datetime.now()
        sDate = d.strftime("%Y%m%d") 
        
        nowTime = time.localtime(time.time())
        
        #=================================================================================
        #create a log
        
        logbaseName = "ExtractPhotos_" + time.strftime("%Y%m%d_%H%M", nowTime) 
        logfPath = os.path.join(sTargetPath, logbaseName + ".txt")
        xlPath = os.path.join(sTargetPath, logbaseName + ".xls")
    
        writeToLog("", True, 0)
        writeToLog("===================================================================", True, 0)
        writeToLog(time.strftime("%Y%m%d_%H%M", nowTime), True, 0)
        writeToLog("Extract Photos, {0}".format(sVersionInfo),True,0)
        writeToLog("Support: david.plume@tetratech.com, 303-437-7977",True,0)
        writeToLog("", True, 0)
        writeToLog("Photo ID Field:  {0}".format(sIdFieldName),True,0)
        
        if bOverwrite == True:
            writeToLog("Overwrite: TRUE",True,0)
        else:
            writeToLog("Overwrite: FALSE",True,0)
            
        writeToLog("Output Folder: {0}".format(sTargetPath),True,0)
        writeToLog("Logfile:  {0}".format(logbaseName + ".txt"),True,0)
        writeToLog("ExcelFile:  {0}".format(logbaseName + ".xls"),True,0)
        writeToLog("", True, 0)
        writeToLog("===================================================================", True, 0)
        writeToLog("", True, 0)

        
        #=================================================================================
        #Create the Workbook to hold the name and photo path
        
        fontb = xlwt.Font()
        fontb.name = 'Arial'
        fontb.colour_index = 0
        fontb.bold = True

        stylb = xlwt.XFStyle()
        stylb.font = fontb

        fontn = xlwt.Font()
        fontn.name = 'Arial'
        fontn.colour_index = 0
        fontn.bold = False

        styln = xlwt.XFStyle()
        styln.font = fontn

        styld = xlwt.XFStyle()
        styld.num_format_str = 'm/d/YYYY H:M:S'

        wb = xlwt.Workbook()
        ws = wb.add_sheet(sPhotosFcBaseName)
        ws.write(1,1,sPhotosFcCatPath,stylb)
        ws.write(2,1,"Photo ID Field:  {0}".format(sIdFieldName),stylb)
        ws.write(3,1,"User Comment:  {0}".format(sUserComment),stylb)
        ws.write(4,1,datetime.datetime.now(),styld)
        
        ws2 = wb.add_sheet("PhotoPaths")
        ws2.write(0,0,"FcOID", stylb)
        ws2.write(0,1,"Photo ID", stylb)
        ws2.write(0,2,"Path",stylb)

        nRow = 1
 
        
        #=================================================================================
        #Search the feature class that has the attachments.
        oid_fieldname = desc.OIDFieldName
        
        with arcpy.da.SearchCursor(sPhotosFcBaseName, [oid_fieldname, sIdFieldName, 'GlobalID'] ) as rows:
        
            for row in rows:
                
                nFc = nFc + 1
                
                writeToLog('{0}, {1}'.format(row[0], row[1]),True,0)
                
                #Excel Row gets incremented in the exportAttachments Function
                nRow = exportAttachments(bOverwrite, row[0], row[1], row[2], sTargetPath, sAttachTable, ws2, stylb, nRow)
                
                #If nRow < 0 then stop because there was an error in the exportAttachments function
                if nRow < 0:
                    break
               
        writeToLog("{0} feature classes, {1} with attachments, {2} w/o attachments, {3} attachments".format(nFc, nFcWithAttach, nFcNoAttach, nAttachments),True,0)
        wb.save(xlPath)
        
        del ws
        del ws2
        del wb
        
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




