oDesktop.RestoreWindow()
oProject = oDesktop.SetActiveProject("Modified")
oDesign = oProject.SetActiveDesign("Design")
oModule = oDesign.GetModule("ReportSetup")
oModule.UpdateReports(["S11mag"])
oModule.ExportToFile("S11mag", "C:/Users/giannetti/Documents/HFSS-MATLAB_interface/Dev7/Python/NoVarExport/S11mag.csv")
oModule.UpdateReports(["S11pha"])
oModule.ExportToFile("S11pha", "C:/Users/giannetti/Documents/HFSS-MATLAB_interface/Dev7/Python/NoVarExport/S11pha.csv")
oModule.UpdateReports(["NearE"])
oModule.ExportToFile("NearE", "C:/Users/giannetti/Documents/HFSS-MATLAB_interface/Dev7/Python/NoVarExport/NearE.csv", False)
