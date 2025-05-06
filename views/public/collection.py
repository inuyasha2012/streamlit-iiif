import math
import urllib.parse

import streamlit as st
from dependency_injector.wiring import Provide, inject
from typing import Annotated

from components import header_component
from services import ManifestService
from container import AppContainer


class CollectionView:

    @staticmethod
    def page_header_render():
        header_component(
            title='Browse the Collection',
            desc="This site's sample collection comprises a set of objects, each of which is represented by one or more images. The collection items in this demo are from The Museum of Islamic Art, Qatar, (courtesy of WikiMedia and Google Art Project) and The Qatar National Library (via World Digital Library)."
        )

    @staticmethod
    def page_filter_render(manifest_service):
        """Render dynamic filter components in the sidebar"""
        st.sidebar.subheader("Filter Collection")

        # Get all public manifests
        all_manifests = manifest_service.filter_by_public()

        # Dynamically extract all filterable fields from meta_data
        filter_options = {}
        for manifest in all_manifests:
            if hasattr(manifest, 'meta_data') and manifest.meta_data:
                for item in manifest.meta_data:
                    key = item["key"]
                    value = item["value"]

                    # Skip fields not needed as filter conditions (e.g., order)
                    if key.startswith('_'):
                        continue

                    if key not in filter_options:
                        filter_options[key] = set()
                    filter_options[key].add(value)

        # If no filter options extracted, return empty dictionary
        if not filter_options:
            st.sidebar.warning("No filterable fields available")
            return {}

        selected_filters = {}
        for key in sorted(filter_options.keys()):
            # Get a more friendly display name
            display_name = key.replace("_", " ").title()

            # Create multiselect in sidebar
            selected_values = st.sidebar.multiselect(
                display_name,
                options=sorted(list(filter_options[key])),
                key=f"filter_{key}"
            )
            if selected_values:
                selected_filters[key] = selected_values

        # Add an apply filter button (optional)
        if st.sidebar.button("Apply Filters", key="apply_filter", use_container_width=True):
            st.toast("Filters applied")

        # Add a reset button (optional)
        if st.sidebar.button("Reset Filters", key="reset_filter", use_container_width=True):
            st.rerun()

        return selected_filters


    @staticmethod
    @inject
    def page_body_render(manifest_service: Annotated[ManifestService, Provide[AppContainer.manifest_service]]):
        # Add filter component
        filters = CollectionView.page_filter_render(manifest_service)

        # Get all public manifests
        manifest_list = manifest_service.filter_by_public()

        # Apply filters
        if filters:
            filtered_manifests = []
            for manifest in manifest_list:
                include = True

                if hasattr(manifest, 'meta_data') and manifest.meta_data:
                    # Convert meta_data to dictionary format for easy lookup
                    meta_dict = {}
                    for item in manifest.meta_data:
                        meta_dict[item["key"]] = item["value"]

                    # Check each filter condition
                    for filter_key, filter_values in filters.items():
                        if filter_key not in meta_dict or meta_dict[filter_key] not in filter_values:
                            include = False
                            break
                else:
                    include = False  # Exclude if no meta_data

                if include:
                    filtered_manifests.append(manifest)
        else:
            filtered_manifests = manifest_list

        container =st.container()

        # Pagination setup
        items_per_page = 8  # Number of items per page
        total_items = len(filtered_manifests)
        total_pages = math.ceil(total_items / items_per_page)

        # Display pagination controls
        current_page = st.number_input(
            "Page", min_value=1, max_value=total_pages, value=1, step=1, key="pagination"
        )

        # Calculate start and end indices for the current page
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_manifests = filtered_manifests[start_idx:end_idx]

        # Display result count and pagination info
        st.write(f"Showing {len(paginated_manifests)} of {total_items} items (Page {current_page} of {total_pages})")

        # Show a hint if no filtered results
        if not paginated_manifests:
            st.warning("No matching items found. Please try different filter criteria.")
            return

        # Display paginated items
        with container:
            cols = st.columns(4)
            for i, manifest in enumerate(paginated_manifests):
                col_i = i % 4
                col = cols[col_i]
                encoded_params = urllib.parse.urlencode({'manifest_url': manifest.manifest_url})
                col.html(
                    f"""
                    <div style="border:1px solid #ddd; border-radius:8px; padding:10px; margin-bottom:15px;">
                        <a href="/show?{encoded_params}">
                            <img src="{manifest.thumbnail_url}" alt="{getattr(manifest, 'label', f'Item {i + 1}')}"
                            style="width:100%; border-radius:6px;"/>
                        </a>
                        <h4>{getattr(manifest, 'tag', f'Item {i + 1}')}</h4>
                        <p style="font-size:0.8rem;">Created: {manifest.created_at}<br>
                        Updated: {manifest.updated_at}</p>
                    </div>
                    """,
                )

    @classmethod
    def render(cls):
        st.set_page_config(
            page_title="IIIF Collection",
            page_icon="🖼️",
            layout="wide"
        )
        cls.page_header_render()
        cls.page_body_render()


public_collection_page = st.Page(CollectionView.render, url_path='collection', title="Collection", icon="🖼️")