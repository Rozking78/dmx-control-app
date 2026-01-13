"""
API Client for DMX Visualizer
"""

import requests
from typing import Optional, Dict, Any, List


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8082"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 5

    def set_base_url(self, url: str):
        """Update the base URL."""
        self.base_url = url.rstrip('/')

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}/api/v1{endpoint}"
        kwargs.setdefault('timeout', self.timeout)

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()

        if response.content:
            return response.json()
        return {}

    # Status
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return self._request('GET', '/status')

    def get_preview_url(self) -> str:
        """Get the preview image URL."""
        return f"{self.base_url}/api/v1/status/preview"

    # Outputs
    def get_outputs(self) -> List[Dict[str, Any]]:
        """Get all outputs."""
        data = self._request('GET', '/outputs')
        return data.get('outputs', [])

    def get_displays(self) -> List[Dict[str, Any]]:
        """Get available displays."""
        data = self._request('GET', '/displays')
        return data.get('displays', [])

    def add_display_output(self, display_id: str) -> Dict[str, Any]:
        """Add a display output."""
        return self._request('POST', '/outputs/display', json={'displayId': display_id})

    def add_ndi_output(self, name: str) -> Dict[str, Any]:
        """Add an NDI output."""
        return self._request('POST', '/outputs/ndi', json={'name': name})

    def enable_output(self, output_id: int) -> Dict[str, Any]:
        """Enable an output."""
        return self._request('PUT', f'/outputs/{output_id}/enable')

    def disable_output(self, output_id: int) -> Dict[str, Any]:
        """Disable an output."""
        return self._request('PUT', f'/outputs/{output_id}/disable')

    def delete_output(self, output_id: int) -> Dict[str, Any]:
        """Delete an output."""
        return self._request('DELETE', f'/outputs/{output_id}')

    def update_output_settings(self, output_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update output settings."""
        return self._request('PUT', f'/outputs/{output_id}/settings', json=settings)

    # Gobos
    def get_gobos(self) -> List[Dict[str, Any]]:
        """Get all gobos."""
        data = self._request('GET', '/gobos')
        return data.get('gobos', [])

    def get_gobo_image_url(self, gobo_id: int) -> str:
        """Get the URL for a gobo image."""
        return f"{self.base_url}/api/v1/gobos/{gobo_id}/image"

    def upload_gobo(self, slot: int, file_path: str) -> Dict[str, Any]:
        """Upload a gobo to a slot."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'slot': slot}
            return self._request('POST', '/gobos/upload', files=files, data=data)

    def delete_gobo(self, slot: int) -> Dict[str, Any]:
        """Delete a gobo from a slot."""
        return self._request('DELETE', f'/gobos/{slot}')

    # Media Slots
    def get_media_slots(self) -> List[Dict[str, Any]]:
        """Get all media slots."""
        data = self._request('GET', '/media/slots')
        return data.get('slots', [])

    def get_videos(self) -> List[Dict[str, Any]]:
        """Get available videos."""
        data = self._request('GET', '/media/videos')
        return data.get('videos', [])

    def get_images(self) -> List[Dict[str, Any]]:
        """Get available images."""
        data = self._request('GET', '/media/images')
        return data.get('images', [])

    def upload_video(self, file_path: str) -> Dict[str, Any]:
        """Upload a video."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self._request('POST', '/media/videos/upload', files=files)

    def upload_image(self, file_path: str) -> Dict[str, Any]:
        """Upload an image."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self._request('POST', '/media/images/upload', files=files)

    def assign_media_slot(self, slot: int, source: str) -> Dict[str, Any]:
        """Assign media to a slot."""
        return self._request('PUT', f'/media/slots/{slot}', json={'source': source})

    def clear_media_slot(self, slot: int) -> Dict[str, Any]:
        """Clear a media slot."""
        return self._request('DELETE', f'/media/slots/{slot}')

    # NDI Sources
    def get_ndi_sources(self) -> List[Dict[str, Any]]:
        """Get NDI sources."""
        data = self._request('GET', '/ndi/sources')
        return data.get('sources', [])

    def refresh_ndi_sources(self) -> Dict[str, Any]:
        """Refresh NDI source discovery."""
        return self._request('POST', '/ndi/refresh')
