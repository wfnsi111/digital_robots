from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config.config import CHROMA_CONFIG
from datetime import datetime
import os
from typing import List
from multiprocessing import Pool
from tqdm import tqdm
from langchain_community.document_loaders import (
    CSVLoader, EverNoteLoader,
    PDFMinerLoader, TextLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader, UnstructuredMarkdownLoader,
    UnstructuredODTLoader, UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

LOADER_MAPPING = {
    ".csv": (CSVLoader, {}), ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}), ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}), ".odt": (UnstructuredODTLoader, {}), ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}), ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".xls": (UnstructuredExcelLoader, {}), ".xlsx": (UnstructuredExcelLoader, {}),
}

embedding_function = HuggingFaceEmbeddings(model_name=CHROMA_CONFIG['embedding_model'])
vector = Chroma(persist_directory=CHROMA_CONFIG['db_source'], embedding_function=embedding_function)


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(file_list: List[str]) -> List[Document]:
    """
    加载文档
    """
    # with Pool(processes=os.cpu_count()) as pool:
    #     results = []
    #     with tqdm(total=len(file_list), desc='Loading new documents', ncols=80) as pbar:
    #         for i, docs in enumerate(pool.imap_unordered(load_single_document, file_list)):
    #             results.extend(docs)
    #             pbar.update()
    #
    # return results

    results = []
    for file in file_list:
        results.extend(load_single_document(file))
    return results


def set_metadata(documents, set_filename=True, **kwargs):
    # 设置 metadata
    if set_filename:
        for document in documents:
            source = document.metadata['source']
            filename = os.path.split(source)[-1]
            document.metadata.update(kwargs)
            document.metadata['filename'] = filename
    else:
        [document.metadata.update(kwargs) for document in documents]


def add_docs(fileinfo):
    file_list: list = fileinfo['file_list']
    digital_role = fileinfo['digital_role']
    attribute = fileinfo['attribute']
    user_id = fileinfo['user_id']
    documents = load_documents(file_list)
    if not documents:
        print("No new documents to load")
    print(f"Loaded {len(documents)} new documents.")
    set_metadata(documents, set_filename=True, digital_role=digital_role, attribute=attribute, user_id=user_id)

    # 分词
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHROMA_CONFIG['chunk_size'],
                                                   chunk_overlap=CHROMA_CONFIG['chunk_overlap'])
    texts = text_splitter.split_documents(documents)

    print(f"Creating embeddings. May take some minutes...")
    chroma_db = Chroma.from_documents(texts, embedding_function, persist_directory=CHROMA_CONFIG['db_source'])
    chroma_db.persist()
    chroma_db = None

    return 'ok'


def delete_docs(doc_id=None, digital_role=None, attribute=None, filename=None):
    # 向量数据库-删除
    try:
        result = vector.get(where={"filename": filename})
        if result['ids']:
            vector.delete(result['ids'])
            return 'ok'
    except Exception as e:
        print(e)
        raise


def similarity_search(prompt, k, filter=None):
    response = vector.similarity_search(prompt, k=k, filter=filter)

    # 服务端简单日志
    print("搜索结束")
    log = '", prompt:"' + prompt + '"response:"' + repr(response) + '"'
    print(datetime.now().time(), log)
    # 合并检索结果

    merge_message_list = [c.page_content for c in response]
    return merge_message_list
