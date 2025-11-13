"""Vultr API client implementation."""

import requests
from typing import Dict, List, Optional, Any


class VultrAPI:
    """Vultr API client for interacting with Vultr cloud services."""

    BASE_URL = "https://api.vultr.com/v2"

    def __init__(self, api_key: str):
        """Initialize the Vultr API client.

        Args:
            api_key: Vultr API key for authentication
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_plans(self, plan_type: str = "vc2") -> List[Dict[str, Any]]:
        """Get available plans.

        Args:
            plan_type: Type of plans to retrieve

        Returns:
            List of available plans
        """
        url = f"{self.BASE_URL}/plans"
        params = {"type": plan_type}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("plans", [])
        return []

    def get_regions(self) -> List[Dict[str, Any]]:
        """Get available regions.

        Returns:
            List of available regions
        """
        url = f"{self.BASE_URL}/regions"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("regions", [])
        return []

    def get_available_plans_in_region(self, region_id: str) -> List[str]:
        """Get available plans in a specific region.

        Args:
            region_id: ID of the region

        Returns:
            List of available plan IDs
        """
        url = f"{self.BASE_URL}/regions/{region_id}/availability"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("available_plans", [])
        return []

    def get_os_images(self) -> List[Dict[str, Any]]:
        """Get available OS images.

        Returns:
            List of available OS images
        """
        url = f"{self.BASE_URL}/os"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("os", [])
        return []

    def create_instance(self, instance_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new instance.

        Args:
            instance_config: Configuration for the new instance

        Returns:
            Created instance data or None if failed
        """
        url = f"{self.BASE_URL}/instances"
        response = requests.post(url, headers=self.headers, json=instance_config)
        if response.status_code == 201:
            return response.json().get("instance")
        return None

    def get_instances(self) -> List[Dict[str, Any]]:
        """Get all instances.

        Returns:
            List of instances
        """
        url = f"{self.BASE_URL}/instances"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("instances", [])
        return []

    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific instance.

        Args:
            instance_id: ID of the instance

        Returns:
            Instance data or None if not found
        """
        url = f"{self.BASE_URL}/instances/{instance_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("instance")
        return None

    def delete_instance(self, instance_id: str) -> bool:
        """Delete an instance.

        Args:
            instance_id: ID of the instance to delete

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/instances/{instance_id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204

    def start_instance(self, instance_id: str) -> bool:
        """Start an instance.

        Args:
            instance_id: ID of the instance to start

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/instances/{instance_id}/start"
        response = requests.post(url, headers=self.headers)
        return response.status_code == 204

    def stop_instance(self, instance_id: str) -> bool:
        """Stop an instance.

        Args:
            instance_id: ID of the instance to stop

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/instances/{instance_id}/stop"
        response = requests.post(url, headers=self.headers)
        return response.status_code == 204

    def reboot_instance(self, instance_id: str) -> bool:
        """Reboot an instance.

        Args:
            instance_id: ID of the instance to reboot

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/instances/{instance_id}/reboot"
        response = requests.post(url, headers=self.headers)
        return response.status_code == 204