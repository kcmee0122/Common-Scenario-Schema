# Common-Scenario-Schema
The scenario-based approach is used for generation of safety-critical scenarios. It is applied for various applications ranging from development of perception and decision algorithms to the corresponding test and validation.

# Installation
Installing Packages

scipy >= 1.14.0
h5py >= 3.12.1
pandas >= 2.2.2
colorama >= 0.4.6
tqdm >= 4.66.4
natsort >= 8.4.0
openpyxl >= 3.1.5
pymongo >= 4.8.0


# Usage
<img width="1843" height="939" alt="image" src="https://github.com/user-attachments/assets/3ef7552d-4dea-4c7e-8104-b566e4f829de" />

A.1. Generation of logical scenario (Manual)
Logical scenarios are defined as knowledge-based, data-driven (FOT), and scenario augmentation processes. To implement the defined logical scenarios in a file, you must create a file for your simulator.

Logical scenario file extensions to create

xosc (MORAI)
testrun (carmaker)
A.2. CSS for logical scenario (Code)
After the logical scenarios are created or programmed in the framework of CarMaker or MORAI SIM (i.e., XOSC), create a common scenario schema (CSS) corresponding to the scenario database. The schema code for databasing logical scenarios created with MORAI is css_for_xosc.py. The output of the code is a JSON file.


A.3. Generation of raw parameter space (Manual)
Raw parameter space file name to create

rawPS: Parameter ranges defined by expert knowledge
rawPS_Dim: Adding the parameter dimension of an existing scenario
rawPS_Extend: Extending parameter ranges for existing scenarios
rawPS_Geometry: Changing road terrain in an existing scenario
rawPS_New: Defining scenario parameters at the wrong point in time for a non-existent algorithm in an existing scenario catalog
A.4. CSS for raw parameter space (Code)
Create a schema for database with the generated raw parameter space. The code for generating the schema is css_for_RawPS.py. The output of the code is a JSON file.

A.5. CSS for road (Code)
This is the code that populates the schema with road information relevant to the scenario generation. The code for adding this information is css_for_road.py. The output of the code is a JSON file.
