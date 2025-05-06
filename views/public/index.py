import streamlit as st
from streamlit.errors import StreamlitSetPageConfigMustBeFirstCommandError

from components import header_component

def index_view():
    try:
        st.set_page_config(
            page_title="IIIF Image Manager",
            page_icon="🖼️",
            layout="wide"
        )
    except StreamlitSetPageConfigMustBeFirstCommandError:
        pass

    header_component(
        title='Streamlit-IIIF',
        desc='Revolutionizing Digital Exhibitions with AI and IIIF Integration'
    )

    # Updated HTML with style that matches the header component
    html_content = """
    <style>
        .features {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 1.5rem 0;
        }
        .feature-card {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            width: 48%;
            border: 1px solid #dee2e6;
            transition: transform 0.2s ease;
        }
        .feature-card:hover {
            transform: translateY(-3px);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.8rem;
            color: #212529;
        }
        .feature-card h2 {
            font-size: 1.4rem;
            margin-bottom: 0.8rem;
            font-weight: 500;
            color: #212529;
        }
        .feature-card p {
            font-size: 1rem;
            color: #6c757d;
        }
        .section-divider {
            height: 1px;
            background: #dee2e6;
            margin: 2rem 0;
        }
        .demo-section {
            background: #f8f9fa;
            padding: 2rem 1.5rem;
            border-radius: 5px;
            margin-top: 1.5rem;
            border: 1px solid #dee2e6;
        }
        .demo-section h2 {
            color: #212529;
            font-size: 1.8rem;
            margin-bottom: 1rem;
            text-align: center;
            font-weight: 500;
        }
        .demo-section p {
            color: #6c757d;
            text-align: center;
            max-width: 800px;
            margin: 0 auto 1.5rem auto;
        }
        .collection-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            justify-content: center;
            margin: 1.5rem 0;
        }
        .collection-item {
            background: white;
            border-radius: 5px;
            padding: 1.5rem;
            width: calc(50% - 1rem);
            border: 1px solid #dee2e6;
            transition: transform 0.2s ease;
        }
        .collection-item:hover {
            transform: translateY(-3px);
        }
        .collection-item h3 {
            color: #212529;
            margin-bottom: 0.5rem;
            font-weight: 500;
            font-size: 1.2rem;
        }
        .collection-icon {
            font-size: 1.8rem;
            margin-bottom: 0.8rem;
            color: #212529;
        }
        .collection-item p {
            color: #6c757d;
            font-size: 1rem;
        }
        @media (max-width: 768px) {
            .feature-card, .collection-item {
                width: 100%;
            }
        }
    </style>

    <div id="features" class="features">
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h2>AI-Powered Platform</h2>
            <p>Built entirely on Streamlit with seamless AI integration, ensuring an intuitive user experience while leveraging advanced machine learning models.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🏷️</div>
            <h2>Automatic Image Annotation</h2>
            <p>Say goodbye to manual tagging! Our AI analyzes and labels images with relevant metadata, saving time and ensuring consistency.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h2>Multimodal Image Retrieval</h2>
            <p>Search and retrieve images using a combination of text, visual, and other entity types for powerful organization of large collections.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h2>IIIF Intelligent Agent</h2>
            <p>Our intelligent agent leverages the International Image Interoperability Framework to provide smart, context-aware interactions with your collections.</p>
        </div>
    </div>

    <div class="section-divider"></div>

    <div class="demo-section">
        <h2>Featured Collections</h2>
        <p>Explore our curated digital exhibitions showcasing culturally significant materials from around the world.</p>

        <div class="collection-container">
            <div class="collection-item">
                <div class="collection-icon">🏛️</div>
                <h3>The Museum of Islamic Art, Qatar</h3>
                <p>A stunning collection of Islamic artifacts spanning three continents and 1,400 years, courtesy of WikiMedia and Google Art Project.</p>
            </div>

            <div class="collection-item">
                <div class="collection-icon">📚</div>
                <h3>The Qatar National Library</h3>
                <p>Rare manuscripts and historical documents from the Middle East and beyond, available via the World Digital Library initiative.</p>
            </div>
        </div>
    </div>
    """

    st.html(html_content)


public_home_page = st.Page(index_view, url_path='', title="Home", icon="🏠", default=True)