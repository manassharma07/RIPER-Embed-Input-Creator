import streamlit as st
import streamlit.components.v1 as components
import py3Dmol
import subprocess
import sys
import time
from io import StringIO
import pandas as pd
import numpy as np

try:
    # from openbabel import OBMol, OBConversion
    import openbabel
except ModuleNotFoundError as e:
    subprocess.Popen([f'{sys.executable} -m pip install --global-option=build_ext --global-option="-I/usr/include/openbabel3" --global-option="-L/usr/lib/openbabel" openbabel'], shell=True)
    subprocess.Popen([f'{sys.executable} -m pip install --global-option=build_ext --global-option="-I/home/appuser/include/openbabel3" --global-option="-L/home/appuser/lib/openbabel" openbabel'], shell=True)
    subprocess.Popen([f'{sys.executable} -m pip install --global-option=build_ext --global-option="-I/home/appuser/usr/include/openbabel3" --global-option="-L/home/appuser/usr/lib/openbabel" openbabel'], shell=True)
    # wait for subprocess to install package before running your actual code below
    time.sleep(90)
    
import os
from openbabel import pybel

if os.path.exists('viz.html'):
    os.remove('viz.html')

def COM_calculator(coords):
    return coords.mean(axis=0)

# Set page config
st.set_page_config(page_title="DFT based Embedding Input File Creator (for TURBOMOLE's riper module)", layout='wide', page_icon="🧊",
menu_items={
         'About': "### This online tool allows you to create an input file for DFT based embedding calculations using TURBOMOLE's riper module"
     })


# Sidebar stuff
st.sidebar.write('# About')
st.sidebar.write('### Made By [Manas Sharma](https://manas.bragitoff.com/)')
st.sidebar.write('### *Powered by*')
st.sidebar.write('* [Py3Dmol](https://pypi.org/project/py3Dmol/) for Visualization')
st.sidebar.write('* [Open Babel](http://openbabel.org/) for Format Conversion')
st.sidebar.write('## Brought to you by [TURBOMOLE](https://www.turbomole.org)')
st.sidebar.write('## Cite us:')
st.sidebar.write('[Sharma, M. & Sierka, M. (2022). J. Chem. Theo. Comput. xx, xxxx-xxxx.](https://doi.org/10.1021/acs.jctc.2c00380)')

# Main app
st.write("## DFT based Embedding Input File Creator (for TURBOMOLE's riper module)")
st.write("This online tool allows you to create an input file for DFT based embedding calculations using TURBOMOLE's riper module")


# DATA for test systems
hf_dimer_xyz = '''
4

F          1.32374       -0.09023       -0.00001
H          1.74044        0.73339        0.00001
F         -1.45720        0.01926       -0.00001
H         -0.53931       -0.09466        0.00015
'''
h2o_dimer_xyz = '''
6

O          1.53175        0.00592       -0.12088
H          0.57597       -0.00525        0.02497
H          1.90625       -0.03756        0.76322
O         -1.39623       -0.00499        0.10677
H         -1.78937       -0.74228       -0.37101
H         -1.77704        0.77764       -0.30426
'''
nh3_dimer_xyz = '''
8

N          1.57523        0.00008       -0.04261
H          2.13111        0.81395       -0.28661
H          1.49645       -0.00294        0.97026
H          2.13172       -0.81189       -0.29145
N         -1.68825        0.00008        0.10485
H         -2.12640       -0.81268       -0.31731
H         -2.12744        0.81184       -0.31816
H         -0.71430        0.00054       -0.19241
'''
ch4_dimer_xyz = ''''''
benzene_fulvene_dimer_xyz = '''
24

C         -0.65914       -1.21034        3.98683
C          0.73798       -1.21034        4.02059
C         -1.35771       -0.00006        3.96990
C          1.43653       -0.00004        4.03741
C         -0.65915        1.21024        3.98685
C          0.73797        1.21024        4.02061
H         -1.20447       -2.15520        3.97369
H          1.28332       -2.15517        4.03382
H         -2.44839       -0.00006        3.94342
H          2.52722       -0.00004        4.06369
H         -1.20448        2.15509        3.97373
H          1.28330        2.15508        4.03386
C          0.64550       -0.00003        0.03038
C         -0.23458       -1.17916       -0.00274
C         -0.23446        1.17919       -0.00272
C         -1.51856       -0.73620       -0.05059
C         -1.51848        0.73637       -0.05058
C          1.99323       -0.00010        0.08182
H          0.11302       -2.20914        0.01010
H          0.11325        2.20913        0.01013
H         -2.41412       -1.35392       -0.08389
H         -2.41398        1.35418       -0.08387
H          2.56084        0.93137        0.10366
H          2.56074       -0.93163        0.10364
'''
ethane_xyz = '''
8

C          0.00000        0.00000        0.76510
H          0.00000       -1.02220        1.16660
H         -0.88530        0.51110        1.16660
H          0.88530        0.51110        1.16660
C          0.00000        0.00000       -0.76510
H          0.88530       -0.51110       -1.16660
H          0.00000        1.02220       -1.16660
H         -0.88530       -0.51110       -1.16660
'''

dict_name_to_xyz = {'HF dimer': hf_dimer_xyz,'H2O dimer': h2o_dimer_xyz,'NH3 dimer': nh3_dimer_xyz,'Benzene-Fulvene': benzene_fulvene_dimer_xyz,'Ethane': ethane_xyz}

input_test_system = st.selectbox('Select a test system',
     ( 'HF dimer', 'H2O dimer', 'NH3 dimer', 'Benzene-Fulvene', 'Ethane'))

selected_xyz_str = dict_name_to_xyz[input_test_system]

st.write('#### Alternatively you can provide the XYZ file contents of your own structure here')
input_text_area = st.empty()
input_geom_str = input_text_area.text_area(label='XYZ file of the given/selected system', value = selected_xyz_str, placeholder = 'Put your text here', height=250, key = 'input_text_area')
# Get rid of trailing empty lines
input_geom_str = input_geom_str.rstrip()
# Get rid of leading empty lines
input_geom_str = input_geom_str.lstrip()

uploaded_file = st.file_uploader("You can also choose a file on your system")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()
    selected_xyz_str = string_data
    input_geom_str = input_text_area.text_area(label='XYZ file of the given/selected system', value = selected_xyz_str, placeholder = 'Put your text here', height=250)
    

### Create a dataframe from the original XYZ file ###
INPUT_GEOM_DATA = StringIO(input_geom_str[2:])
df = pd.read_csv(INPUT_GEOM_DATA, delim_whitespace=True, names=['atom','x','y','z'])
# df.reindex(index=range(1, natoms_tot+1))
df.index += 1 
coords_tot_np_arr = df[['x','y','z']].to_numpy()

st.write('#### Visualization')
### VISUALIZATION ####
style = st.selectbox('Visualization style',['ball-stick','line','cross','stick','sphere'])
col1, col2 = st.columns(2)
spin = col1.checkbox('Spin', value = False)
showLabels = col2.checkbox('Show Labels', value = True)
view = py3Dmol.view(width=500, height=300)
structure_for_visualization = ''
try:
    mol = pybel.readstring('xyz', input_geom_str)
    natoms_tot = len(mol.atoms)
    # mol.make3D()
    if style=='cartoon':
        structure_for_visualization = mol.write('pdb')
    else:
        structure_for_visualization = mol.write('xyz')
except Exception as e:
    print('There was a problem with the conversion', e)
if style=='cartoon':
    view.addModel(structure_for_visualization, 'pdb')
else:
    view.addModel(structure_for_visualization, 'xyz')
if style=='ball-stick': # my own custom style
    view.setStyle({'sphere':{'colorscheme':'Jmol','scale':0.3},
                       'stick':{'colorscheme':'Jmol', 'radius':0.}})
else:
    view.setStyle({style:{'colorscheme':'Jmol'}})
# Label addition template
# view.addLabel('Aromatic', {'position': {'x':-6.89, 'y':0.75, 'z':0.35}, 
#             'backgroundColor': 'white', 'backgroundOpacity': 0.5,'fontSize':18,'fontColor':'black',
#                 'fontOpacity':1,'borderThickness':0.0,'inFront':'true','showBackground':'false'})
if showLabels:
    for atom in mol:
        view.addLabel(str(atom.idx), {'position': {'x':atom.coords[0], 'y':atom.coords[1], 'z':atom.coords[2]}, 
            'backgroundColor': 'white', 'backgroundOpacity': 0.5,'fontSize':18,'fontColor':'black',
                'fontOpacity':1,'borderThickness':0.0,'inFront':'true','showBackground':'false'})
# Draw Axis
originAxis = [0.0, 0.0,0.0]
view.addArrow({"start": {"x":originAxis[0], "y":originAxis[1], "z":originAxis[2]}, "end": {"x":0.8, "y":originAxis[1], "z":originAxis[2]}, "radiusRadio": 0.2, "color":"red"})
view.addArrow({"start": {"x":originAxis[0], "y":originAxis[1], "z":originAxis[2]}, "end": {"x":originAxis[0], "y":0.8, "z":originAxis[2]}, "radiusRadio": 0.2, "color":"green"})
view.addArrow({"start": {"x":originAxis[0], "y":originAxis[1], "z":originAxis[2]}, "end": {"x":originAxis[0], "y":originAxis[1], "z":0.8}, "radiusRadio": 0.2, "color":"blue"})
view.addLabel('x', {'position': {'x':0.8, 'y':originAxis[1] + 0.1, 'z':originAxis[2]}, 
            'backgroundColor': 'white', 'backgroundOpacity': 0.5,'fontSize':15,'fontColor':'black',
                'fontOpacity':1,'borderThickness':0.0,'inFront':'true','showBackground':'false'})
view.addLabel('y', {'position': {'x':originAxis[0], 'y':0.8 + 0.1, 'z':originAxis[2]}, 
            'backgroundColor': 'white', 'backgroundOpacity': 0.5,'fontSize':15,'fontColor':'black',
                'fontOpacity':1,'borderThickness':0.0,'inFront':'true','showBackground':'false'})
view.addLabel('z', {'position': {'x':originAxis[0], 'y':originAxis[1] + 0.1, 'z':0.8}, 
            'backgroundColor': 'white', 'backgroundOpacity': 0.5,'fontSize':15,'fontColor':'black',
                'fontOpacity':1,'borderThickness':0.0,'inFront':'true','showBackground':'false'})
# view.addCylinder({"start": {"x":0.0, "y":2.0, "z":0.0}, "end": {"x":0.5, "y":2.0, "z":0.0}, "radius": 0.5, "color":"red"})
view.zoomTo()
view.spin(spin)
view.setClickable({'clickable':'true'})
view.enableContextMenu({'contextMenuEnabled':'true'})
view.show()
view.render()
view.resize()
# view.png()
t = view.js()
f = open('viz.html', 'w')
f.write(t.startjs)
f.write(t.endjs)
f.close()

col1, col2 = st.columns(2)
with col1:
    st.write('#### Visualization [Original]')
    HtmlFile = open("viz.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 300, width=900)
    HtmlFile.close()

with col2:
    st.write('#### Atomic Positions ')
    st.table(df)
    st.write('Center of Mass of the total system', COM_calculator(coords_tot_np_arr))

# Select some rows using st.multiselect. This will break down when you have >1000 rows.
st.write('#### Choose the atom labels/indices that should assigend to subsystem A')
selected_indices = st.multiselect('Select rows:', df.index)
selected_rows_A = df.loc[selected_indices]
selected_rows_B = df.loc[~df.index.isin(selected_indices)]

coords_A_np_arr = selected_rows_A[['x','y','z']].to_numpy()
coords_B_np_arr = selected_rows_B[['x','y','z']].to_numpy()
com_A = COM_calculator(coords_A_np_arr)
com_B = COM_calculator(coords_B_np_arr)
col1, col2 = st.columns(2)
with col1:
    st.write('#### Selected atoms for subsystem A')
    st.table(selected_rows_A)
    st.write('Center of Mass of the subsystem A', COM_calculator(coords_A_np_arr))
with col2:
    st.write('#### Selected atoms for subsystem B')
    st.table(selected_rows_B)
    st.write('Center of Mass of the subsystem B', COM_calculator(coords_B_np_arr))


dist_bw_subsystems = np.linalg.norm(com_A - com_B)
st.write('Distance b/w the subsystems: ' + str(np.round(dist_bw_subsystems, 6))+'  Angstroms')
st.write('#### Reformatted XYZ file with the atoms belonging to the subystem A in the beginning')
modified_xyz = selected_rows_A.to_string(header=False, index=False)
modified_xyz = modified_xyz + '\n' + selected_rows_B.to_string(header=False, index=False)
st.text(modified_xyz)



### BASIS SET ####
is_same_basis_set = st.checkbox('Use same basis set for the total system', value=True)

basis_set_list = ('sto-3g', 'def2-SVP', 'def2-TZVP', 'def2-TZVPP', 'def2-TZVPD', 'def2-TZVPPD', 'def2-QZVP', '6-31G', '6-311G')

if is_same_basis_set:
    basis_set_tot = st.selectbox('Select a basis set for the total system',
        basis_set_list, key='basis_set_tot')
else:
    basis_set_A = st.selectbox('Select a basis set for the subsystem A',
    basis_set_list, key='basis_set_A')
    basis_set_B = st.selectbox('Select a basis set for the subsystem A',
    basis_set_list, key='basis_set_B')