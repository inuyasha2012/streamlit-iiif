from dependency_injector import containers, providers
import streamlit as st
from langchain.retrievers import MultiVectorRetriever
from langchain.storage import LocalFileStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from services import ImageService, ManifestService
from services.ai import (
    EmbeddingService,
    AnnotationService,
    RAGService,
    AgentService
)
from storage import GithubIIIF3Storage, LocalIIIF3Storage
from repositories.entities import ImageRepository, ManifestRepository
from repositories.ai import RetrieverRepository
from utils.tools import ImageAnnoTool

class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    connection = providers.Singleton(
        providers.Callable(
            st.connection,
            name='sql'
        )
    )

    storage = providers.Selector(
        config.storage.type,
        github=providers.Singleton(
            GithubIIIF3Storage,
            access_token=config.storage.access_token,
            repo_name=config.storage.repo_name,
            image_dir=config.storage.image_dir,
            manifest_dir=config.storage.manifest_dir
        ),
        local=providers.Singleton(
            LocalIIIF3Storage,
            base_dir=config.storage.base_dir,
            image_dir=config.storage.image_dir,
            manifest_dir=config.storage.manifest_dir
        )
    )

    image_repository = providers.Singleton(
        ImageRepository,
        connection=connection
    )

    manifest_repository = providers.Singleton(
        ManifestRepository,
        connection=connection
    )

    image_service = providers.Factory(
        ImageService,
        repository=image_repository,
        storage=storage,
        base_url=config.base.url
    )

    manifest_service = providers.Factory(
        ManifestService,
        repository=manifest_repository,
        storage=storage,
        base_url=config.base.url
    )

    vl_llm_client = providers.Singleton(
        ChatOpenAI,
        api_key=config.openai.vl.api_key,
        model=config.openai.vl.model,
        base_url=config.openai.vl.base_url,
        temperature=0,
    )

    text_llm_client = providers.Singleton(
        ChatOpenAI,
        api_key=config.openai.text.api_key,
        model=config.openai.text.model,
        base_url=config.openai.text.base_url,
        temperature=0,
    )

    embedding_llm_client = providers.Singleton(
        OpenAIEmbeddings,
        api_key=config.openai.embedding.api_key,
        model=config.openai.embedding.model,
        base_url=config.openai.embedding.base_url,
        check_embedding_ctx_length=False,
    )

    doc_store = providers.Singleton(
        LocalFileStore,
        root_path="./.persistence/storage"
    )

    vector_store = providers.Singleton(
        Chroma,
        collection_name="iiif",
        embedding_function=embedding_llm_client,
        persist_directory=config.openai.embedding.chroma_path,
    )

    retriever = providers.Singleton(
        MultiVectorRetriever,
        vectorstore=vector_store,
        docstore=doc_store,
        id_key='doc_id',
    )

    retriever_repository = providers.Factory(
        RetrieverRepository,
        retriever=retriever,
    )

    embedding_service = providers.Factory(
        EmbeddingService,
        vl_llm_client=vl_llm_client,
        text_llm_client=text_llm_client,
        retriever_repository=retriever_repository
    )

    image_anno_tool = providers.Singleton(
        ImageAnnoTool,
        vl_llm_client=vl_llm_client,
    )

    annotation_service = providers.Factory(
        AnnotationService,
        anno_tool=image_anno_tool
    )

    rag_service = providers.Factory(
        RAGService,
        retriever_repository=retriever_repository,
        vl_llm_client=vl_llm_client,
    )

    agent_service = providers.Factory(
        AgentService,
        text_llm_client=text_llm_client,
        vl_llm_client=vl_llm_client,
    )

    wiring_config = containers.WiringConfiguration(
        modules=[
            'views.public.collection',
            'views.public.show',
            'views.admin.image',
            'views.admin.manifest',
            'views.admin.embedding',
            'views.admin.annotation',
            'views.public.rag',
            'views.public.agent',
        ]
    )

