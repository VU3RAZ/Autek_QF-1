"""Netlists for the two Autek QF-1 boards, as traced from the original schematics.
Each part: ref -> dict(sym, value, fp, pins={pin_number: net}, [dnp, note, group])."""

R07 = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
R09 = "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"
CFILM = "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"
CDISC = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
CHV = "Capacitor_THT:C_Disc_D7.5mm_W5.0mm_P5.00mm"
DIODE = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"
DIP8 = "Package_DIP:DIP-8_W7.62mm"
TO92 = "Package_TO_SOT_THT:TO-92_Inline_Wide"


def R(a, b, val, fp=R07, **kw):
    return dict(sym="Device:R", value=val, fp=fp, pins={"1": a, "2": b}, **kw)


def C(a, b, val, fp=CFILM, **kw):
    return dict(sym="Device:C", value=val, fp=fp, pins={"1": a, "2": b}, **kw)


def CP(p, n, val, fp, **kw):
    return dict(sym="Device:C_Polarized", value=val, fp=fp, pins={"1": p, "2": n}, **kw)


def D(a, k, val="1N4001", **kw):
    return dict(sym="Device:D", value=val, fp=DIODE, pins={"1": k, "2": a}, **kw)


# ----------------------------------------------------------------- MAIN BOARD
MAIN = dict(name="QF1_Main_Filter", title="Autek QF-1 — Main Filter Board", parts={})
P = MAIN["parts"]
# board pins 1-7 (J1) and 8-19 (J2), 20 (J3), 21 (J4) keep the original numbering
P["J1"] = dict(sym="Connector_Generic:Conn_01x07", value="Pins 1-7",
               fp="Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical",
               pins={"1": "B+IN", "2": "OUT_EXT", "3": "SW2_COM", "4": "IN", "5": "SEL_F",
                     "6": "R4_P6", "7": "GND"},
               note="Board pins 1 B+in, 2 out (not QF-1), 3 sw2 com, 4 input, 5/6 front select, 7 gnd")
j2 = {8: "BP1", 9: "R5_P9", 10: "NOTCH1", 11: "LP1", 12: "SW1_COM", 13: "SEL_R", 14: "R11_P14",
      15: "R10_P15", 16: "R9_P16", 17: "NOTCH2", 18: "BP2", 19: "R24_P19"}
P["J2"] = dict(sym="Connector_Generic:Conn_01x12", value="Pins 8-19",
               fp="Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",
               pins={str(k - 7): v for k, v in j2.items()},
               note="J2 pin n = original board pin n+7")
P["J3"] = dict(sym="Connector_Generic:Conn_01x01", value="Pin 20 GND",
               fp="Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical", pins={"1": "GND"})
P["J4"] = dict(sym="Connector_Generic:Conn_01x01", value="Pin 21 QF-1 OUT",
               fp="Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical", pins={"1": "OUT_QF1"})

# supply and bias
P["D1"] = D("B+IN", "B+")
P["R21"] = R("B+", "BIAS", "220K")
P["R20"] = R("BIAS", "GND", "220K")
P["C12"] = CP("BIAS", "GND", "22uF 25V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
P["C13"] = CP("B+", "GND", "47uF 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
              note="added: B+ bulk decoupling (not on original)")
P["C14"] = C("B+", "GND", "100nF", CDISC, note="added: decoupling U1/U2")
P["C15"] = C("B+", "GND", "100nF", CDISC, note="added: decoupling U3/U4")

# op-amps: TL072 replaces uA747 (A=1/2/3, B=5/6/7, V-=4, V+=8)
P["U1"] = dict(sym="Amplifier_Operational:TL072", value="TL072", note="replaces µA747", fp=DIP8,
               pins={"1": "HP1", "2": "SUM1", "3": "SEL_F", "5": "BIAS", "6": "INT1",
                     "7": "BP1", "4": "GND", "8": "B+"})
P["U2"] = dict(sym="Amplifier_Operational:TL072", value="TL072", note="replaces µA747", fp=DIP8,
               pins={"1": "LP1", "2": "INT2", "3": "BIAS", "5": "SEL_R", "6": "SUM2",
                     "7": "HP2", "4": "GND", "8": "B+"})
P["U3"] = dict(sym="Amplifier_Operational:TL072", value="TL072", note="replaces µA747", fp=DIP8,
               pins={"1": "BP2", "2": "INT3", "3": "BIAS", "5": "BIAS", "6": "INT4",
                     "7": "LP2", "4": "GND", "8": "B+"})
P["U4"] = dict(sym="Amplifier_Operational:TL071", value="TL071", note="replaces µA741", fp=DIP8,
               pins={"2": "U4_INV", "3": "BIAS", "6": "U4_OUT", "7": "B+", "4": "GND"})

# section 1
P["C1"] = C("IN", "C1_R1", "10nF 1kV", CHV)
P["R1"] = R("C1_R1", "SUM1", "100K")
P["R2"] = R("SUM1", "HP1", "22K")
P["R17"] = R("SUM1", "LP1", "22K")
P["C9"] = C("SUM1", "LP1", "n/s", CDISC, dnp=True, note="value not given on original; optional")
P["R16"] = R("HP1", "NOTCH1", "3.3K")
P["R15"] = R("NOTCH1", "LP1", "3.3K")
P["R3"] = R("HP1", "INT1", "4.7K", note="3.3K-6.8K, matched to C2-C5")
P["C2"] = C("INT1", "BP1", "18nF 1%")
P["R4"] = R("R4_P6", "BIAS", "4.7K", note="select to match selectivity pot")
P["R5"] = R("R5_P9", "INT2", "4.7K", note="3.3K-6.8K, matched to C2-C5")
P["C3"] = C("INT2", "LP1", "18nF 1%")
# section 2
P["R6"] = R("SW1_COM", "SUM2", "22K")
P["R7"] = R("SUM2", "HP2", "22K")
P["R14"] = R("SUM2", "LP2", "22K")
P["C10"] = C("SUM2", "LP2", "n/s", CDISC, dnp=True, note="value not given on original; optional")
P["R13"] = R("HP2", "NOTCH2", "3.3K")
P["R12"] = R("NOTCH2", "LP2", "3.3K")
P["R8"] = dict(sym="Device:R_Potentiometer_Trim", value="10K trim",
               fp="Potentiometer_THT:Potentiometer_Bourns_3386P_Vertical",
               pins={"1": "HP2", "2": "INT3", "3": "INT3"}, note="alignment trim (rheostat)")
P["C4"] = C("INT3", "BP2", "18nF 1%")
P["R24"] = R("BP2", "R24_P19", "10K")
P["R9"] = R("R9_P16", "BIAS", "4.7K", note="select to match selectivity pot")
P["R10"] = R("R10_P15", "INT4", "4.7K", note="3.3K-6.8K, matched to C2-C5")
P["C5"] = C("INT4", "LP2", "18nF 1%")
P["R11"] = R("LP2", "R11_P14", "4.7K", note="3.3K-6.8K")
# output amp
P["C11"] = C("SW2_COM", "U4_INV", "220nF")
P["R25"] = R("U4_INV", "U4_OUT", "100K")
P["C6"] = C("U4_INV", "U4_OUT", "1nF", CDISC)
P["R26"] = R("U4_OUT", "OUT_QF1", "100")
P["C7"] = CP("OUT_QF1", "OUT_EXT", "22uF 25V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
             dnp=True, note="not included in QF-1")
for i in range(1, 5):
    P[f"H{i}"] = dict(sym="Mechanical:MountingHole", value="M3", fp="MountingHole:MountingHole_3.2mm_M3",
                      pins={})

# ----------------------------------------------------------------- AMP / SUPPLY BOARD
AMP = dict(name="QF1_Amp_Supply", title="Autek QF-1 — Audio Power Amp / Supply Board", parts={})
A = AMP["parts"]
A["J101"] = dict(sym="Connector:Screw_Terminal_01x02", value="12-15 VAC IN",
                 fp="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
                 pins={"1": "AC1", "2": "AC2"}, note="from transformer secondary or AC adapter")
A["J102"] = dict(sym="Connector:Screw_Terminal_01x04", value="IN/GND/OUT/B+",
                 fp="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-4-5.08_1x04_P5.08mm_Horizontal",
                 pins={"1": "IN", "2": "GND", "3": "AUDIO_OUT", "4": "B+"})
A["D102"] = D("AC1", "B+", "1N4004")
A["D103"] = D("AC2", "B+", "1N4004")
A["D104"] = D("GND", "AC1", "1N4004")
A["D105"] = D("GND", "AC2", "1N4004")
A["C106"] = CP("B+", "GND", "1000uF 35V", "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm")
A["C109"] = C("B+", "GND", "100nF", CDISC, note="added: U101 decoupling")
A["R101"] = R("IN", "NA", "12K")
A["R102"] = R("NA", "NP", "100K")
A["C101"] = C("NA", "EMIT", "10nF")
A["C102"] = C("NP", "GND", "1nF", CDISC)
A["U101"] = dict(sym="Amplifier_Operational:TL071", value="TL071", note="replaces µA741", fp=DIP8,
                 pins={"2": "EMIT", "3": "NP", "6": "OA_OUT", "7": "B+", "4": "GND"})
A["C103"] = C("EMIT", "DRV", "1nF", CDISC)
A["R103"] = R("OA_OUT", "DRV", "100")
A["R104"] = R("DRV", "BIAS1", "39")
A["D101"] = D("BIAS1", "BIAS2", "1N4001")
A["R105"] = R("BIAS2", "GND", "1K")
A["Q101"] = dict(sym="Transistor_BJT:BC337", value="BC337", note="replaces MPS6560", fp=TO92,
                 pins={"1": "QC1", "2": "DRV", "3": "EMIT"})
A["Q102"] = dict(sym="Transistor_BJT:BC327", value="BC327", note="replaces MPS6562", fp=TO92,
                 pins={"1": "QC2", "2": "BIAS2", "3": "EMIT"})
A["R106"] = R("QC1", "B+", "3.3 1/2W", R09)
A["R107"] = R("QC2", "GND", "3.3 1/2W", R09)
A["C104"] = CP("EMIT", "AUDIO_OUT", "100uF 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
A["R108"] = R("AUDIO_OUT", "GND", "390")
A["C105"] = C("AUDIO_OUT", "GND", "100nF", CDISC, note="RF bypass (.1-.22)")
A["H101"] = dict(sym="Mechanical:MountingHole_Pad", value="RF GND to chassis",
                 fp="MountingHole:MountingHole_3.2mm_M3_Pad_Via", pins={"1": "GND"})
for i in range(102, 105):
    A[f"H{i}"] = dict(sym="Mechanical:MountingHole", value="M3", fp="MountingHole:MountingHole_3.2mm_M3",
                      pins={})

BOARDS = [MAIN, AMP]
