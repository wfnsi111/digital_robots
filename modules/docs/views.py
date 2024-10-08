from fastapi import APIRouter, Depends, File, UploadFile, Form

from sqlalchemy.orm import Session
from modules.docs.crud import docs_crud
from db_mysql.session import get_db
from config.config import CHROMA_CONFIG
from modules.user.views import get_current_active_user
from .schema_models import *
from .. import knowledge_func
import os

from mylog.log import logger

router = APIRouter()
# router = APIRouter(dependencies=[Depends(verify_token)])    # 验证token


@router.get("/list", response_model=ListDocumentsResponse, summary="知识库列表")
async def list_documents(digital_role: str = None, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    docs_list = []
    docs = docs_crud.list_docs(db, user_id=user.id, digital_role=digital_role)
    for document in docs:
        docs_list.append(
            {
                "id": document.id,
                'file_name': document.file_name,
                'update_time': document.update_time,
                'status': document.file_status,
            }
        )

    return ListDocumentsResponse(documents=docs_list)


@router.post("/delete", response_model=DeleteDocumentsResponse, summary="删除文档")
async def delete_documents(request: DeleteDocumentsRequest, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    # user_id = request.user_id
    doc_id = request.doc_id
    filename = request.filename
    digital_role = request.digital_role
    # 删除向量数据库数据
    res = knowledge_func.delete_docs(user, filename=filename, digital_role=digital_role)
    if res == 'no data':
        return DeleteDocumentsResponse(result=res)

    # 删除mysql数据库数据
    res = docs_crud.delete_docs(db, doc_id)
    return DeleteDocumentsResponse(result=res)


@router.post("/upload", response_model=AddDocumentsResponse, summary='上传文档')
async def upload_documents(digital_role: str = Form(),
                           files: List[UploadFile] = File(...),
                           db: Session = Depends(get_db),
                           user=Depends(get_current_active_user)):
    file_list = []
    docs_path = CHROMA_CONFIG["doc_source"]
    try:
        for i in files:
            filename = os.path.join(docs_path, i.filename)
            file_list.append(filename)
            with open(filename, 'wb') as f:
                f.write(await i.read())

        fileinfo = {
            "file_list": file_list,
            'digital_role': digital_role,
            'attribute': 'knowledge',
            'user_id': user.id
        }

        knowledge_func.add_docs(fileinfo)  # 添加知识库
        docs_crud.upload_docs(db, fileinfo["file_list"], fileinfo["digital_role"], fileinfo["attribute"],
                              fileinfo["user_id"], file_status='成功')
        logger.info(f'{file_list}文件上传成功')
        return AddDocumentsResponse(result='ok')
    except Exception as e:
        logger.error(f'{file_list}文件上传失败')
        logger.error(e)
        return AddDocumentsResponse(result='error')


@router.post("/query", summary="单独查询知识库")
async def query_documents(request: QueryDocumentsRequest, user=Depends(get_current_active_user)):
    prompt = request.prompt
    k = request.k
    # filter = {
    #     'role': request.digital_role,
    #     'attribute': 'knowledge',  # 属性
    #     # 'user_id': 1,
    #
    # }
    filter = {
        "$and": [
            {'digital_role': request.digital_role},
            {'attribute': 'knowledge'},
            {'user_id': user.id},
        ]
    }

    knowledge_info = knowledge_func.similarity_search(prompt, k=k, filter=filter)

    return {'msg': knowledge_info}
