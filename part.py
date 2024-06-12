from typing import NamedTuple, List

class Process(NamedTuple):
    process_name: str
    tonnage: int
    tonnage_alternatives: List[int]
    stock: int

    def __str__(self):
        return f"Process: {self.process_name}, Tonnage: {self.tonnage}"

class Part:
    def __init__(self, name: str, id: str, customer:str, ideal_stock_3hk: int, material: str, processes: List[Process]):
        self.name = name
        self.id = id
        self.customer = customer
        self.ideal_stock_3hk = ideal_stock_3hk
        self.material = material
        self.processes = processes


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
