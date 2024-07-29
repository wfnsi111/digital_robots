from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .crud import skill_crud
from db_mysql.session import get_db
from modules.user.views import get_current_active_user
from .schema_models import *
from mylog.log import logger
import json

router = APIRouter()
# router = APIRouter(dependencies=[Depends(verify_token)])    # 验证token


@router.post("/create", summary="创建技能")
async def create_skill(request: SkillModel, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    try:
        skill = skill_crud.create_skill(db, user.id, request.skill_name, request.skill_id, request.description,
                                        request.params, request.other)

        logger.info(f'{user.username} successfully created skill: {request.skill_name}.')
        return skill
    except Exception as e:
        logger.error(f'{user.username} failed to create skill: {request.skill_name}.')
        raise


@router.get("/list", response_model=list[SkillModel], summary="技能库列表")
async def list_skill(user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    skills = skill_crud.list_skill(db, user.id)

    skill_dict = {}
    for skill in skills:
        try:
            skill_dict[skill.skill_name] = {
                "name": skill.skill_name,  # 函数名字
                "description": skill.description,  # 函数描述：大模型通过函数的描述，来选择是否调用函数
                "parameters": json.loads(skill.params)
            }
        except json.decoder.JSONDecodeError as e:
            logger.error(f'JSON格式错误：{skill.params}')
    print(skill_dict)

    return skills


@router.post("/delete", response_model=SkillModel, summary="删除技能")
async def delete_skill(request: DeleteSkillRequest, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    skill = skill_crud.delete_skill(db, request.id)
    return skill
