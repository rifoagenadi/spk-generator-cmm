
from typing import NamedTuple, List
from constants import SHIFT_HOUR
from part import materials

class Task(NamedTuple):
    part_name: str
    process_name: str
    op: str
    quantity: int
    tonnage: int
    tonnage_alternatives: List[int]
    material: str
    necessity: int

def get_max_capacity(machine_tonnage):
    if machine_tonnage <= 150: # PP
        return 2800
    elif machine_tonnage < 300: # MP
        return 2000
    else: # LP
        return 1400 

def get_prioritized_tasks(parts, top_n=50):
    sorted_parts = sorted(parts, key=lambda x: int(x.ideal_stock_3hk) - int(x.processes[-1].stock), reverse=True)

    # decompose to tasks
    sorted_tasks = []
    for part in sorted_parts:
        initial_necessity = int(part.ideal_stock_3hk) - int(part.processes[-1].stock)
        current_necessity = part.ideal_stock_3hk
        
        # first pass: count quantity for each process
        neccesities = [0] * len(part.processes)
        for i, process in enumerate(part.processes[::-1]):
            current_necessity = int(current_necessity) - int(process.stock)
            neccesities[len(part.processes)-1-i] = current_necessity

        # second pass: count actual quantity (compared to available material or WIP stock)
        multiplier = part.material_multiplier
        producible_quantity = int(multiplier * materials[part.material]) if multiplier >= 1 else int(materials[part.material]/multiplier)
        prev_stock = producible_quantity
        for i, process in enumerate(part.processes):
            current_necessity = neccesities[i]
            if i == 0:
                if materials[part.material] <= 0:
                    continue
                quantity = min(current_necessity, prev_stock)
                materials[part.material] -= quantity
            else:
                quantity = min(current_necessity, prev_stock)
            prev_stock = process.stock + quantity
            if quantity > 0:
                op_id = i+1
                current_task = Task(part_name=part.name,
                                    process_name=process.process_name,
                                    op=f"OP{op_id}0",
                                    quantity=quantity,
                                    tonnage=process.tonnage,
                                    tonnage_alternatives=process.tonnage_alternatives,
                                    material=part.material,
                                    necessity=initial_necessity)
                sorted_tasks.append(current_task)
    

    return sorted_tasks[:top_n]

from constants import machine_tonnages, SHIFT_HOUR
def assign_task_to_machines(sorted_tasks):
    max_capacities = [get_max_capacity(m) for m in machine_tonnages]
    current_workload = [0] * len(machine_tonnages)
    are_loaded = [False] * len(machine_tonnages)
    machine_tasks = [[] for _ in range(len(machine_tonnages))]
    while not all(are_loaded) and sorted_tasks:
        task = sorted_tasks[0]
        machine_idx = machine_tonnages.index(task.tonnage)

        if not are_loaded[machine_idx]:
            current_workload[machine_idx] += task.quantity
            if current_workload[machine_idx] >= max_capacities[machine_idx]:
                are_loaded[machine_idx] = True
            machine_tasks[machine_idx].append(task)
        else:
            for alt in task.tonnage_alternatives:
                alt_idx = machine_tonnages.index(alt)

                if not are_loaded[alt_idx]:
                    current_workload[alt_idx] += task.quantity
                    if current_workload[alt_idx] >= max_capacities[alt_idx]:
                        are_loaded[alt_idx] = True
                    machine_tasks[alt_idx].append(task)
                    break
        
        sorted_tasks.pop(0)
    
    return machine_tasks

