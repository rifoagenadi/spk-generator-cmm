
from typing import NamedTuple, List
from constants import SHIFT_HOUR, material_stock

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
    if machine_tonnage <= 150:
        return 200*SHIFT_HOUR
    elif machine_tonnage < 300:
        return 250*SHIFT_HOUR
    else:
        return 320*SHIFT_HOUR

def get_prioritized_tasks(parts, top_n=50):
    sorted_parts = sorted(parts, key=lambda x: x.ideal_stock_3hk - x.processes[-1].stock, reverse=True)

    # decompose to tasks
    sorted_tasks = []
    for part in sorted_parts:
        neccesity = part.ideal_stock_3hk - part.processes[-1].stock
        initial_necessity = neccesity
        if neccesity < 0:
            break
        for i, process in enumerate(part.processes[::-1]): # iterate from last process to first process
            op_id = len(part.processes) - i
            if i == len(part.processes)-1: # if first process
                quantity = min(neccesity, material_stock[part.material])
            else:
                prev_step_stock = part.processes[i+1].stock
                quantity = neccesity if neccesity <=  prev_step_stock else min(process.stock, get_max_capacity(process.tonnage))
                neccesity -= quantity
            
            if quantity > 0:
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
    max_capacities = [get_max_capacity(t.tonnage) for t in sorted_tasks]
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
        
        sorted_tasks.pop(0)
    
    return machine_tasks
                