import pandas as pd
from part import Part, Process
import ast

df_part = pd.read_csv('data/data_part.csv')
df_part.dropna(inplace=True)

df_material = pd.read_csv('data/data_material.csv')
multipliers = {row['Nama Material']: row['BQ'] for _, row in df_material.iterrows() if str(row['BQ']) != 'nan'}

parts = []
for i, row in df_part.iterrows():
    processes = ast.literal_eval(row['Proses'])
    stocks = ast.literal_eval(row['Stok Terkini (pcs)'])
    processes = [Process(process_name=process['process_name'], tonnage=process['tonnage_std'], tonnage_alternatives=process['tonnage_alternatives'], stock=stock) for process, stock in zip(processes, stocks)]
    part = Part(name=row['Nama Part'],
         id=row['ID Part'],
         customer=row['Customer'],
         ideal_stock_3hk=row['Std Stock (3HK)'],
         material=row['Material'],
         material_multiplier=multipliers[row['Nama Part']] if row['Nama Part'] in multipliers else 1.0,
         minimum_production_quantity=row['Minimal Produksi'],
         processes=processes)
    parts.append(part)

import pickle as pkl
pkl.dump(parts, open('data/parts.pickle', 'wb'))