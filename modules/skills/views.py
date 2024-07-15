from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .crud import skill_crud
from db_mysql.session import get_db
from .schema_models import *

import json


router = APIRouter()


@router.post("/create", summary="创建技能")
async def create_skill(request: SkillModel, db: Session = Depends(get_db)):
    skill = skill_crud.create_skill(db, request.user_id, request.skill_name, request.skill_id, request.description,
                                    request.params, request.other)

    return skill


@router.get("/list", response_model=list[SkillModel], summary="技能库列表")
async def list_skill(user_id: int = 1, db: Session = Depends(get_db)):
    skills = skill_crud.list_skill(db, user_id)

    skill_dict = {}
    for skill in skills:
        skill_dict[skill.skill_name] = {
            "name": skill.skill_name,  # 函数名字
            "description": skill.description,  # 函数描述：大模型通过函数的描述，来选择是否调用函数
            "parameters": json.loads(skill.params)
        }

    print(skill_dict)

    return skills


@router.post("/delete", response_model=SkillModel, summary="删除技能")
async def delete_skill(request: DeleteSkillRequest, db: Session = Depends(get_db)):
    skill = skill_crud.delete_skill(db, request.id)
    return skill
