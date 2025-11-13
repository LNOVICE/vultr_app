"""Main Kivy application for Vultr CLI Android App."""

import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from ..api.client import VultrAPI


class LoadingPopup(Popup):
    """Loading popup with progress bar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Loading"
        self.size_hint = (0.8, 0.3)

        layout = BoxLayout(orientation='vertical', padding=dp(20))
        layout.add_widget(Label(text="Please wait..."))
        self.progress = ProgressBar()
        layout.add_widget(self.progress)

        self.content = layout


class DeployPage(BoxLayout):
    """Page for deploying new instances."""

    def __init__(self, api_client, switch_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.switch_callback = switch_callback  # Callback to switch to instance list
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        self.snapshot_id = None
        self.selected_plan_id = None
        self.selected_region_id = None
        self.regions_map = {}
        self.all_plans = []
        self.selected_plan_btn = None  # Track the currently selected plan button

        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        # City selection
        city_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        city_layout.add_widget(Label(text="Select City:", size_hint_x=0.3))
        self.city_spinner = Spinner(text='Loading...', values=['Loading...'])
        city_layout.add_widget(self.city_spinner)
        self.add_widget(city_layout)

        # Plans label
        self.add_widget(Label(text="Available Plans:", size_hint_y=None, height=dp(30)))

        # Plans scroll view
        self.plans_scroll = ScrollView()
        self.plans_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.plans_layout.bind(minimum_height=self.plans_layout.setter('height'))
        self.plans_scroll.add_widget(self.plans_layout)
        self.add_widget(self.plans_scroll)

        # Create instance button
        self.create_btn = Button(text="Create Instance", size_hint_y=None, height=dp(50))
        self.create_btn.disabled = True
        self.create_btn.bind(on_press=self.create_instance)
        self.add_widget(self.create_btn)

        # Load initial data
        Clock.schedule_once(lambda dt: self.load_initial_data(), 0)

    def load_initial_data(self):
        """Load initial data from API."""
        loading = LoadingPopup()
        loading.open()

        try:
            # Load regions
            regions = self.api_client.get_regions()
            city_values = []
            for region in regions:
                city = region.get("city", "Unknown")
                region_id = region.get("id")
                self.regions_map[city] = region_id
                city_values.append(city)

            self.city_spinner.values = city_values

            # Set default to Osaka if available
            if "Osaka" in city_values:
                self.city_spinner.text = "Osaka"
            elif city_values:
                self.city_spinner.text = city_values[0]

            # Load plans
            self.all_plans = self.api_client.get_plans("vc2")

            # Load snapshot
            snapshots = self.api_client.get_snapshots()
            if snapshots:
                self.snapshot_id = snapshots[0].get("id")

            self.city_spinner.bind(text=self.on_city_changed)
            self.on_city_changed(self.city_spinner, self.city_spinner.text)

        except Exception as e:
            self.show_error(f"Failed to load data: {str(e)}")
        finally:
            loading.dismiss()

    def on_city_changed(self, spinner, city):
        """Handle city selection change."""
        if city in self.regions_map:
            self.selected_region_id = self.regions_map[city]
            # Reset plan selection when city changes
            self.selected_plan_id = None
            self.selected_plan_btn = None
            self.create_btn.disabled = True
            self.load_available_plans()

    def load_available_plans(self):
        """Load available plans for selected region."""
        if not self.selected_region_id:
            return

        loading = LoadingPopup()
        loading.open()

        try:
            available_plans = self.api_client.get_available_plans_in_region(self.selected_region_id)

            # Clear existing plans
            self.plans_layout.clear_widgets()

            # Filter plans based on availability
            filtered_plans = [plan for plan in self.all_plans if plan["id"] in available_plans]

            for plan in filtered_plans:
                plan_btn = Button(
                    text=f"{plan['id']} - {plan.get('vcpu_count', 'N/A')} vCPU - ${plan.get('monthly_cost', 'N/A')}/month",
                    size_hint_y=None,
                    height=dp(50)
                )
                plan_btn.bind(on_press=lambda btn, p=plan: self.select_plan(p, btn))
                self.plans_layout.add_widget(plan_btn)

        except Exception as e:
            self.show_error(f"Failed to load available plans: {str(e)}")
        finally:
            loading.dismiss()

    def select_plan(self, plan, btn):
        """Select a plan and highlight the button."""
        # Reset previous selection
        if self.selected_plan_btn:
            self.selected_plan_btn.background_color = (1.0, 1.0, 1.0, 1.0)

        # Highlight the selected button (light blue)
        btn.background_color = (0.6, 0.8, 1.0, 1.0)
        self.selected_plan_btn = btn

        # Store selected plan ID
        self.selected_plan_id = plan["id"]
        self.create_btn.disabled = False

    def create_instance(self, instance):
        """Create instance button handler."""
        if not all([self.selected_plan_id, self.selected_region_id, self.snapshot_id]):
            self.show_error("Please select a plan and ensure all data is loaded")
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=f"Create instance with:\nPlan: {self.selected_plan_id}\nRegion: {self.selected_region_id}"))

        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")

        popup = Popup(title="Confirm", content=content, size_hint=(0.8, 0.4))

        def on_yes(btn):
            popup.dismiss()
            self.do_create_instance()

        def on_no(btn):
            popup.dismiss()

        yes_btn.bind(on_press=on_yes)
        no_btn.bind(on_press=on_no)

        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup.open()

    def do_create_instance(self):
        """Actually create the instance."""
        loading = LoadingPopup()
        loading.open()

        try:
            result = self.api_client.create_instance(
                self.selected_plan_id,
                self.selected_region_id,
                self.snapshot_id
            )
            self.show_success("Instance created successfully!")
            # Switch to instance list using callback if available
            if self.switch_callback:
                self.switch_callback()
        except Exception as e:
            self.show_error(f"Failed to create instance: {str(e)}")
        finally:
            loading.dismiss()

    def show_error(self, message):
        """Show error popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Error", content=scroll, size_hint=(0.9, 0.6))
        popup.open()

    def show_success(self, message):
        """Show success popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Success", content=scroll, size_hint=(0.9, 0.6))
        popup.open()
        # Auto-close after 2 seconds
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)


class InstanceListPage(BoxLayout):
    """Page for listing and managing instances."""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        # Refresh button
        refresh_btn = Button(text="Refresh", size_hint_y=None, height=dp(50))
        refresh_btn.bind(on_press=lambda x: self.load_instances())
        self.add_widget(refresh_btn)

        # Instances scroll view
        self.instances_scroll = ScrollView()
        self.instances_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.instances_layout.bind(minimum_height=self.instances_layout.setter('height'))
        self.instances_scroll.add_widget(self.instances_layout)
        self.add_widget(self.instances_scroll)

        # Load initial data
        Clock.schedule_once(lambda dt: self.load_instances(), 0)

    def load_instances(self):
        """Load instances from API."""
        loading = LoadingPopup()
        loading.open()

        try:
            instances = self.api_client.get_instances()
            self.instances_layout.clear_widgets()

            for instance in instances:
                instance_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140))

                # Instance info
                info_text = f"ID: {instance.get('id', 'N/A')}\n"
                info_text += f"Plan: {instance.get('plan', 'N/A')}\n"
                info_text += f"IP: {instance.get('main_ip', 'N/A')}\n"
                info_text += f"Status: {instance.get('status', 'N/A')}"

                # Add pending charges if available
                pending_charges = instance.get('pending_charges')
                if pending_charges:
                    info_text += f"\nPending: ${pending_charges}"

                info_label = Label(text=info_text, size_hint_y=0.7, text_size=(None, None))
                instance_layout.add_widget(info_label)

                # Delete button
                delete_btn = Button(text="Destroy", size_hint_y=None, height=dp(30))
                instance_id = instance.get("id")
                status = instance.get("status")
                delete_btn.disabled = status != "active"
                delete_btn.bind(on_press=lambda btn, id=instance_id: self.delete_instance(id))
                instance_layout.add_widget(delete_btn)

                self.instances_layout.add_widget(instance_layout)

        except Exception as e:
            self.show_error(f"Failed to load instances: {str(e)}")
        finally:
            loading.dismiss()

    def delete_instance(self, instance_id):
        """Delete instance button handler."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=f"Destroy instance {instance_id}?"))

        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")

        popup = Popup(title="Confirm", content=content, size_hint=(0.8, 0.4))

        def on_yes(btn):
            popup.dismiss()
            self.do_delete_instance(instance_id)

        def on_no(btn):
            popup.dismiss()

        yes_btn.bind(on_press=on_yes)
        no_btn.bind(on_press=on_no)

        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup.open()

    def do_delete_instance(self, instance_id):
        """Actually delete the instance."""
        loading = LoadingPopup()
        loading.open()

        try:
            success = self.api_client.delete_instance(instance_id)
            if success:
                self.show_success("Instance destroyed successfully!")
                self.load_instances()
            else:
                self.show_error("Failed to destroy instance")
        except Exception as e:
            self.show_error(f"Failed to destroy instance: {str(e)}")
        finally:
            loading.dismiss()

    def show_error(self, message):
        """Show error popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Error", content=scroll, size_hint=(0.9, 0.6))
        popup.open()

    def show_success(self, message):
        """Show success popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Success", content=scroll, size_hint=(0.9, 0.6))
        popup.open()
        # Auto-close after 2 seconds
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)


class MainScreen(BoxLayout):
    """Main application screen."""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.orientation = 'vertical'

        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        # Navigation buttons
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.deploy_btn = Button(text="Deploy Instance")
        self.instance_list_btn = Button(text="Instance List")
        self.deploy_btn.bind(on_press=lambda x: self.switch_to_deploy())
        self.instance_list_btn.bind(on_press=lambda x: self.switch_to_instance_list())
        nav_layout.add_widget(self.deploy_btn)
        nav_layout.add_widget(self.instance_list_btn)
        self.add_widget(nav_layout)

        # Content area - pass callback to switch to instance list
        self.deploy_page = DeployPage(self.api_client, switch_callback=self.switch_to_instance_list)
        self.instance_list_page = InstanceListPage(self.api_client)
        self.add_widget(self.deploy_page)

        # Show deploy page by default
        self.current_page = self.deploy_page

    def switch_to_deploy(self):
        """Switch to deploy page."""
        if self.current_page != self.deploy_page:
            self.remove_widget(self.current_page)
            self.add_widget(self.deploy_page)
            self.current_page = self.deploy_page

    def switch_to_instance_list(self):
        """Switch to instance list page."""
        if self.current_page != self.instance_list_page:
            self.remove_widget(self.current_page)
            self.add_widget(self.instance_list_page)
            self.current_page = self.instance_list_page
            self.instance_list_page.load_instances()


class VultrCliApp(App):
    """Main Kivy application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = None
        self.api_client = None

    def build(self):
        """Build the application."""
        self.title = "Vultr CLI"

        # Try to load API key from config file
        config_file = "vultr_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('api_key')
                    if api_key:
                        # Test the API key
                        test_client = VultrAPI(api_key)
                        regions = test_client.get_regions()
                        if regions:
                            self.api_key = api_key
                            self.api_client = test_client
                            return MainScreen(self.api_client)
            except Exception:
                pass

        # If config file doesn't exist or API key is invalid, show API key screen
        return self.get_api_key_screen()

    def get_api_key_screen(self):
        """Create API key input screen."""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        layout.add_widget(Label(text="Enter your Vultr API Key:"))

        self.api_input = TextInput(multiline=False, password=True)
        layout.add_widget(self.api_input)

        submit_btn = Button(text="Submit", size_hint_y=None, height=dp(50))
        submit_btn.bind(on_press=self.submit_api_key)
        layout.add_widget(submit_btn)

        return layout

    def submit_api_key(self, instance):
        """Handle API key submission."""
        api_key = self.api_input.text.strip()
        if not api_key:
            self.show_error("API Key is required")
            return

        # Test the API key
        loading = LoadingPopup()
        loading.open()

        try:
            test_client = VultrAPI(api_key)
            regions = test_client.get_regions()
            if regions:
                self.api_key = api_key
                self.api_client = test_client

                # Save API key to config file
                config_file = "vultr_config.json"
                config = {"api_key": api_key}
                with open(config_file, 'w') as f:
                    json.dump(config, f)

                loading.dismiss()
                self.show_success("API Key saved successfully!")
                self.show_main_screen()
            else:
                loading.dismiss()
                self.show_error("Invalid API Key")
        except Exception as e:
            loading.dismiss()
            self.show_error(f"Failed to connect: {str(e)}")

    def show_main_screen(self):
        """Switch to main screen."""
        self.root_window.remove_widget(self.root)
        self.root = MainScreen(self.api_client)
        self.root_window.add_widget(self.root)

    def show_error(self, message):
        """Show error popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Error", content=scroll, size_hint=(0.9, 0.6))
        popup.open()

    def show_success(self, message):
        """Show success popup."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(text=message, text_size=(None, None), size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title="Success", content=scroll, size_hint=(0.9, 0.6))
        popup.open()
        # Auto-close after 2 seconds
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
