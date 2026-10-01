import json
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.history import RecommendationHistory
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest
from app.services.recommendations import generate_home, generate_party, generate_jewelry
from app.config import settings

router=APIRouter(prefix="/api",tags=["planners"])

def save(db,user,planner,request_data,result):
    h=RecommendationHistory(user_id=user.id,planner=planner,request_json=json.dumps(request_data),response_json=json.dumps(result)); db.add(h); db.commit()

@router.post("/generate-home")
def home(data:HomeRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    result=generate_home(data.model_dump()); save(db,user,"home",data.model_dump(),result); return result

@router.post("/generate-party")
def party(data:PartyRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    result=generate_party(data.model_dump()); save(db,user,"party",data.model_dump(),result); return result

@router.post("/generate-jewelry")
async def jewelry(budget:float=Form(...),occasion:str=Form("wedding"),style:str=Form("elegant"),outfit_description:str=Form(""),notes:str=Form(""),outfit_image:UploadFile|None=File(None),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if budget<=0: raise HTTPException(422,"Budget must be greater than zero")
    image_bytes=None; mime=None
    if outfit_image:
        if not outfit_image.content_type or not outfit_image.content_type.startswith("image/"): raise HTTPException(400,"Outfit upload must be an image")
        image_bytes=await outfit_image.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"Image is too large")
        mime=outfit_image.content_type
    data={"budget":budget,"occasion":occasion,"style":style,"outfit_description":outfit_description,"notes":notes}
    result=generate_jewelry(data,image_bytes,mime); save(db,user,"jewelry",data,result); return result

@router.get("/history")
def history(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(RecommendationHistory).filter(RecommendationHistory.user_id==user.id).order_by(RecommendationHistory.created_at.desc()).limit(50).all()
    return [{"id":r.id,"planner":r.planner,"created_at":r.created_at.isoformat(),"request":json.loads(r.request_json),"response":json.loads(r.response_json)} for r in rows]
