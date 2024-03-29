# How to use
**This method is for `Cloning` and optimized in `OT-2`. (`PCR` - `Assembly` - `Transformation`)**   

> Success  
The Maximum number of plates is 4  
Reaction Plate must be single and place on thermocycler.  

> Warnning  
The Name in each table is necessary!  
If name of sample is overlaped, protocol makes error.  
If name of sample is empty, the sample will be skipped  

## Usage flow

1. Fill the `DNA Plate` in the order of the following table  
2. Describe the Reaction using Sample Name write in `Sample Plate`.
3. Fill the `Reaction plate` in the order of the following table.
4. Fill the `TF plate` in the order of the following table.
   - You can spot the same sample several times.
5. If you don't use default setting, **check advanced tab**.
   - If you add additional DNA or enzyme you must fill the volume for it.
   - It can adjust volume and condition.
6. Click Make Protocol button.
   - Automatically check the error.
     - same sample name, empty sample name ...
   - The Report will be displayed  
   - Transformed Plate on each sample is recorded
   - Parameters used in this protocol
7. Download and Transfer protocol.py file to OT-2
8. Run the protocol with appropriate samples

# Developer only

## Protocol Maker

1. Check Number of plate and plate type can access to Device
2. Check whole DNA used in Reaction be in DNA plate.
3. Check whole Reacted Sample used in Transformation be in Reaction plate.
4. Check and Notice Enzyme and DW using in this Protocol.
5. Check Number of Reaction and How many tips need.
6. Make Report and Protocol with upper information.

## Parameters

프로토콜 동작을 위해 외부(Web) 에서 받아와야할 Parameter

### 정적 변수

Pipette Type  
Thermocycler Condition  
Enzyme deck position  
Deck position

### 동적 변수

**Plate**  
Plate Name  
Number of Plate  
Labware Name  
Plate Data (Long - Wide form 전환)  

**Reaction**  
Reaction table  
DNA, Enzyme 수  

**Transformation**  
Transformation Table (Spotting 여러번 가능)  

**Advanced**  
Reaction Volume  
Stop between steps  
PCR extension time  
Transformation recovery time

## Output Information

``` json
{
    "Plates": {
        "Name1": {
            "data": [Dict] Well Data,
            "labware": [str] Labware name,
            "type": [str] Plate type (DNA, PCR ...),
        }
    },
    "Reactions": {
        "Reaction_table": {
            "data": [Dict] Reaction table,
            "type": [str] Reaction type,
        }
    },
    "Reaction_volume": {
        "Reaction type": [Dict] Volumes in Reaction
    },
    "Deck": {
        "Enzyme_position": [Dict] Enzyme well position,
        "Deck_position": [Dict] Deck position
    },
    "Parameters": {
        "protocol": [str] "OT-2 Cloning",
        "Plate type": [Dict] Plate Order,
        "Reaction type": [Dict] Reaction Order,
        "number of tips": [int] Total Tips used in this protocol
    }
}
```

## session_state

``` json
"Plate": { # type: DNA, Reaction, TF
    "num_of_DNA_plate": [int] Number of DNA plate,
    "plate" : {
        f"{plate_type}_plate_{i}_df": [pd.DataFrame] Plate data, # long form
        f"{plate_type}_plate_{i}_name": [str] Plate name,
        f"{plate_type}_plate_{i}_labware": [str] Plate labware,
        f"{plate_type}_plate_{i}_toggle": [bool] Dataframe toggle,
        f"{plate_type}_plate_{i}_uploader": [str] Plate uploader,
    }
},
"Reaction": { # PCR, Assembly
    "reaction" : {
        f"{reaction_type}_plate_{i}_df": [pd.DataFrame] Plate data, # long form
        f"{reaction_type}_plate_{i}_selecttype": [str] Add column type,
        f"{reaction_type}_plate_{i}_addcolumn": [str] Add column type
    }
},

}


# st.session_state["Reaction_plate_0_df"]
# st.session_state["Reaction_plate_0_name"]
# st.session_state["Reaction_plate_0_labware"]
# st.session_state["Reaction_plate_0_toggle"]
# st.session_state["Reaction_plate_0_df"]
# st.session_state["Reaction_plate_0_uploader"]
# st.session_state["Reaction_plate_0_long"]
# st.session_state["Reaction_plate_0_wide"]
# st.session_state["num_of_Reaction_plate"]
# st.session_state["TF_plate_0_df"]
# st.session_state["TF_plate_0_name"]
# st.session_state["TF_plate_0_labware"]
# st.session_state["TF_plate_0_toggle"]
# st.session_state["TF_plate_0_df"]
# st.session_state["TF_plate_0_uploader"]
# st.session_state["TF_plate_0_long"]
# st.session_state["TF_plate_0_wide"]
# st.session_state["num_of_TF_plate"]
# st.session_state["labwares"]
# st.session_state["load"]
# st.session_state["messenger"]
# st.session_state["stop_between_reactions"]
# st.session_state["PCR_extension_time"]
# st.session_state["TF_recovery_time"]
```
## Check Protocol

프로토콜 마다 