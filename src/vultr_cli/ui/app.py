"""Main Kivy application for Vultr CLI."""

import os
import sys
from typing import Optional

# Add the src directory to the Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp

from ..api.client import VultrAPI


class DeployPage(BoxLayout):
    """Page for deploying new instances."""

    def __init__(self, api_client: VultrAPI, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        # Initialize UI components
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = Label(
            text='Deploy New Instance',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(20)
        )
        self.add_widget(title_label)

        # Form container
        form_layout = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200)
        )

        # Region selection
        form_layout.add_widget(Label(text='Region:', size_hint_x=None, width=dp(100)))
        self.region_spinner = Spinner(
            text='Select Region',
            values=[],
            size_hint_x=None,
            width=dp(200)
        )
        form_layout.add_widget(self.region_spinner)

        # Plan selection
        form_layout.add_widget(Label(text='Plan:', size_hint_x=None, width=dp(100)))
        self.plan_spinner = Spinner(
            text='Select Plan',
            values=[],
            size_hint_x=None,
            width=dp(200)
        )
        form_layout.add_widget(self.plan_spinner)

        # OS selection
        form_layout.add_widget(Label(text='OS:', size_hint_x=None, width=dp(100)))
        self.os_spinner = Spinner(
            text='Select OS',
            values=[],
            size_hint_x=None,
            width=dp(200)
        )
        form_layout.add_widget(self.os_spinner)

        # Instance label
        form_layout.add_widget(Label(text='Label:', size_hint_x=None, width=dp(100)))
        self.label_input = TextInput(
            multiline=False,
            size_hint_x=None,
            width=dp(200)
        )
        form_layout.add_widget(self.label_input)

        self.add_widget(form_layout)

        # Deploy button
        deploy_button = Button(
            text='Deploy Instance',
            size_hint_y=None,
            height=dp(50)
        )
        deploy_button.bind(on_press=self.deploy_instance)
        self.add_widget(deploy_button)

        # Status label
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.status_label)

    def _load_data(self):
        """Load data from API."""
        try:
            # Load regions
            regions = self.api_client.get_regions()
            region_values = [f"{r['id']} - {r['city']}, {r['country']}" for r in regions]
            self.region_spinner.values = region_values

            # Load plans
            plans = self.api_client.get_plans()
            plan_values = [f"{p['id']} - ${p['monthly_cost']}/mo - {p['vcpu_count']}vCPU/{p['ram']}/{p['disk']}" for p in plans]
            self.plan_spinner.values = plan_values

            # Load OS images
            os_images = self.api_client.get_os_images()
            os_values = [f"{os['id']} - {os['name']}" for os in os_images]
            self.os_spinner.values = os_values

        except Exception as e:
            self.status_label.text = f'Error loading data: {str(e)}'

    def deploy_instance(self, instance):
        """Deploy a new instance."""
        try:
            region_id = self.region_spinner.text.split(' - ')[0] if ' - ' in self.region_spinner.text else None
            plan_id = self.plan_spinner.text.split(' - ')[0] if ' - ' in self.plan_spinner.text else None
            os_id = self.os_spinner.text.split(' - ')[0] if ' - ' in self.os_spinner.text else None
            label = self.label_input.text.strip()

            if not all([region_id, plan_id, os_id, label]):
                self.status_label.text = 'Please fill in all fields'
                return

            instance_config = {
                'region': region_id,
                'plan': plan_id,
                'os_id': os_id,
                'label': label
            }

            result = self.api_client.create_instance(instance_config)
            if result:
                self.status_label.text = f'Instance deployed successfully: {result["id"]}'
                self.label_input.text = ''
            else:
                self.status_label.text = 'Failed to deploy instance'

        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'


class InstanceListPage(BoxLayout):
    """Page for listing and managing instances."""

    def __init__(self, api_client: VultrAPI, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        # Initialize UI components
        self._setup_ui()
        self.refresh_instances()

    def _setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = Label(
            text='Instance Management',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(20)
        )
        self.add_widget(title_label)

        # Refresh button
        refresh_button = Button(
            text='Refresh',
            size_hint_y=None,
            height=dp(40)
        )
        refresh_button.bind(on_press=self.refresh_instances)
        self.add_widget(refresh_button)

        # Scrollable instance list
        scroll_view = ScrollView(size_hint=(1, 1))
        self.instance_list_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        self.instance_list_layout.bind(minimum_height=self.instance_list_layout.setter('height'))
        scroll_view.add_widget(self.instance_list_layout)
        self.add_widget(scroll_view)

        # Status label
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.status_label)

    def refresh_instances(self, instance=None):
        """Refresh the instances list."""
        try:
            instances = self.api_client.get_instances()
            self.instance_list_layout.clear_widgets()

            if not instances:
                self.status_label.text = 'No instances found'
                return

            for instance_data in instances:
                instance_item = self._create_instance_item(instance_data)
                self.instance_list_layout.add_widget(instance_item)

            self.status_label.text = f'Found {len(instances)} instances'

        except Exception as e:
            self.status_label.text = f'Error loading instances: {str(e)}'

    def _create_instance_item(self, instance_data):
        """Create a widget for a single instance."""
        item_layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(150)
        )

        # Instance info
        info_label = Label(
            text=f"{instance_data.get('label', 'Unnamed')} ({instance_data['id']})\n"
                 f"Status: {instance_data.get('status', 'Unknown')}\n"
                 f"IP: {instance_data.get('main_ip', 'N/A')}\n"
                 f"Plan: {instance_data.get('plan', 'Unknown')}",
            size_hint_y=None,
            height=dp(80),
            text_size=(None, dp(80))
        )
        item_layout.add_widget(info_label)

        # Action buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )

        start_btn = Button(text='Start')
        stop_btn = Button(text='Stop')
        reboot_btn = Button(text='Reboot')
        delete_btn = Button(text='Delete')

        start_btn.bind(on_press=lambda x, i=instance_data['id']: self.start_instance(i))
        stop_btn.bind(on_press=lambda x, i=instance_data['id']: self.stop_instance(i))
        reboot_btn.bind(on_press=lambda x, i=instance_data['id']: self.reboot_instance(i))
        delete_btn.bind(on_press=lambda x, i=instance_data['id']: self.delete_instance(i))

        button_layout.add_widget(start_btn)
        button_layout.add_widget(stop_btn)
        button_layout.add_widget(reboot_btn)
        button_layout.add_widget(delete_btn)

        item_layout.add_widget(button_layout)

        return item_layout

    def start_instance(self, instance_id):
        """Start an instance."""
        try:
            if self.api_client.start_instance(instance_id):
                self.status_label.text = f'Instance {instance_id} started'
            else:
                self.status_label.text = f'Failed to start instance {instance_id}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'

    def stop_instance(self, instance_id):
        """Stop an instance."""
        try:
            if self.api_client.stop_instance(instance_id):
                self.status_label.text = f'Instance {instance_id} stopped'
            else:
                self.status_label.text = f'Failed to stop instance {instance_id}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'

    def reboot_instance(self, instance_id):
        """Reboot an instance."""
        try:
            if self.api_client.reboot_instance(instance_id):
                self.status_label.text = f'Instance {instance_id} rebooted'
            else:
                self.status_label.text = f'Failed to reboot instance {instance_id}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'

    def delete_instance(self, instance_id):
        """Delete an instance."""
        try:
            if self.api_client.delete_instance(instance_id):
                self.status_label.text = f'Instance {instance_id} deleted'
                self.refresh_instances()
            else:
                self.status_label.text = f'Failed to delete instance {instance_id}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'


class MainScreen(BoxLayout):
    """Main application screen."""

    def __init__(self, api_client: VultrAPI, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.orientation = 'vertical'

        # Navigation
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=dp(10),
            spacing=dp(10)
        )

        deploy_btn = Button(text='Deploy')
        instances_btn = Button(text='Instances')

        deploy_btn.bind(on_press=self.show_deploy_page)
        instances_btn.bind(on_press=self.show_instances_page)

        nav_layout.add_widget(deploy_btn)
        nav_layout.add_widget(instances_btn)
        self.add_widget(nav_layout)

        # Content area
        self.content_area = BoxLayout()
        self.add_widget(self.content_area)

        # Show deploy page by default
        self.show_deploy_page()

    def show_deploy_page(self, instance=None):
        """Show the deploy page."""
        self.content_area.clear_widgets()
        deploy_page = DeployPage(self.api_client)
        self.content_area.add_widget(deploy_page)

    def show_instances_page(self, instance=None):
        """Show the instances page."""
        self.content_area.clear_widgets()
        instances_page = InstanceListPage(self.api_client)
        self.content_area.add_widget(instances_page)


class VultrCliApp(App):
    """Main Kivy application class."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get('VULTR_API_KEY', '')

    def build(self):
        """Build the application."""
        self.title = 'Vultr CLI'

        if not self.api_key:
            # Show API key input dialog
            return self._create_api_key_input()

        try:
            api_client = VultrAPI(self.api_key)
            return MainScreen(api_client)
        except Exception as e:
            error_label = Label(text=f'Error: {str(e)}')
            return error_label

    def _create_api_key_input(self):
        """Create API key input dialog."""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        title_label = Label(
            text='Enter Vultr API Key:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(18)
        )
        layout.add_widget(title_label)

        self.api_key_input = TextInput(
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.api_key_input)

        submit_btn = Button(
            text='Submit',
            size_hint_y=None,
            height=dp(50)
        )
        submit_btn.bind(on_press=self._on_api_key_submit)
        layout.add_widget(submit_btn)

        self.error_label = Label(text='', color=(1, 0, 0, 1))
        layout.add_widget(self.error_label)

        return layout

    def _on_api_key_submit(self, instance):
        """Handle API key submission."""
        api_key = self.api_key_input.text.strip()
        if not api_key:
            self.error_label.text = 'Please enter an API key'
            return

        try:
            # Test the API key
            api_client = VultrAPI(api_key)
            regions = api_client.get_regions()

            if regions:
                self.api_key = api_key
                self.root.clear_widgets()
                main_screen = MainScreen(api_client)
                self.root.add_widget(main_screen)
            else:
                self.error_label.text = 'Invalid API key or no access'

        except Exception as e:
            self.error_label.text = f'Error: {str(e)}'


def main():
    """Main entry point for the application."""
    VultrCliApp().run()


if __name__ == '__main__':
    main()