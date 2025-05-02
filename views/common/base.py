from abc import ABC, abstractmethod


class InterfaceCrudView(ABC):
    @abstractmethod
    def render_header_section(self):
        """Render the page header section"""
        raise NotImplementedError

    @abstractmethod
    def render_notification(self):
        """Render notification messages to the user"""
        raise NotImplementedError

    @abstractmethod
    def render_search_section(self):
        """Render search filters and controls

        Returns:
            tuple: A tuple containing search parameters (e.g., start_date, end_date)
        """
        raise NotImplementedError

    @abstractmethod
    def render_dataframe_section(self, **kwargs):
        """Render entities in tabular format

        Args:
            **kwargs: Search parameters to filter the entities
        """
        raise NotImplementedError

    @abstractmethod
    def render_action_section(self):
        """Render action buttons for CRUD operations

        Returns:
            tuple: A tuple of button states (clicked or not)
        """
        raise NotImplementedError

    @abstractmethod
    def render_create_dialog(self):
        """Render UI for creating a new resource"""
        raise NotImplementedError

    @abstractmethod
    def render_update_dialog(self):
        """Render UI for updating an existing resource"""
        raise NotImplementedError

    @abstractmethod
    def render_delete_dialog(self):
        """Render UI for confirming resource deletion"""
        raise NotImplementedError

    @abstractmethod
    def render(self):
        """Main render method that orchestrates the complete view"""
        raise NotImplementedError