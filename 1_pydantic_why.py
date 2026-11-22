from pydantic import BaseModel, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : Annotated[str, Field(max_length=50, title="Name of the patient", description="Enter the name of the patient within 50 chars", examples=["Ana", "Bob"])]
    email: EmailStr
    age: int = Field(gt=0, lt=120)
    weight: Annotated[float, Field(gt=0, strict=True)]
    linkedin_url: AnyUrl
    #you can set default values
    married: bool = Annotated(bool, Field(default=None, description="Is the patient married or not"))
    #when you make a feild optional it's necessary to give a default value too!!
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length = 5)]
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

patient_info = {"name": "Avila", "email": "avila.m@gmail.com", "age": 22, "weight": 49, "linkedin_url": "https://www.linkedin.com/in/avila-princy-m-633820307/", "allergies": ["pollen", "dust"], "contact_details":{"phone": "123456789"}}


patient1 = Patient(**patient_info)

insert_patient_data(patient1)
update_patient_data(patient1)
