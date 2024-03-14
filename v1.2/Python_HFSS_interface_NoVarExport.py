# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:52:03 2024

@author: giannetti
"""

import pandas as pd
import numpy as np
import re
import os
import subprocess
import matplotlib.pyplot as plt
import pdb # to debug the code
from datetime import datetime
from warnings import warn
# pdb.set_trace()

def signpost_substitution(filename_in, filename_out):
    # Find the variables
    with open(filename_in, 'r') as file:
        c = file.readlines()

    Names = []
    Variables = []
    ValueUnit = []
    for k in range(len(c)):
        if "VariableProp" in c[k]:
            name = c[k].split("VariableProp('")[1].split("', '")[0]
            help_c = c[k]
            if help_c[-3:-1] == "))":
                sub1 = "', '"
                sub2 = "', oa("
            else:
                sub1 = "', '"
                sub2 = "')"

            # getting index of substrings
            idx1 = c[k].index(sub1)
            idx2 = c[k].index(sub2)

            help_str = ''
            # getting elements in between
            for idxH in range(idx1 + len(sub1), idx2):
                help_str = help_str + c[k][idxH]
                
            ValueUnit = help_str[::-1].split("'", 1)[0][::-1]

            Names.append(name)
            Variables.append([name, ValueUnit])

    Value = []
    Unit = []
    for k in range(len(Variables)):
        Value.append(''.join(filter(lambda i: filter_function(i), Variables[k][1])))
        Unit.append(''.join(filter(lambda i: i.isalpha() or i == "_", Variables[k][1])))
    
    a = np.array([Names, Value, Unit])
    variables = pd.DataFrame(a.T, columns=['Name', 'Value', 'Unit'])
    
    # pdb.set_trace()
    
    UnitList = ['', 'mm', 'V', 'W', 'deg', 'S_per_m'] # List of units
    variables = variables[variables['Unit'].isin(UnitList)]

    # Remove dependent variables
    variables['Value'] = pd.to_numeric(variables['Value'],errors='coerce')
    var2sub = variables.dropna(axis=0)
    var2sub = var2sub.reset_index(drop=True)

    nvar, _ = var2sub.shape # Number of variables to substitute
    signpost_list = generate_signposts(nvar)
    
    var2sub = pd.concat([var2sub, pd.Series(signpost_list, name='Signpost')], axis=1)

    with open(filename_in, 'r') as file:
        c = file.readlines()

    for k in range(len(c)):
        if "VariableProp" in c[k]:
            for idx in range(nvar):
                actual_var = c[k].split("VariableProp('")[1].split("', '")[0]
                if actual_var == var2sub.iloc[idx, 0]:
                    help_c = c[k]
                    if help_c[-3:-1] == "))":
                        sub1 = "', '"
                        sub2 = "', oa("
                    else:
                        sub1 = "', '"
                        sub2 = "')"

                    # getting index of substrings
                    idx1 = c[k].index(sub1)
                    idx2 = c[k].index(sub2)

                    help_str = ''
                    # getting elements in between
                    for idxH in range(idx1 + len(sub1), idx2):
                        help_str = help_str + c[k][idxH]

                    value_unit = help_str[::-1].split("'", 1)[0][::-1] # [::-1] means reverse
                    unit = str(var2sub.iloc[idx, 2])
                    if unit == "":
                        value = value_unit
                    else:
                        value = value_unit.replace(unit, "")

                    c[k] = c[k].replace(f"'{value}{unit}'", f"'{signpost_list[idx]}{unit}'")

    with open(filename_out, 'w') as file:
        file.writelines(c)
        
    return var2sub

def filter_function(x):
    
    if x.isdigit():
        return True
    elif x in ['+', '-', '.']:
        return True
    else:
        return False

def generate_signposts(nvar):
    numbers = list(map(str, range(10)))
    words = ["A", "B", "C", "D", "E", "F", "G", "H", "L", "M"]
    nwords = len(words)

    signposts = []

    for idx in range(nvar):
        idx_numbers = idx // nwords
        idx_words = idx % nwords
        signposts.append(f"{numbers[idx_numbers]}{words[idx_words]}{numbers[idx_numbers]}{words[idx_words]}")

    return signposts


def import_file(filename, data_lines=None):
    if data_lines is None:
        data_lines = [2, np.inf]

    # Set up the Import Options and import the data
    optsH = pd.read_csv(filename, sep='\t')
    opts = optsH.replace(np.nan, '', regex=True)
    return opts

def path_and_file():
    main_path = "C:\\Users\\giannetti\\Documents\\CavityFilter\\DualBand\\API_Python\\"
    hfss_path = 'C:\\"Program Files\\AnsysEM\\v241\\Win64\\ansysedt.exe"'
    hfss_file_filename = "Modified.aedt"
    model_name = "Design"
    hfss_script_filename = "ExportToFile_Sparam.py"
    hfss_output_filename = ["S11mag", "S11pha", "Gd"]
    hfss_output_notes = ["", "", ""]
    # filename_in_start_filename = "BaseNoSignposts.txt"
    filename_in_start_filename = "Base.aedt" 
    filename_in_filename = "Base.txt"
    filename_out_filename = hfss_file_filename

    str_batch_solve = " /Ng /BatchSolve "
    str_batch_extract = " /Ng /BatchExtract "

    hfss_file = os.path.join(main_path, hfss_file_filename)
    hfss_script = os.path.join(main_path, hfss_script_filename + " ")
    hfss_output = []
    for idx in range(len(hfss_output_filename)):
        hfss_output.append(os.path.join(main_path, hfss_output_filename[idx]))
      
    filename_in = os.path.join(main_path, filename_in_filename)
    filename_out = os.path.join(main_path, filename_out_filename)
    filename_log = os.path.join(main_path, hfss_file_filename + ".batchinfo\\",
                                hfss_file_filename.replace("aedt", "log"))
    cmd_hfss_sim = f"{hfss_path}{str_batch_solve}{hfss_file}"
    cmd_hfss_res = f"{hfss_path}{str_batch_extract}{hfss_script}{hfss_file}"

    return {
        "main_path": main_path,
        "hfss_path": hfss_path,
        "hfss_file_filename": hfss_file_filename,
        "model_name": model_name,
        "hfss_script_filename": hfss_script_filename,
        "hfss_output_filename": hfss_output_filename,
        "hfss_output_notes": hfss_output_notes,
        "filename_in_start_filename": filename_in_start_filename,
        "filename_in_filename": filename_in_filename,
        "filename_out_filename": filename_out_filename,
        "str_batch_solve": str_batch_solve,
        "str_batch_extract": str_batch_extract,
        "hfss_file": hfss_file,
        "hfss_script": hfss_script,
        "hfss_output": hfss_output,
        "filename_in": filename_in,
        "filename_out": filename_out,
        "filename_log": filename_log,
        "cmd_hfss_sim": cmd_hfss_sim,
        "cmd_hfss_res": cmd_hfss_res
    }


def parameter_update(sx, filename_in, filename_out, paf):
    with open(filename_in, 'r') as file:
        c = file.readlines()

    signpost_list = paf["signpost_list"]

    for k in range(len(c)):
        for idx in range(len(sx)):
            c[k] = c[k].replace(signpost_list[idx], f"{sx[idx]:.14f}")

    with open(filename_out, 'w') as file:
        file.writelines(c)


def sim_hfss_matlab(x, paf):
    
    hfss_file = paf["hfss_file"]
    hfss_output = paf["hfss_output"]
    filename_log = paf["filename_log"]
    filename_in = paf["filename_in"]
    filename_out = hfss_file
    cmd_hfss_sim = paf["cmd_hfss_sim"]
    cmd_hfss_res = paf["cmd_hfss_res"]

    parameter_update(x, filename_in, filename_out, paf)
    # pdb.set_trace()
    subprocess.run(cmd_hfss_sim.replace('\\', '/'), shell=True)

    with open(filename_log, 'r') as file:
        c = file.readlines()

    idx = 1
    while c[-1].strip() == "[Exiting application]":
        t = datetime.now()
        time_now = t.strftime('%Y-%m-%d %H:%M:%S')
        warn(f"HFSS is not working properly and stopped at {time_now}")

        idx += 1
        if idx > 10:
            break

        subprocess.run(f'del "{hfss_file}.lock"', shell=True)
        subprocess.run(cmd_hfss_sim, shell=True)

        with open(filename_log, 'r') as file:
            c = file.readlines()

    # pdb.set_trace()
    subprocess.run(cmd_hfss_res.replace('\\', '/'), shell=True)
    return results(hfss_output)


def results(hfss_output):
    
    nout = len(hfss_output)
    t = [pd.read_csv(f"{o}.csv", header=None, skiprows=1) for o in hfss_output]
    return t


def writing_export_file(paf):
    n = len(paf["hfss_output_filename"])

    with open(os.path.join(paf["main_path"], paf["hfss_script_filename"]), 'w') as file:
        file.write('oDesktop.RestoreWindow()\n')
        file.write(f'oProject = oDesktop.SetActiveProject("{paf["hfss_file_filename"].replace(".aedt", "")}")\n')
        file.write(f'oDesign = oProject.SetActiveDesign("{paf["model_name"]}")\n')
        file.write('oModule = oDesign.GetModule("ReportSetup")\n')

        for idx in range(n):
            file.write(f'oModule.UpdateReports(["{paf["hfss_output_filename"][idx]}"])\n')
            file.write('oModule.ExportToFile("%s", "%s%s.csv"%s)\r\n' % (paf["hfss_output_filename"][idx], paf["main_path"].replace("\\", "/"), paf["hfss_output_filename"][idx], paf['hfss_output_notes'][idx]))

# Preamble
PAF = path_and_file()
writing_export_file(PAF)

var2sub = signpost_substitution(PAF["filename_in_start_filename"], PAF["filename_in_filename"])

PAF["signpost_list"] = var2sub.iloc[:, 3]

x = var2sub.iloc[:, 1]

# Optimum values
x[var2sub.iloc[:, 0] == "a"] = 50

# pdb.set_trace()

output1 = sim_hfss_matlab(x, PAF)

Data_type = object
output = [output1]
outputTot = np.array(output, dtype=Data_type)
np.save("ResultOutput.npy", outputTot)

# Figures
outputLoad = np.load("ResultOutput.npy", allow_pickle=True)

fig1, ax1 = plt.subplots()
ax1.plot(outputLoad[0][0][:,0], outputLoad[0][0][:,1], label="magnitude")
ax1.legend(loc="lower right")
ax1.grid()
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("S11 Magnitude (dB)")

fig2, ax2 = plt.subplots()
ax2.plot(outputLoad[0][2][:,0], outputLoad[0][2][:,1], label="Group delay")
ax2.legend(loc="lower right")
ax2.grid()
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Group delay (ns)")

plt.show()