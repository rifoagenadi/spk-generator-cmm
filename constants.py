import pandas as pd
df_empty_tasks = pd.DataFrame({
    "No": [],
    "Mesin": [],
    "Part Name": [],
    "Process Name": [],
    "OP": [],
    "Quantity": [],
    "Material Spec Size": []
})  

SHIFT_HOUR = 8
machine_tonnages = [350, 300, 200, 160, 150, 150, 110, 75, 75, 55, 55, 55]
tonnage2name = [
        "LP1-350T",
        "LP2-300T",
        "MP1-200T",
        "MP2-200T",
        "PP1-150T A",
        "PP1-150T A",
        "PP2-110T",
        "PP3-75T A",
        "PP3-75T B",
        "PP4-55T A",
        "PP4-55T B",
        "PP4-55T C"
    ]

MONTH_ID_TO_NAME = ['Jan', 'Feb', "Mar", 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']