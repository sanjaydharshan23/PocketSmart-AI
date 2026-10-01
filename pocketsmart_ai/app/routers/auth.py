from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.schemas import RegisterRequest, LoginRequest
from app.auth import hash_password, verify_password, create_token, COOKIE_NAME, get_current_user

router=APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(data:RegisterRequest, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email.lower()).first(): raise HTTPException(400,"Email already registered")
    user=User(name=data.name.strip(),email=data.email.lower(),password_hash=hash_password(data.password)); db.add(user); db.commit(); db.refresh(user)
    return {"message":"Registration successful"}

@router.post("/login")
def login(data:LoginRequest,response:Response,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email.lower()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
    response.set_cookie(COOKIE_NAME,create_token(user.id),httponly=True,samesite="lax",secure=False,max_age=604800)
    return {"message":"Login successful","user":{"id":user.id,"name":user.name,"email":user.email}}

@router.post("/logout")
def logout(response:Response):
    response.delete_cookie(COOKIE_NAME); return {"message":"Logged out"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id":user.id,"name":user.name,"email":user.email}
