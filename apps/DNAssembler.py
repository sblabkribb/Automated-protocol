"""
DB를 JSON으로 처음부터 갔었으면 쉬웠을듯.
= 다른 사람들은 외부에서 excel을 열 수 있어야 하긴함..
"""

# Functions
import sys
import streamlit as st
import pandas as pd
from streamlit_ace import st_ace
import numpy as np
import re

# Necessary Data
# EXT well is opentrons 24 wells plate form.
EXT_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6']
_gen_wells = [str(j)+str(i) for j in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] for i in [1,2,3,4,5,6,7,8]]
DB = "./data/Part_DB.csv"
template_path = './data/protocols/DNAssembler/assembly_template.py'


class dna:
    # Basic information
    ## MW can calculate with python or Excel.
    ## MW & name is necessary
    def __init__(self, name, MW=None, No=None, well=None, plate="EXT"):
        #self.length = length
        #self.conc = conc
        self.MW = MW
        self.name = name
        self.No = No
        self.well = well
        self.plate = plate
    
    # get optimal volume based on [part, cds, vector]_MW parameter.
    def get_volume(self, goal_MW):
        if self.MW == None:
            return (self.vol)
        final = round(goal_MW/self.MW, 2)
        return (final)

def part_check(uni_parts, db):
    for i1 in uni_parts:
        if i1 in db['No'].values:
            continue
        else:
            st.error(f"Part Error ! '{i1}' isn't in DB", icon="🚨")
            st.stop()
            #sys.exit('Parts No Error')
    #print ("Parts confirmed")

def parameter_check(wells):
    for well in wells.iloc():
        part_num = len(well['DNA'].split('_'))
        vol_num = len(well['Volume'].split('_'))
        if part_num != vol_num:
            st.error(f"Volume Error!, {well['DNA']}'s Volume must be same length with part number \nExit Protocol.", icon="🚨")
            st.stop()
    #print ("Parameters Confrimed")

def part_to_dna_form(uni_parts, db):
    tmp = db[db["No"] == uni_parts]
    tmp_dna = dna(
        name = tmp.Name.values[0],
        MW = tmp.MW.values[0],
        well = tmp.Well.values[0],
        No = tmp.No.values[0],
        plate = tmp.plate.values[0])
    
    return (tmp_dna)

def assembly(well, part_list, part_list_dna, final_volume):
    n = 0
    No_list, name_list, vol_list, well_dict = [], [], [], {}
    for no, vol in zip(well['DNA'].split('_'), well['Volume'].split('_')):
        DNA = part_list_dna[part_list.index(no)]
        well_dict[f'part{n+1}'] = {'plate':DNA.plate, 'well': DNA.well, 'vol':vol}
        No_list.append(DNA.No)
        name_list.append(DNA.name)
        vol_list.append(float(vol))
        n+=1
    meta_data = {
        'No': '_'.join(No_list),
        'name': '_'.join(name_list),
        'DW': round(final_volume - sum(vol_list), 2)
        }
    well_dict['meta'] = meta_data

    return (well_dict)

def calculate_metadata(**kwargs):
    """
    kwargs : input_path, db_path
    """
    ## input parameter
    db = pd.read_csv(kwargs['db_path'])
    wells = kwargs['df'].iloc()[:,:3].fillna(0)
    well_parts = [i.split('_') for i in wells['DNA']]
    part_list = list(set(sum(well_parts, [])))
    part_check(part_list, db)
    parameter_check(wells)

    ## convert to dna class
    part_list_dna = [part_to_dna_form(i, db) for i in part_list]

    ### EXT parts
    n, ext_dna = 0, {}
    for i in part_list_dna:
        if i.plate == 'ext':
            ext_dna[i.No] = EXT_wells[n]
            i.well = EXT_wells[n]
            n+=1

    plates = list(set([i.plate for i in part_list_dna]))

    meta_data = {}
    n, well_data = 1, {}
    for well in wells.iloc():
        well_data[f'well{n}'] = assembly(well, part_list, part_list_dna, kwargs['final_volume'])
        n+=1

    meta_data['well_data'] = well_data
    meta_data['part'] = part_list
    meta_data['plate'] = plates
    meta_data['EXT'] = ext_dna

    meta_data['log'] = f"Final Well Number: {len(wells['DNA'])}  \n Used Parts: {part_list}"

    return (meta_data)

def app():
    
    def load_template(path):
        template = path

        with open(template, 'r') as f:
            template = ''.join(f.readlines())
            f.close()

        comment_tag = re.compile("#!#.+#!#") # for comment in template
        template = re.sub(comment_tag, "", template) # remove comment in template

        return (template)

    def export_protocol():
        data = calculate_metadata(df=df, db_path = DB, final_volume=20)
        plate = data['plate']

        if len(plate) > 4:
            sys.exit("Too many plates ! Maximum is 4. \nProtocol End")

        n, load_plate = 1, []
        for i in plate:
            load_plate.append(f"globals()['{i}'] = protocol.load_labware('biorad_96_wellplate_200ul_pcr', {n})")
            n+=1
        
        new_script = template.format(date = date, meta_data = str(data), load_plate='\n    '.join(load_plate), thermocycler=thermocycler)
            # Output protocol
        return data, new_script


    # DIV
    st.title("DNAssembler")
    st.caption("Author : Seong-Kun Bak <<tjdrns227@gmail.com>>")
    st.text("")

    # Session Data
    if 'DB' not in st.session_state:
        st.session_state.DB = pd.read_csv(DB)
    if 'gen_well' not in st.session_state:
        st.session_state.gen_well = pd.DataFrame({'Well': [],'DNA':[], 'Volume':[]})
    if '_gen_well_count' not in st.session_state:
        st.session_state._gen_well_count = 0

    tab1, tab2, tab3 = st.tabs(["Protocol generation", "Generate Input File", "Part DB"])

    with tab1:
        with st.container():
            date = st.date_input("Date")
            input_wells = st.file_uploader("Upload Wells", type=".csv", key='uploaded')
            if st.checkbox("Use Sample", False, key='sample'):
                input_wells = './data/assembly_input.csv'
                
            if input_wells:
                df = pd.read_csv(input_wells)
                with st.expander('Preview'):
                    st.dataframe(df.head())
            st.text("")

        st.subheader("Parameters")
        thermocycler = st.selectbox("RUN Thermocycler", ('False', 'True'), help = "Directly run thermocycler in OT2")
        st.text("")

        #Load_template
        template = load_template(path = template_path)

        if 'make_protocol' not in st.session_state:
            st.session_state.make_protocol = False

        if st.session_state.uploaded or st.session_state.sample:
            st.session_state.make_protocol = True
            data, template = export_protocol()

        st.download_button("⬇️ Download Protocol", template, file_name="DNAssembler.py", disabled=(st.session_state.make_protocol is not True))

        with st.expander("Detail Information"):
            st.warning("For more informations like Deck Position,\\\nCheck the Opentrons App")
            if input_wells:
                f"""
                **Plate** : {data['plate']}  
                **Part**  : {data['part']}  
                **EXT**   : {data['EXT']}
                """
            else:
                pass

        with st.expander("Change Script (Only for Developer)"):
            edit_code = st_ace(template, language='python', theme='dracula')
            st.download_button("⬇️ Editied Protocol", edit_code, file_name='DNAssembler.py')


    with tab2:
        with st.container():
            st.subheader("Generate Input")
            col1_1, col1_2 = st.columns([1,1])
            with col1_1:
                library = st.selectbox("Form", ("Single", "Library"), 
                                       help = "If you use 'library', Please separate part No with comma")
            with col1_2:
                part_num = st.number_input("Part Numbers", min_value = 1, max_value=4, help="Max is 4")

            col2_1, col2_2, col2_3, col2_4, col2_5 = st.columns([1,3,2,2,1])
            col2_1.markdown("##")
            col2_2.markdown("**No**")
            col2_3.markdown("**Volume (uL)**")
            col2_4.markdown("**MW (fmol)**")
            col2_5.markdown("**Use MW**")
            for i in range(part_num):
                if f'usemw{i+1}' not in st.session_state:
                    st.session_state[f'usemw{i+1}'] = False

            for i in range(part_num):
                col2_1.write("")
                col2_1.markdown(f"Part{i+1}")
                col2_2.text_input(f"no{i+1}", key =f'no{i+1}', label_visibility='collapsed')
                col2_3.number_input(f"vol{i+1}", key= f'vol{i+1}', step=0.1, label_visibility='collapsed', disabled = st.session_state[f'usemw{i+1}']) 
                col2_4.text_input(f"mw{i+1}", key=f'mw{i+1}', label_visibility='collapsed', disabled = not st.session_state[f'usemw{i+1}'])
                col2_5.write("")
                col2_5.checkbox("", key=f"usemw{i+1}")
            if st.button("Submit"):
                DNA, VOLUME = [], []
                for i in range(part_num):
                    DNA.append(st.session_state[f'no{i+1}'])
                    VOLUME.append(str(st.session_state[f'vol{i+1}']))
                new_well = {'Well': _gen_wells[st.session_state._gen_well_count], 'DNA':['_'.join(DNA)], 'Volume': ['_'.join(VOLUME)]}
                st.session_state._gen_well_count += 1
                st.session_state.gen_well = pd.concat([st.session_state.gen_well, pd.DataFrame(new_well)], ignore_index=True, axis=0)

        with st.expander("Submitted Wells", expanded=True):
            st.dataframe(st.session_state.gen_well, use_container_width=True)
            st.download_button('⬇️ Download', st.session_state.gen_well.to_csv(), file_name='assembly_input.csv')
    
    with tab3:
        st.subheader("Part DB")
        st.warning("In this Page, Only can add data temporarly \\\nIf you want to add data permanently, Move to Part DB on sidebar")
        
        plate = st.selectbox("Well Plate", np.delete(st.session_state.DB['plate'].unique(), 0))
        st.dataframe(st.session_state.DB.query(f"plate == '{plate}'"))
        
        with st.container():

            if 'count' not in st.session_state:
                st.session_state.count = 1

            with st.form("cont2", clear_on_submit=True):
                st.markdown('**Add temporary data**')
                name = st.text_input('Name')
                vol = st.text_input('Volume')
                st.text_input('Plate', 'ext', disabled=True, help='Temporary data only can add as ext')
                st.text_input('No', f'e{st.session_state.count}', disabled=True, help='Temporary data only can add as ext')
                if st.form_submit_button('Add data', help = 'Fill all of sections'):
                    if (name == '') | (vol == ''):
                        st.error('Fill All of sections!')
                    else:
                        df2 = ({'Name': name, 'plate':'ext', 'No': f'e{st.session_state.count}'})
                        st.session_state.DB = st.session_state.DB.append(df2, ignore_index=True)
                        st.success(f"Succesfully Add as e{st.session_state.count}")
                        st.session_state.count += 1
                        st.experimental_rerun()
                        #form 초기화 필요

if __name__=='__main__':
    app()