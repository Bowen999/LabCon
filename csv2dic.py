import pandas as pd
import numpy as np
import re
import json

"""
This script processes CSV files to extract and format chemical contaminant data at different voltage levels. 
It reads CSVs, cleans and formats data (handling missing values and newline characters), and converts peak data into structured lists. 
The results are saved as dictionaries in output_data.py under variable names based on file names (e.g., eppendorf, glassware).
The parse_list_string() function helps parse list strings into numerical lists.

此脚本处理CSV文件，提取并格式化不同电压下的化学污染物数据。
它读取CSV文件，清洗并格式化数据（处理缺失值和换行符），并将峰值数据转换为结构化列表。
结果以字典形式保存在output_data.py中，变量名基于文件名（如eppendorf，glassware）。
辅助函数parse_list_string()用于解析列表字符串为数值列表。
"""

def process_csv(file_path):
    # Load CSV using pandas
    df = pd.read_csv(file_path, skipinitialspace=True)

    # Replace NaN values in 'Structural Identity' with 'unknown Compound'
    df['Structural\nIdentity\n(if available)'].fillna('unknown Compound', inplace=True)
    
    # Replace '\n' in 'Structural Identity' with a space
    df['Structural\nIdentity\n(if available)'] = df['Structural\nIdentity\n(if available)'].str.replace('\n', ' ')

    # Prepare a list to store the output dictionaries
    output = []

    # Iterate over each row to build the structure
    for index, row in df.iterrows():
        for voltage in [20, 40, 60]:
            # Create dictionary for each voltage level
            entry = {
                'id': f"{row['id']}_{voltage}V",
                'Contaminant': row['id'],
                'precursor_mz': float(row['Contaminant m/z']),
                'Adduct': row['Ion adduct'],
                'Structural Identity': row['Structural\nIdentity\n(if available)'],
                'peaks': np.array(
                    parse_list_string(row[f"relative_{voltage}v"]),
                    dtype=np.float32
                ).tolist(),  # Convert numpy array to list for better formatting
                'absolute_peaks': np.array(
                    parse_list_string(row[f"{voltage}v"]),
                    dtype=np.float32
                ).tolist()  # Convert numpy array to list for better formatting
            }
            output.append(entry)
    return output

def parse_list_string(list_string):
    # Convert string representation of list to actual list of lists
    list_string = re.sub(r'\s+', '', list_string)  # Remove any unnecessary spaces or line breaks
    matches = re.findall(r'\[([-+]?\d*\.\d+|\d+),([-+]?\d*\.\d+|\d+)\]', list_string)
    return [[float(x), float(y)] for x, y in matches]

# Process and save data for different CSV files
file_paths = {'eppendorf_ref.csv': 'eppendorf', 'glass_ref.csv': 'glassware'}

for file_path, variable_name in file_paths.items():
    result = process_csv(file_path)

    # Save the result to a Python file
    with open('output_data.py', 'a') as f:
        f.write(f"{variable_name} = {json.dumps(result, indent=4)}\n\n")

# Print a message to indicate the data has been saved
print("The results have been saved to 'output_data.py' with appropriate variable names.")
