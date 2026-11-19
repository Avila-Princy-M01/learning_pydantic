def insert_patient_data(name: str, age: int):
    if type(name) == str and type(age) == int:
        print(name)
        print(age)
        print("inserted into db")
    else:
        raise TypeError("Incorrect data type")

def update_patient_data(name: str, age: int):
    if type(name) == str and type(age) == int:
        print(name)
        print(age)
        print("updated in the db")
    else:
        raise TypeError("Incorrect data type")

insert_patient_data("avila", "twenty-two")
insert_patient_data("avila", "22")
insert_patient_data("avila", 22)