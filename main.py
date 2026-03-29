# python -m uvicorn main:app --reload 

from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Annotated,Literal,Optional

# HTTPException - used to raise errors in API
# Like path function query can also make parameter required,default values,decription,validation (min,max,length)

import json

class Patient(BaseModel):
    patient_id: Annotated[int,Field(...,description="ID of patient",examples=[1])]
    name:Annotated[str,Field(...,description="Name of the parient",min_length=2)]
    age:Annotated[int,Field(...,description="Age of the patient",gt=0,lt=120)]
    gender:Annotated[Literal['Male','Female','Other'],Field(...,examples=['Male','Female','Other'])]
    blood_group:Annotated[str,Field(description="Blood group of the patient",examples=['A+','B+'])]
    disease:Annotated[str,Field(...,description="From Which disease patient is suffering",examples=['Malaria'],min_length=2)]
    admission_date:Optional[int]=None
    city:Annotated[str,Field(...,description="In which city patient lives",min_length=2)]



class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(description="Name of the parient",min_length=2)]=None
    age:Annotated[Optional[int],Field(description="Age of the patient",gt=0,lt=120)]=None
    gender:Annotated[Optional[Literal['Male','Female','Other']],Field(examples=['Male','Female','Other'])]=None
    blood_group:Annotated[Optional[str],Field(description="Blood group of the patient",examples=['A+','B+'])]=None
    disease:Annotated[Optional[str],Field(description="From Which disease patient is suffering",examples=['Malaria'],min_length=2)]=None
    admission_date:Optional[int]=None
    city:Annotated[Optional[str],Field(description="In which city patient lives",min_length=2)]=None


app=FastAPI()


@app.get('/about') #we have created route (@app) if someone clicks on www.xxx./about
def about():
    return {'message:Hi, this is Saurav Dixit Data Scientist and AI/ML Engineer'} #they will get this message


# We are creating a api which will have patient data

@app.get('/')
def hello():
    return {'message':'Patient management system api'}


# our first endpoint will view it will give the whole data present in the patient file 
def  load_data():
    with open('Patients.json','r') as f:
        data = json.load(f)
    return data 

# for post endpoint we need to create func save file 
def save_data(data):
    with open('Patients.json','w') as f:
        json.dump(data,f)

@app.get('/view')
def view():
    data = load_data()  # after clicking on this endpoint it will give all the data, using load_data function

    return data


# Second endpoint will be getting info of patient by providing patient id 
@app.get('/patient/{patient_id}') # here {patient_id} is path parameter.
def view_patient(patient_id:int = Path(...,description="Unique ID of the patient",example="1")):#... it indicated the para meter is required
    data =load_data()
    for patient in data: # we will apply this loop to all patient in data 
        if patient["patient_id"] == patient_id: # patient id = patient id given by user 
            return patient # return the info of patient and if no patient id is their raise an error

    raise HTTPException(status_code=404,detail="No patient found") # status code tells client what error ocurred


# third endpoint will be created on the basis of sorting it will have two query sort by = age and order = ascending/descending
@app.get('/sort')
def sorting(sort_by:str=Query(...,description="which para meter you want to sort"),order_by:str=Query(description="Sort by ascending or descending")):

    if order_by not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid Order. Select between asc or desc")

    data = load_data() # first we will load data 

    sorted_data=sorted(data,key=lambda x: x[sort_by],
        reverse=True if order_by == "desc" else False) # then we will sort the values on the basis of above parameter given by the user
    # sorted() function helps to sort the data. if we want to sort on the basis of decs order we will just keep reverse = true

    return sorted_data #then we will return the sorted data

# fourth endpoint will  be post endpoint based on our pydantic model and it will take
# patient data from user and create a patient info database
@app.post('/create')
def create_patient(patient:Patient): # and this function will perform in 3 steps
    # Load the data
    data=load_data()

    # Check if patient already exist
    for p in data:
     if p["patient_id"] == patient.patient_id:
        raise HTTPException(status_code=400,detail="Patient already exist")
    
    # new patient add to data base
    data.append(patient.model_dump()) #the above patient is in python format dump helps to convert it into json format

    # save the data into the json file
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'New Patient added Successfully'})


# our next endpoint will be edit which will update the info of the patient.
# for that user will send an id as path parameter and and we had create a base model
@app.put('/edit/{patient_id}')
# this function will take two input  patient id and a request body which we will store in variable patient_update
def update_patient(patient_id:int,patient_update:PatientUpdate):

    # load the data
    data=load_data()

    #check if patient id exist or not
    for index, p in enumerate(data):
        if p['patient_id']==patient_id: # if the patient id is valid
            # now we will update the info provided by the user
            updated_patient_info=patient_update.model_dump(exclude_unset=True)
            # go to key value pair of updated patient info and change the value of existing patient info's key with the updated value.
            for key,value in updated_patient_info.items():
                p[key]=value
            # save the updated data
            data[index] = p
            save_data(data)

            return {
                'message':'Patient updated successfully',
                'patient':p
            }
            
    # if patient not found
    raise HTTPException(status_code=404,detail='Patient not found')
        


# Our next end point will be delete end point and it will take patient id as path parameter 
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:int):
    # load data
    data = load_data()
    # check if given patient id is present in data
    for index,p in enumerate(data):
       if p['patient_id']==patient_id: # if patient id is found
           data.pop(index) # delete the patient of that index
           save_data(data) #then save data
           return {'message':'Patient record deleted'}
    
    # raise error if patient id not found
    raise HTTPException(status_code=404,detail='No patient found')
        
    

   

