
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
    minimum_production_quantity: int
    multiplier: float

def get_max_capacity(machine_tonnage):
    if machine_tonnage <= 150: # PP
        return 2800
    elif machine_tonnage < 300: # MP
        return 2000
    else: # LP
        return 1400 

def get_prioritized_tasks(parts, top_n=50, check_material_availability=True):
    sorted_parts = sorted(parts, key=lambda x: int(x.ideal_stock_3hk) - int(x.processes[-1].stock), reverse=True)

    # decompose to tasks
    sorted_tasks = []
    low_material_tasks = []
    for part in sorted_parts:
        initial_necessity = int(part.ideal_stock_3hk) - int(part.processes[-1].stock)
        current_necessity = part.ideal_stock_3hk
        
        # first pass: count quantity for each process
        neccesities = [0] * len(part.processes)
        for i, process in enumerate(part.processes[::-1]):
            current_necessity = int(current_necessity) - int(process.stock)
            neccesities[len(part.processes)-1-i] = current_necessity

        if check_material_availability:
            # second pass: count actual quantity (compared to available material or WIP stock)
            multiplier = part.material_multiplier
            producible_quantity = int(multiplier * materials[part.material]) if multiplier >= 1 else int(materials[part.material]/multiplier)
            prev_stock = producible_quantity
            for i, process in enumerate(part.processes):
                current_necessity = neccesities[i]
                if i == 0:
                    if materials[part.material] <= 0 and initial_necessity > 0:
                        current_task = Task(part_name=f"{part.id} - {part.name} - {part.customer}",
                                        process_name=process.process_name,
                                        op=f"OP10",
                                        quantity=initial_necessity,
                                        tonnage=process.tonnage,
                                        tonnage_alternatives=process.tonnage_alternatives,
                                        material=part.material,
                                        minimum_production_quantity=part.minimum_production_quantity,
                                        necessity=initial_necessity,
                                        multiplier=part.material_multiplier)
                        low_material_tasks.append(current_task)
                        continue
                    if initial_necessity >= 0:
                        quantity = max(current_necessity, part.minimum_production_quantity)
                        quantity = min(quantity, prev_stock)
                    else:
                        quantity = prev_stock if prev_stock >= part.minimum_production_quantity else 0
                    materials[part.material] -= int(quantity / multiplier) if multiplier >= 1 else int(quantity*multiplier)
                else:
                    quantity = min(current_necessity, prev_stock)
                prev_stock = process.stock + quantity
                if quantity > 0:
                    op_id = i+1
                    current_task = Task(part_name=f"{part.id} - {part.name} - {part.customer}",
                                        process_name=process.process_name,
                                        op=f"OP{op_id}0",
                                        quantity=quantity,
                                        tonnage=process.tonnage,
                                        tonnage_alternatives=process.tonnage_alternatives,
                                        material=part.material,
                                        minimum_production_quantity=part.minimum_production_quantity,
                                        necessity=initial_necessity,
                                        multiplier=part.material_multiplier)
                    sorted_tasks.append(current_task)
        else:
            for i, process in enumerate(part.processes):
                current_necessity = neccesities[i]
                op_id = i+1
                current_task = Task(part_name=f"{part.id} - {part.name} - {part.customer}",
                                    process_name=process.process_name,
                                    op=f"OP{op_id}0",
                                    quantity=current_necessity,
                                    tonnage=process.tonnage,
                                    tonnage_alternatives=process.tonnage_alternatives,
                                    material=part.material,
                                    necessity=initial_necessity,
                                    multiplier=part.material_multiplier)
                sorted_tasks.append(current_task)
    

    return sorted_tasks[:top_n], low_material_tasks

from constants import machine_tonnages
def assign_task_to_machines(sorted_tasks):
    unassigned_tasks = []
    max_capacities = [get_max_capacity(m) for m in machine_tonnages]
    current_workload = [0] * len(machine_tonnages)
    are_loaded = [False] * len(machine_tonnages)
    machine_tasks = [[] for _ in range(len(machine_tonnages))]
    while not all(are_loaded) and sorted_tasks:
        task = sorted_tasks[0]
        assigned = False
        machine_idx = machine_tonnages.index(task.tonnage)

        if not are_loaded[machine_idx]:
            current_workload_plus_this_task = current_workload[machine_idx] + task.quantity
            if not current_workload_plus_this_task > max_capacities[machine_idx]:
                current_workload[machine_idx] += task.quantity
                machine_tasks[machine_idx].append(task)
                assigned = True
            else:
                doable_workload = max_capacities[machine_idx] - current_workload[machine_idx]
                if doable_workload >= task.minimum_production_quantity:
                    current_workload[machine_idx] += doable_workload
                    machine_tasks[machine_idx].append(task)
                    assigned = True

            if current_workload[machine_idx] >= max_capacities[machine_idx]:
                are_loaded[machine_idx] = True
            
        else:
            for alt in task.tonnage_alternatives:
                alt_idx = machine_tonnages.index(alt)

                if not are_loaded[alt_idx]:
                    current_workload_plus_this_task = current_workload[alt_idx] + task.quantity
                    if not current_workload_plus_this_task > max_capacities[alt_idx]:
                        current_workload[alt_idx] += task.quantity
                        machine_tasks[alt_idx].append(task)
                        assigned = True
                    else:
                        doable_workload = max_capacities[alt_idx] - current_workload[alt_idx]
                        if doable_workload >= task.minimum_production_quantity:
                            current_workload[alt_idx] += doable_workload
                            machine_tasks[alt_idx].append(task)
                            assigned = True

                    if current_workload[alt_idx] >= max_capacities[alt_idx]:
                        are_loaded[alt_idx] = True
                    
                    break
        
        if not assigned:
            unassigned_tasks.append(task)
        sorted_tasks.pop(0)
    
    return machine_tasks, unassigned_tasks
