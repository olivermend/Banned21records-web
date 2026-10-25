"""Bandcamp official API client: token management only until account access is granted.

No publishing/upload methods are claimed or implemented. Standard library only.
Never log or commit secrets. Set BANDCAMP_CLIENT_ID and BANDCAMP_CLIENT_SECRET.
"""
import json
import os
import urllib.parse
import urllib.request


class BandcampAPIError(RuntimeError):
    pass


class BandcampClient:
    TOKEN_URL = "https://bandcamp.com/oauth_token"

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.environ.get("BANDCAMP_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("BANDCAMP_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise BandcampAPIError("Bandcamp API credentials not configured. Bandcamp must approve API access first.")

    def _token_request(self, fields):
        payload = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **fields,
        }).encode("utf-8")
        req = urllib.request.Request(self.TOKEN_URL, data=payload, method="POST",
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.load(response)
        except Exception as exc:
            raise BandcampAPIError("Bandcamp token request failed; inspect API access and token status.") from exc
        if not result.get("ok") or not result.get("access_token"):
            raise BandcampAPIError("Bandcamp did not issue an access token.")
        return result

    def initial_token(self):
        """Call once; repeat calls may trigger duplicate_grant."""
        return self._token_request({"grant_type": "client_credentials"})

    def refresh_token(self, refresh_token):
        return self._token_request({"grant_type": "refresh_token", "refresh_token": refresh_token})
