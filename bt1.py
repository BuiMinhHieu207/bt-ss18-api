from typing import List
from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel,ConfigDict,Field
from sqlalchemy import create_engine,Column,Integer,String,ForeignKey
from sqlalchemy.orm import declarative_base,sessionmaker,relationship,Session
DATABASE_URL="sqlite:///./company.db"
engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()
class Department(Base):
    __tablename__="departments"
    id=Column(Integer,primary_key=True);name=Column(String);status=Column(String);max_employees=Column(Integer)
    employees=relationship("Employee",back_populates="department")
class Employee(Base):
    __tablename__="employees"
    id=Column(Integer,primary_key=True);employee_code=Column(String);full_name=Column(String)
    department_id=Column(Integer,ForeignKey("departments.id"));department=relationship("Department",back_populates="employees")
Base.metadata.create_all(bind=engine)
class DepartmentCreate(BaseModel): name:str;status:str;max_employees:int
class EmployeeCreate(BaseModel): employee_code:str;full_name:str;department_id:int
class EmployeeResponse(BaseModel):
    id:int;employee_code:str;full_name:str;department_id:int
    model_config=ConfigDict(from_attributes=True)
class DepartmentDetailResponse(BaseModel):
    id:int;name:str;status:str;max_employees:int
    employees:List[EmployeeResponse]=Field(default_factory=list)
    model_config=ConfigDict(from_attributes=True)
app=FastAPI()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
@app.post("/departments")
def create_department(data:DepartmentCreate,db:Session=Depends(get_db)):
    d=Department(**data.model_dump());db.add(d);db.commit();db.refresh(d);return d
@app.get("/departments/{department_id}",response_model=DepartmentDetailResponse)
def get_dep(department_id:int,db:Session=Depends(get_db)):
    d=db.query(Department).filter_by(id=department_id).first()
    if not d: raise HTTPException(404,"Phòng ban không tồn tại")
    return d
@app.post("/employees",response_model=EmployeeResponse,status_code=status.HTTP_201_CREATED)
def create_emp(data:EmployeeCreate,db:Session=Depends(get_db)):
    dep=db.query(Department).filter_by(id=data.department_id).first()
    if not dep: raise HTTPException(404,"Phòng ban không tồn tại")
    if dep.status=="INACTIVE": raise HTTPException(400,"Phòng ban đã ngừng hoạt động")
    if db.query(Employee).filter_by(employee_code=data.employee_code).first():
        raise HTTPException(400,"Mã nhân viên đã tồn tại")
    if db.query(Employee).filter_by(department_id=data.department_id).count()>=dep.max_employees:
        raise HTTPException(400,"Phòng ban đã đủ nhân viên")
    e=Employee(**data.model_dump());db.add(e);db.commit();db.refresh(e);return e
