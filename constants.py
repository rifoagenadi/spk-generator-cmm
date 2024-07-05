import pandas as pd

uname_and_pass2credential = {
    ('azka', 'cmmazka'): 'ppic',
    ('junaedi', 'cmmjunaedi'): 'supervisor'
}

month_name_to_number = {
    'Januari': 1,
    'Februari': 2,
    'Maret': 3,
    'April': 4,
    'Mei': 5,
    'Juni': 6,
    'Juli': 7,
    'Agusuts': 8,
    'September': 9,
    'Oktober': 10,
    'November': 11,
    'Desember': 12
}

df_empty_tasks = pd.DataFrame({
    "No": [],
    "Mesin": [],
    "Part Name": [],
    "Process Name": [],
    "OP": [],
    "Quantity": [],
    "Material Spec Size": [],
    "Delete": []
})  

SHIFT_HOUR = 8
machine_tonnages = [350, 300, 200, 160, 150, 150, 110, 75, 75, 55, 55, 55]
tonnage2name = [
        "LP1-350T",
        "LP2-300T",
        "MP1-200T",
        "MP2-160T",
        "PP1-150T A",
        "PP1-150T B",
        "PP2-110T",
        "PP3-75T A",
        "PP3-75T B",
        "PP4-55T A",
        "PP4-55T B",
        "PP4-55T C"
    ]

MONTH_ID_TO_NAME = ['Jan', 'Feb', "Mar", 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']