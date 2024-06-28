from typing import List
import pandas as pd

class Process:
    def __init__(self, process_name: str, tonnage: int, tonnage_alternatives: List[int], stock: int):
        self.process_name = process_name
        self.tonnage = tonnage
        self.tonnage_alternatives = tonnage_alternatives
        self._stock = stock

    def __str__(self):
        return f"Process: {self.process_name}, Tonnage: {self.tonnage}"
    
    @property
    def stock(self):
        return self._stock
    
    @stock.setter
    def stock(self, new_value):
        self._stock = new_value

    def __str__(self):
        return f"Process: {self.process_name}, Tonnage: {self.tonnage}, Tonnage Alternatives: {self.tonnage_alternatives}, Stock: {self._stock}"

class Part:
    def __init__(self, name: str, id: str, customer:str, ideal_stock_3hk: int, material: str, processes: List[Process], material_multiplier: float, minimum_production_quantity: int, is_active: bool):
        self.name = name
        self.id = id
        self.customer = customer
        self.ideal_stock_3hk = ideal_stock_3hk
        self.material = material
        self.material_multiplier = material_multiplier
        self.processes = processes
        self.minimum_production_quantity = minimum_production_quantity
        self.is_active = is_active
        
    def __str__(self):
        processes_str = "\n".join(f"  {process}" for process in self.processes)
        return (
            f"Part: {self.name}\n"
            f"ID: {self.id}\n"
            f"Customer: {self.customer}\n"
            f"Ideal Stock 3HK: {self.ideal_stock_3hk}\n"
            f"Material: {self.material}\n"
            f"Material Multiplier: {self.material_multiplier}\n"
            f"Processes:\n{processes_str}"
        )

materials = {'SPHC  3.2 X 99 X 1494': 162,
 'SPHC  3.2 X 124 X 2385': 0,
 'SPHC-PO  2.3 X 230 X 430': 0,
 'SPCC T 2.0 X 50 X 1219': 2184,
 'SPCC T 1.6 X 570 X 150': 0,
 'SPCC T 1.6 X 655 X 1219': 0,
 'SPCC T.1.2 X 645 X 1219': 0,
 'SPCC T 1.2 X 648 X 1219': 0,
 'SGCC T. 0.23 X 535 X 729.6': 0,
 'SGCC T. 0.23 X 541 X 636.2': 1000,
 'SGCC T. 0.23 X 535 X 829.6': 0,
 'SPCC T 1.4 X 540 X 1219': 0,
 'SPCC T 2.0 X 780 X 1219': 0,
 'SGCC T. 0.23 X 555 X 881.6': 0,
 'SGCC T. 0.23 X 561 X 666.2': 0,
 'SGCC T. 0.23 X 555 X 951.6': 0,
 'SGCC T. 0.23 X 535 X 909.6': 0,
 'SGCC T. 0.23 X 535 X 967.6': 0,
 'SPCC T 1.4 X 585 X 1219': 0,
 'SGCC T. 0.23 X 555 X 1193.6': 0,
 'SGCC T. 0.23 X 561 X 706.2': 0,
 'SGCC T. 0.23 X 560.7 X 656.2': 0,
 'SGCC T. 0.23 X 555 X 1431.6': 0,
 'SGCC T. 0.23 X 555 X 1049.4': 500,
 'SGCC T. 0.23 X 555 X 1229.4': 500,
 'SGCC T. 0.23 X 500 X 522.1': 0,
 'SGCC T. 0.23 X 278 X 536.8': 0,
 'SGCC T. 0.23 X 555 X 1479.4': 4000,
 'SCGA270D-45 T. 1.00 X 125 X 435': 0,
 'SS400 D.10.00 X 1200': 0,
 'SS400 D.10.00 X 1000': 0,
 'SPHC-P T. 2.00 X 98 X COIL': 2355,
 'SPHC-P T. 2.00 X 164 X COIL': 2705,
 'SPC440 T. 1.40 X 152 X COIL': 1771,
 'SCGA270D-45 T. 1.00 X 223 X 531': 0,
 'SCGA270D-45 T. 0.75 X 128 X 408': 0,
 'SCGA270D-45 T. 0.70 X 154 X 135': 0,
 'SCGA440-45A T. 1.00 X 378 X 182': 0,
 'SPC70C T. 1.2 X 80 X 1190 ': 0,
 'JSC270C T. 1.00 X 145 X 200': 0,
 'JSH270C T. 3.2 X 120 X 1219': 13148,
 'JSC270C T. 1.20 X 78 X 1219': 5886,
 'SPC270C T. 1.2 X 68 X 1219': 4797,
 'JSC270C T. 1.20 X 200 X 1219': 0,
 'JSH270C T. 1.6 X 272 X 1219': 0,
 'SPHC-P T. 1.60 X 275 X 1219': 0,
 'SPHC-P T. 1.60 X 120 X 1219': 0,
 'SPC270C T. 0.9 X 1210 X 95': 0,
 'JSH270C T. 1.4 X 680 X 230': 2403,
 'JAC270C-45/45 T. 1.2 X 1290 X 140': 0,
 'JAC270C -45/45 T.1.6 X 1340 X 900': 4884,
 'JAC270C 45/45 T. 0.8 X 290 X 290': 360,
 'SPHC-PO T. 1.6 X 135 X 1114': 1311,
 'SPC270C T. 1 X 69 X 270': 4860,
 'JSH270C T. 2.0 X 1630 X 200': 0,
 'JSH270C T. 2.6 X 1340 X 920': 0,
 'SHGA270C T. 2.6 X 177 X 1170': 0,
 'JAC270C T. 1.2 X 1290 X 160': 2660,
 'JAC270C T.1.2 X 1219 X 160': 0,
 'SS400 T. 3.2 X 1150 X 34': 0,
 'SPC270C T. 0.70 X 147 X 1219': 7200,
 'SPHC-PO T 2.0 X 1400 X 75': 0,
 'SPHC T. 1.6 X 870 X 690 ': 0,
 'SPCC T 1.6 X 611 X 1219 ': 0,
 'SPCC T 1.6 X 565 X 1219': 0,
 'SPCC T 1.6 X 735.5 X 1219': 0,
 'SPCC T 1.6 X 671 X 1219': 0,
 'SPCC T 1.6 X 640 X 1219': 0,
 'SPC440 T. 1.00 X 217 X 1200': 34224,
 'SPC440 T. 1.00 X 277 X 1219': 6600,
 'SPC440 T. 1.60 X 45 X 610': 14400,
 'SCGA270C-45 T. 1.40 X 384 X 1219': 9600,
 'JSC270C 0.8 X 133 X 1480 ': 0,
 'JAC270C-45/45 T. 1.2 X 310 X 1290': 0,
 'SPHC-PO T.2.0 X 175 X 1400': 0,
 'SPHC-PC T. 3.2 X 70 X 660 ': 0,
 'SS400 T. 3.2 X 120 X 646': 0,
 'GALVANIZED T. 1.2 X 150 X 13': 25600,
 'ZACS T. 0.6 X 45 X 700': 10080}

import pickle as pkl
from datetime import datetime
parts = pkl.load(open('data/parts.pickle', 'rb'))
parts_last_updated = datetime(2024, 6, 11, 0, 0, 0, 0)

def get_report_document(type, env):
    supported_docs = ['SPK_ACTUALIZATION', "MATERIAL_IN", "DELIVERY_OUT"]
    assert type in supported_docs, f"document type not supported yet, supported type: {supported_docs}"
    assert env in ['DEV', 'PROD'], "Environment should be 'DEV' or 'PROD'"

    if env == 'DEV':
        if type == 'SPK_ACTUALIZATION':
            return pkl.load(open('data/fake_actspk.pickle', 'rb')) # actualization of SPK
        elif type == "MATERIAL_IN":
            return pkl.load(open('data/fake_mtlin.pickle', 'rb')) # material in
        elif type == "DELIVERY_OUT":
            return pkl.load(open('data/fake_rekapdo.pickle', 'rb')) # rekap delivery out

    elif env == 'PROD':
        import pyodbc
        cnxn = pyodbc.connect("Driver={ODBC Driver 18 for SQL Server};"
                            "Server=localhost, 64872;"
                            "Database=AZKA;"
                            "UID=sa;"
                            "PWD=sbs;"
                            "Encrypt=no;")
        cursor = cnxn.cursor()
        
        if type == 'SPK_ACTUALIZATION':
            cursor.execute('SELECT Q_ACTSPK.* FROM Q_ACTSPK')
            return [row for row in cursor]
        elif type == "MATERIAL_IN":
            cursor.execute('SELECT Q_MTLIN.* FROM Q_MTLIN')
            return [row for row in cursor]
        elif type == "DELIVERY_OUT":
            cursor.execute('SELECT Q_REKAPDO.* FROM Q_REKAPDO')
            return [row for row in cursor]

def update_stock(parts, materials, env):
        import re

        def opstring2idx(input_string):
            match = re.search(r'\d+', input_string)
            if match:
                idx = int(match.group())
                idx = idx//10 - 1
                return idx
            else:
                return None  # or handle the case where no integer is found

        name2idx = {part.name:idx for idx, part in enumerate(parts)}
        
        # add past production to stocks
        actspk = get_report_document('SPK_ACTUALIZATION', env)
        for production in actspk:
            date = production[1]
            if date > parts_last_updated:
                produced_quantity = production[7]
                name = production[9] #part name
                name = name.replace('.', '').strip()
                operation = production[4]
                if name in name2idx:
                    part_idx = name2idx[name]
                    process_idx = opstring2idx(operation)
                    if process_idx < len(parts[part_idx].processes):
                        parts[part_idx].processes[process_idx].stock += int(produced_quantity)

        # add material inventorization to material stocks
        mtlin = get_report_document('MATERIAL_IN', env)
        for row in mtlin:
            date = row[2]
            if date > parts_last_updated:
                quantity_in = row[1]
                material_name = row[5]
                if material_name in materials:
                    materials[material_name] += int(quantity_in)

        # subtract delivery from stocks
        rekapdo = get_report_document('DELIVERY_OUT', env)
        for row in rekapdo:
            date = row[5]
            if date > parts_last_updated:
                delivered_quantity = row[3]
                name = row[6]
                if name in name2idx:
                    part_idx = name2idx[name]
                    process_idx = -1 # Fin material
                    parts[part_idx].processes[process_idx].stock -= int(delivered_quantity)

        return parts, materials


def get_spk_dataframe_display(machine_tasks):
    from constants import tonnage2name
    tasks = [(tonnage_idx, task) for tonnage_idx, tasks_ in enumerate(machine_tasks) for task in tasks_]

    df_tasks = pd.DataFrame({
        "No": [i+1 for i in range(len(tasks))],
        "Mesin": [tonnage2name[tonnage_idx] for tonnage_idx, _ in tasks],
        "Part Number": [task.part_id for _, task in tasks],
        "Part Name": [task.part_name for _, task in tasks],
        "Process Name": [task.process_name for _, task in tasks],
        "OP": [task.op for _, task in tasks],
        "Quantity": [task.quantity for _, task in tasks],
        "Material Spec Size": [task.material if task.op == 'OP10' else '' for _, task in tasks],
        "Delete": ['`DELETE`' for _ in tasks]
    })

    return df_tasks

def get_low_material_task_display(low_material_tasks):
    return pd.DataFrame({
        "No": [i+1 for i in range(len(low_material_tasks))],
        "Part Name": [task.part_name for task in low_material_tasks],
        "Material Spec Size": [task.material for task in low_material_tasks],
        "Kebutuhan": [task.necessity for task in low_material_tasks],
        "BQ": [task.multiplier for task in low_material_tasks]
    })


def get_part_stock_dataframe_display(parts):
    return pd.DataFrame({
        "Part Name": [part.name for part in parts],
        "Stok": ["; ".join([f"{process.process_name}: {process.stock}" for process in part.processes]) for part in parts],
        "3HK": [part.ideal_stock_3hk for part in parts],
        "Status": ["OK" if part.processes[-1].stock >= int(part.ideal_stock_3hk) else "Stok Kurang" for part in parts]
    })

def get_material_stock_dataframe_display(materials):
    return pd.DataFrame({
        "Nama Material": [m for m in materials.keys()],
        "Stok": [materials[m] for m in materials.keys()]
    })

# Example usage:
if __name__ == '__main__':
    processes = [
        Process(process_name="Blank", tonnage=160, tonnage_alternatives=[200], stock=150), 
        Process(process_name="Bending", tonnage=160, tonnage_alternatives=[200], stock=300), 
        Process(process_name="Bending 2", tonnage=75, tonnage_alternatives=[110, 150], stock=40), 
        Process(process_name="Restrike", tonnage=150, tonnage_alternatives=[110, 75], stock=150), 
        Process(process_name="Piercing", tonnage=55, tonnage_alternatives=[55, 75], stock=1000)
        ]    
    part1 = Part(name="Component A", id="aaa-gvdvdv-ddwd", customer="PPII", ideal_stock_3hk=300, material="material", processes=processes)

    print(part1.name)  # Output: Component A
    print(part1.id)  # Output: 123456
    print(part1.material)  # Output: MaterialInfo(material_name='Steel', dimension=Dimension(thickness=5, weight=10, height=20))
    print(part1.processes)  # Output: [Process(process_name='Cutting', tonnage=100), Process(process_name='Welding', tonnage=50)]
