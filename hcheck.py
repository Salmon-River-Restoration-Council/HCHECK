#!/usr/bin/env python3
# Import necessary libraries
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QProgressBar, QVBoxLayout, QLabel, QDialog, QInputDialog
import os
import pandas as pd
import openpyxl

__version__ = '0.5.15'

# Create a QApplication instance for the GUI elements
app = QApplication([])

# Get user input for top and bottom check range, and anomaly thresholds
checkTopRange, ok = QInputDialog.getInt(None, "Input", "Enter top check range:", value=400, min=0)
checkBottomRange, ok = QInputDialog.getInt(None, "Input", "Enter bottom check range:", value=7000, min=0)
anom, ok = QInputDialog.getDouble(None, "Input", "Enter anomaly threshold for _w_ files:", value=0.8, min=0)
anom_a, ok = QInputDialog.getDouble(None, "Input", "Enter anomaly threshold for _a_ files:", value=4, min=0)

# Initialize an empty list to store output data
output = []

# Get directory from user where the CSV files are located
directory = QFileDialog.getExistingDirectory(None, "Select Directory")

# Get all CSV files in the directory that are to be processed
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.csv')]

# Ask user if they want to add headers to the processed files, output both, or neither
msg = QMessageBox()
msg.setWindowTitle("Add Headers")
msg.setText("Do you want to add mock headers, output both, or neither?")
msg.addButton('Yes', QMessageBox.YesRole)  # Option to add headers
msg.addButton('No', QMessageBox.NoRole)    # Option to not add headers
msg.addButton('Both', QMessageBox.AcceptRole)  # Option to output both
add_headers = msg.exec_()

# Create new directories based on user's choice about headers
processed_dir = os.path.join(directory, 'processed_hobo_excels')
processed_headerless_dir = os.path.join(directory, 'processed_hobo_excels_headerless')

# Create the processed directories if they don't exist
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
if not os.path.exists(processed_headerless_dir):
    os.makedirs(processed_headerless_dir)

# Create a progress dialog to show the processing progress
progressDialog = QDialog()
progressDialog.setWindowTitle("Processing Files")
progressDialog.setFixedSize(400, 100)
layout = QVBoxLayout()
label = QLabel()
progressBar = QProgressBar()
layout.addWidget(label)
layout.addWidget(progressBar)
progressDialog.setLayout(layout)
progressDialog.show()

# Process each file for temperature anomalies
for index, filepath in enumerate(files):
    label.setText(f"Processing {filepath}...")
    progressBar.setValue(int((index / len(files)) * 100))
    QApplication.processEvents()

    # Determine anomaly threshold based on file type (either _w_ or _a_)
    if '_w_' in filepath:
        anomaly_threshold = anom
    elif '_a_' in filepath:
        anomaly_threshold = anom_a
    else:
        # If the file type is not clear, ask the user how to process it
        msg = QMessageBox()
        msg.setWindowTitle("File Type")
        msg.setText(f"Should {filepath} be processed as _a_ or _w_?")
        msg.addButton('_w_', QMessageBox.YesRole)
        msg.addButton('_a_', QMessageBox.NoRole)
        result = msg.exec_()
        anomaly_threshold = anom if result == 0 else anom_a

    # Load the CSV file into a DataFrame, skipping the first row (usually metadata)
    df = pd.read_csv(os.path.join(directory, filepath), skiprows=1)
    # Drop the first column (usually index) and keep only the first three columns (Date, Time, Temperature)
    df = df.drop(df.columns[0], axis=1)
    df = df.iloc[:, :3]
    # Add a new column for flagging data
    df[3] = ''

    # Check for anomalies in the top range (early rows of the dataset)
    for i in range(checkTopRange, -1, -1):
        if abs(df.iloc[i+1, 2] - df.iloc[i, 2]) >= anomaly_threshold:
            df.loc[:i+1, 3] = 'n'
            output.append([filepath, f'D1-D{i+1}'])
            break

    # Check for anomalies in the bottom range (later rows of the dataset)
    for i in range(checkBottomRange, df.shape[0]):
        if abs(df.iloc[i-1, 2] - df.iloc[i, 2]) >= anomaly_threshold:
            df.loc[i:, 3] = 'n'
            output.append([filepath, f'D{i}-D{df.shape[0]}'])
            break

    # Convert date column to datetime and format it to MM/DD/YYYY
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0].astype('object')).dt.strftime('%m/%d/%Y')

    # Save the DataFrame to an Excel file in the appropriate directory based on user's choice
    for header_option in [0, 1] if add_headers == 2 else [add_headers]:
        # Determine the directory to save files in
        save_dir = processed_dir if header_option == 0 else processed_headerless_dir
        # Determine if headers should be added
        include_headers = header_option == 0

        # Add headers if user chose to
        if include_headers:
            # Insert headers at the top of the DataFrame
            df_with_headers = df.copy()
            df_with_headers.loc[-1] = ['Date', 'Time, GMT-07:00', 'Temp, °C', 'flagged data']
            df_with_headers.index = df_with_headers.index + 1
            df_with_headers = df_with_headers.sort_index()
            # Insert a title row for the plot
            df_with_headers.loc[-1] = ['Plot Title: '+filepath[:-4], '', '', '']
            df_with_headers.index = df_with_headers.index + 1
            df_with_headers = df_with_headers.sort_index()

            # Save the DataFrame with headers
            with pd.ExcelWriter(os.path.join(save_dir, filepath[:-4] + '.xlsx'), date_format='MM/DD/YYYY', datetime_format='MM/DD/YYYY') as writer:
                df_with_headers.to_excel(writer, index=False, header=None, sheet_name=filepath[:-4])

        # Save the DataFrame without headers
        if not include_headers or add_headers == 2:
            with pd.ExcelWriter(os.path.join(save_dir, filepath[:-4] + '_headerless.xlsx'), date_format='MM/DD/YYYY', datetime_format='MM/DD/YYYY') as writer:
                df.to_excel(writer, index=False, header=None, sheet_name=filepath[:-4])

# Update progress dialog to indicate completion
label.setText("All files processed.")
progressBar.setValue(100)
QApplication.processEvents()

# Convert output list to DataFrame for reporting
output_df = pd.DataFrame(output, columns=['Filename', 'Range'])

# Ask user if they want to generate an output file summarizing the anomalies found
msg = QMessageBox()
msg.setWindowTitle("Generate Output")
msg.setText("Do you want to generate an 'output.xlsx' file?")
msg.addButton('Yes', QMessageBox.YesRole)
msg.addButton('No', QMessageBox.NoRole)
generate_output = msg.exec_()

# Generate output file if user chose to
if generate_output == 0:
    output_df.to_excel(os.path.join(processed_dir, 'output.xlsx'), index=False)

# Close progress dialog as processing is complete
progressDialog.close()