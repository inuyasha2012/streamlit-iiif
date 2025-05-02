import uuid
from typing import List, Optional, Any, Dict, Tuple
from langchain_core.documents import Document
from langchain.retrievers import MultiVectorRetriever


class RetrieverRepository:

    def __init__(self, retriever: MultiVectorRetriever):
        self.retriever = retriever

    def add_documents(self, doc_summaries: List[Any], doc_contents: List[Any]) -> List[str]:
        """
        添加文档到检索器

        Args:
            doc_summaries: 文档摘要列表
            doc_contents: 文档内容列表

        Returns:
            文档ID列表
        """
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={self.retriever.id_key: doc_ids[i]})
            for i, s in enumerate(doc_summaries)
        ]
        self.retriever.vectorstore.add_documents(summary_docs)
        self.retriever.docstore.mset(list(zip(doc_ids, doc_contents)))
        return doc_ids