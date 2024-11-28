from flask import Flask, request, jsonify
import os
import numpy as np
import joblib
import pefile
import re

app = Flask(__name__)

# Load the model
model_path = "rf_ransomware.pkl"
model = joblib.load(model_path)

# Feature extraction functions (same as your provided code)
def get_dll_characteristics(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.DllCharacteristics

def get_major_linker_version(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.MajorLinkerVersion

def get_debug_rva(filepath):
    pe = pefile.PE(filepath)
    if hasattr(pe.OPTIONAL_HEADER, "DATA_DIRECTORY"):
        return pe.OPTIONAL_HEADER.DATA_DIRECTORY[6].VirtualAddress  # Debug directory RVA
    return 0

def get_major_os_version(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.MajorOperatingSystemVersion

def get_debug_size(filepath):
    pe = pefile.PE(filepath)
    if hasattr(pe.OPTIONAL_HEADER, "DATA_DIRECTORY"):
        return pe.OPTIONAL_HEADER.DATA_DIRECTORY[6].Size  # Debug directory size
    return 0

def get_resource_size(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.DATA_DIRECTORY[2].Size  # Resource directory size

def get_size_of_stack_reserve(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.SizeOfStackReserve

def get_machine(filepath):
    pe = pefile.PE(filepath)
    return pe.FILE_HEADER.Machine

def get_number_of_sections(filepath):
    pe = pefile.PE(filepath)
    return pe.FILE_HEADER.NumberOfSections

def get_iat_vra(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress  # IAT address

def get_major_image_version(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.MajorImageVersion

def get_export_size(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size  # Export table size

def get_minor_linker_version(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.MinorLinkerVersion

def get_export_rva(filepath):
    pe = pefile.PE(filepath)
    return pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress  # Export table RVA

def detect_bitcoin_addresses(filepath):
    with open(filepath, "rb") as file:
        content = file.read().decode("utf-8", errors="ignore")
        return len(re.findall(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b", content))

# Function to extract all necessary features from a file
def extract_features_from_file(filepath):
    features = [
        get_dll_characteristics(filepath),
        get_major_linker_version(filepath),
        get_debug_rva(filepath),
        get_major_os_version(filepath),
        get_debug_size(filepath),
        get_resource_size(filepath),
        get_size_of_stack_reserve(filepath),
        get_machine(filepath),
        get_number_of_sections(filepath),
        get_iat_vra(filepath),
        get_major_image_version(filepath),
        get_export_size(filepath),
        get_minor_linker_version(filepath),
        get_export_rva(filepath),
        detect_bitcoin_addresses(filepath),
    ]
    return np.array(features).reshape(1, -1)

# Ransomware detection logic
def detect_ransomware_from_file(filepath):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return

    # Extract features and make prediction
    features = extract_features_from_file(filepath)
    prediction = model.predict(features)
    prediction_probabilities = model.predict_proba(features)

    # Log the prediction details
    print(f"Prediction: {prediction[0]} (1: ransomware, 0: safe)")
    print(f"Prediction Probabilities: {prediction_probabilities}")

    # Compare the two probabilities
    if prediction_probabilities[0][0] > prediction_probabilities[0][1]:  # Class 1: ransomware
        print("Warning: This file is classified as ransomware.")
        return "ransomware"
    else:  # Class 0: safe
        print("Safe: This file is classified as safe.")
        return "safe"

# API route to detect ransomware via file path
@app.route('/detect_ransomware', methods=['POST'])
def detect_ransomware():
    data = request.get_json()
    file_path = data.get("file_path")
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400

    result = detect_ransomware_from_file(file_path)
    if result:
        return jsonify({
            "file_status": result,
            "message": "File classified successfully."
        })
    else:
        return jsonify({"error": "File not found or processing error"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
