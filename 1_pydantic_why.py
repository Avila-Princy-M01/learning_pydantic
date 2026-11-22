from pydantic import BaseModel
from typing import List, Dict, Optional

class Patient(BaseModel):
    name : str
    age: int
    weight: float
    #you can set default values
    married: bool = False
    #when you make a feild optional it's necessary to give a default value too!!
    allergies: Optional[List[str]] = None 
    contact_details: Dict[str, str]

def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.weight)
    print(patient.married)
    print(patient.allergies)
    print(patient.contact_details)
    print("inserted into db")
    print()

def update_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print("updated into db")

patient_info = {"name": "Avila", "age": 22, "weight": 49, "contact_details":{"email": "abc@gmail.com", "phone":"123456789"}}


patient1 = Patient(**patient_info)

insert_patient_data(patient1)
update_patient_data(patient1)
