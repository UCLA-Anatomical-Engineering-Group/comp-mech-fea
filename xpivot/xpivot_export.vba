Dim swApp As Object
Dim swModel As Object
Dim swEqnMgr As Object
Dim boolstatus As Boolean
Dim CWAddinCallBackObj As Object

Sub main()

'Initialize Modules
Set swApp = Application.SldWorks
Set swModel = swApp.ActiveDoc
Set swEquationMgr = swModel.GetEquationMgr
Set CWAddinCallBackObj = swApp.GetAddInObject("CosmosWorks.CosmosWorks")

Dim swFeat As SldWorks.Feature
Dim swSketch As SldWorks.Sketch
Dim swSketchPoint As SldWorks.SketchPoint
Dim sketchPointArray As Variant

' Rebuild Model
boolstatus = swModel.EditRebuild3()

'Get Current Time
Dim currentTime As Date
currentTime = Now

'Get Current Date
Dim currentDate As Date
currentDate = Date

' Step file export folder (enter your path)
address = "$$$"

' Generate export address for step and txt files
ModelName = "$$$"
stepFileName = address & "steps\" & ModelName & ".step"
paramFileName = address & "params\" & ModelName & ".txt"

' Export step file
longstatus = swModel.SaveAs3(stepFileName, 0, 2)

' Initialize print to file
Dim fileNo As Integer
fileNo = FreeFile
Open paramFileName For Output As #fileNo

' ## Print model name
Print #fileNo, "# ModelName: " & ModelName & ".step"

' ## Print current date and time
Print #fileNo, "# Model Export Time: " & Format(currentDate, "yyyy/mm/dd ") & Format(currentTime, "hh:mm:ss AM/PM")
Print #fileNo, ""

' ## Print input parameters (those in Equations mgr)
Print #fileNo, "######## Design Parameters ########"
Print #fileNo, ""

Dim i As Integer
Dim equation As String

' Scan the Equations mgr
For i = 0 To swEquationMgr.GetCount - 1
    equation = swEquationMgr.equation(i)
    
    ' Clean the format for Python execution
    If InStr(equation, "@") = 0 Then ' Skip equations for dimensions/features
       
        ' Remove double quotes for variable name
        processedEquation = Replace(equation, """", "")
        
        'Remove comment
        commentStart = InStr(processedEquation, "'")
        If commentStart > 0 Then
            processedEquation = Left(processedEquation, commentStart - 1)
        End If

        ' Trim any extra spaces
        processedEquation = Trim(processedEquation)

        ' Print the processed equation
        Print #fileNo, processedEquation
    End If
Next i

' ##### Print measurement coordinates ######
Print #fileNo, ""
Print #fileNo, "######## Measurements ########"
Print #fileNo, ""

' ##### Call the sub ######
Call get_point_XYZ("FACE_LOAD", swModel, fileNo, 0)
Call get_point_XYZ("FACE_GND", swModel, fileNo, 0)
Call get_point_XYZ("FACE_INNER_CYLINDER", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_OUTER1_FILLET1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_FILLET2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_FILLET3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_FILLET4", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_OUTER1_TAPER1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_TAPER2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_TAPER3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER1_TAPER4", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_OUTER2_FILLET1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_FILLET2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_FILLET3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_FILLET4", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_OUTER2_TAPER1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_TAPER2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_TAPER3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_OUTER2_TAPER4", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_INNER_FILLET1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_FILLET2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_FILLET3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_FILLET4", swModel, fileNo, 0)

Call get_point_XYZ("IGNORE_INNER_TAPER1", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_TAPER2", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_TAPER3", swModel, fileNo, 0)
Call get_point_XYZ("IGNORE_INNER_TAPER4", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER12", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER13", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER14", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER22", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER23", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_OUTER24", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_CENTER_PARTIAL_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_CENTER_PARTIAL_INNER4", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER12", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER13", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER14", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER22", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER23", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_OUTER24", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_UPPER_PARTIAL_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_UPPER_PARTIAL_INNER4", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER12", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER13", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER14", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER22", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER23", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_OUTER24", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_LOWER_PARTIAL_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_LOWER_PARTIAL_INNER4", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_FULL_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER12", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER13", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER14", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_FULL_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER22", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER23", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_OUTER24", swModel, fileNo, 0)

Call get_point_XYZ("LENGTH_FULL_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("LENGTH_FULL_INNER4", swModel, fileNo, 0)

Call get_point_XYZ("WIDTH_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER12", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER13", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER14", swModel, fileNo, 0)

Call get_point_XYZ("WIDTH_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER22", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER23", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_OUTER24", swModel, fileNo, 0)

Call get_point_XYZ("WIDTH_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("WIDTH_INNER4", swModel, fileNo, 0)

Call get_point_XYZ("THICKNESS_OUTER11", swModel, fileNo, 0)
Call get_point_XYZ("THICKNESS_OUTER12", swModel, fileNo, 0)

Call get_point_XYZ("THICKNESS_OUTER21", swModel, fileNo, 0)
Call get_point_XYZ("THICKNESS_OUTER22", swModel, fileNo, 0)

Call get_point_XYZ("THICKNESS_INNER1", swModel, fileNo, 0)
Call get_point_XYZ("THICKNESS_INNER2", swModel, fileNo, 0)
Call get_point_XYZ("THICKNESS_INNER3", swModel, fileNo, 0)
Call get_point_XYZ("THICKNESS_INNER4", swModel, fileNo, 0)

'Close Modules
Close #fileNo
Set CWAddinCallBackObj = Nothing
End Sub

'Get and print the XYZ coordinates of a 3D point
Sub get_point_XYZ(point_name As String, Model As Object, fileNo As Integer, pointNo As Integer)
    ' pointNo is the nth point you want to print in the 3d sketch, 0 is the first one. You have only one point to print from one sketch
    Dim swSketch As SldWorks.Sketch
    Dim swSketchPoint As SldWorks.SketchPoint
    Set swSketch = Model.FeatureByName(point_name).GetSpecificFeature2
    Set swSketchPoint = swSketch.GetSketchPoints2(pointNo)
    Print #fileNo, point_name & "_X = " & swSketchPoint.X * 1000 ' print in mm
    Print #fileNo, point_name & "_Y = " & swSketchPoint.Y * 1000 ' print in mm
    Print #fileNo, point_name & "_Z = " & swSketchPoint.Z * 1000 ' print in mm
    Print #fileNo, ""
End Sub


