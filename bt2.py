# BT2.py
from typing import List
from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from sqlalchemy import *
from sqlalchemy.orm import *
engine=create_engine("sqlite:///./classroom.db",connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()
class Classroom(Base):
    __tablename__="classrooms";id=Column(Integer,primary_key=True);class_name=Column(String);status=Column(String);capacity=Column(Integer);students=relationship("Student",back_populates="classroom")
class Student(Base):
    __tablename__="students";id=Column(Integer,primary_key=True);student_code=Column(String);full_name=Column(String);classroom_id=Column(Integer,ForeignKey("classrooms.id"));classroom=relationship("Classroom",back_populates="students")
Base.metadata.create_all(bind=engine)
class ClassroomDetailResponse(BaseModel):
    id:int;class_name:str;status:str;capacity:int;students:List=Field(default_factory=list);model_config=ConfigDict(from_attributes=True)
class TransferClassRequest(BaseModel): new_classroom_id:int
app=FastAPI()
def get_db():
 db=SessionLocal();yield db;db.close()
@app.get("/classrooms/{classroom_id}",response_model=ClassroomDetailResponse)
def detail(classroom_id:int,db:Session=Depends(get_db)):
 c=db.query(Classroom).filter_by(id=classroom_id).first()
 if not c: raise HTTPException(404,"Lớp học không tồn tại")
 s=db.query(Student).filter(Student.classroom_id==classroom_id).order_by(Student.id).all()
 return {"id":c.id,"class_name":c.class_name,"status":c.status,"capacity":c.capacity,"students":s}
@app.put("/students/{student_id}/transfer")
def transfer(student_id:int,data:TransferClassRequest,db:Session=Depends(get_db)):
 st=db.query(Student).filter_by(id=student_id).first()
 if not st: raise HTTPException(404,"Sinh viên không tồn tại")
 cl=db.query(Classroom).filter_by(id=data.new_classroom_id).first()
 if not cl: raise HTTPException(404,"Lớp học không tồn tại")
 if cl.status=="CLOSED": raise HTTPException(400,"Lớp học đã đóng")
 if db.query(Student).filter_by(classroom_id=data.new_classroom_id).count()>=cl.capacity: raise HTTPException(400,"Lớp học đã đủ sinh viên")
 st.classroom_id=data.new_classroom_id;db.commit();db.refresh(st);return st
