from part import Process, Part

import random
from faker import Faker

fake = Faker()

dummy_parts = []
for _ in range(100):
    name = fake.word() + " " + fake.word() + " " + fake.word()
    id = str(fake.uuid4())
    customer = fake.company()
    ideal_stock_3hk = random.randint(900 // 100, 3000 // 100) * 100
    material_name = fake.word()
    material_t, material_w, material_l = random.uniform(0, 1.7), random.uniform(75, 250), random.uniform(100, 1200)
    material = f"{material_name} {str(round(material_t,2))}x{str(round(material_w,2))}x{str(round(material_l,2))}"
    # Generate 2, 3, or 4 processes randomly
    num_processes = random.choice([2, 3, 4, 5])
    process_names = ["Blank", "Bending", "Bending 2", "Restrike", "Piercing"]
    selected_processes = process_names[:num_processes]
    
    processes = []
    for i, process_name in enumerate(selected_processes):
        tonnage_options = [55, 75, 110, 150, 160, 200, 300, 350]
        tonnage = random.choice(tonnage_options)
        tonnage_idx = tonnage_options.index(tonnage)
        alternatives_num = random.choice([0, 1, 2])
        tonnage_alternatives = [t for t in tonnage_options[max(tonnage_idx-alternatives_num, 0):tonnage_idx+2] if t != tonnage]
        processes.append(Process(process_name=process_name, tonnage=tonnage, tonnage_alternatives=tonnage_alternatives, stock=random.randint(500 // 100, 4000 // 100) * 100))
    
    part = Part(name=name, id=id, customer=customer, ideal_stock_3hk=ideal_stock_3hk, material=material, processes=processes)
    dummy_parts.append(part)

import pickle as pkl

pkl.dump(dummy_parts, open('data/dummy_parts.pickle', 'wb'))