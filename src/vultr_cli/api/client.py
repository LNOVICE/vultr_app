"""Vultr API client."""

import requests


class VultrAPI:
    """Vultr API client."""

    BASE_URL = "https://api.vultr.com/v2"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_plans(self, plan_type="vc2"):
        url = f"{self.BASE_URL}/plans"
        params = {"type": plan_type}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("plans", [])
        return []

    def get_regions(self):
        url = f"{self.BASE_URL}/regions"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("regions", [])
        return []

    def get_available_plans_in_region(self, region_id):
        url = f"{self.BASE_URL}/regions/{region_id}/availability"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("available_plans", [])
        return []

    def get_snapshots(self):
        url = f"{self.BASE_URL}/snapshots"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("snapshots", [])
        return []

    def create_instance(self, plan_id, region_id, snapshot_id):
        url = f"{self.BASE_URL}/instances"
        data = {
            "plan": plan_id,
            "region": region_id,
            "snapshot_id": snapshot_id,
            "enable_ipv6": True,
            "backups": "disabled"
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code in [200, 201, 202]:
            return response.json()
        else:
            error_msg = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to create instance: {error_msg}")

    def get_instances(self):
        url = f"{self.BASE_URL}/instances"
        params = {"show_pending_charges": "true"}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json().get("instances", [])
        return []

    def delete_instance(self, instance_id):
        url = f"{self.BASE_URL}/instances/{instance_id}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 204
