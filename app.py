__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from streamlit.connections import SQLConnection

from entity import Base
from helper.permission import is_authenticated
from views.public import public_collection_page, public_home_page, public_show_page, public_rag_page, public_agent_page
from views.auth import auth_login_page, auth_logout_page
from views.admin import admin_image_page, admin_manifest_page, admin_embedding_page, admin_annotation_page
from container import AppContainer


@st.cache_resource
def get_container():
    app_container = AppContainer()
    config_dict = st.secrets.to_dict()
    app_container.config.from_dict(config_dict)
    return app_container

def init_db(connection: SQLConnection):
    Base.metadata.create_all(bind=connection.engine)


if __name__ == '__main__':
    container = get_container()
    init_db(container.connection())
    page_dict = {'public': [public_home_page, public_collection_page, public_show_page, public_rag_page, public_agent_page]}

    if is_authenticated():
        page_dict['admin'] = [admin_image_page, admin_manifest_page, admin_embedding_page, admin_annotation_page]
        page_dict['auth'] = [auth_logout_page]
    else:
        page_dict['auth'] = [auth_login_page]

    pg = st.navigation(pages=page_dict)

    pg.run()


