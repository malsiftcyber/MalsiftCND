"""
Integration service for external security tools
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.config import settings


class IntegrationService:
    """Service for managing external integrations"""

    MASK_VALUE = "********"

    def __init__(self):
        self.logger = logging.getLogger("services.integration_service")
        self._definitions = {
            "runzero": {
                "display_name": "RunZero",
                "integration_type": "asset_discovery",
                "description": "RunZero external asset discovery and inventory",
                "fields": [
                    {
                        "key": "api_key",
                        "label": "API Key",
                        "type": "password",
                        "required": True,
                        "help_text": "Generate a service API key from the RunZero console.",
                    },
                    {
                        "key": "base_url",
                        "label": "Base URL",
                        "type": "text",
                        "required": False,
                        "placeholder": "https://api.runzero.com/v1.0",
                        "default": settings.RUNZERO_BASE_URL or "https://api.runzero.com/v1.0",
                    },
                ],
            },
            "tanium": {
                "display_name": "Tanium",
                "integration_type": "endpoint_management",
                "description": "Tanium device inventory and patch status",
                "fields": [
                    {
                        "key": "api_key",
                        "label": "API Key",
                        "type": "password",
                        "required": True,
                        "help_text": "Create a REST API token inside the Tanium console.",
                    },
                    {
                        "key": "base_url",
                        "label": "Base URL",
                        "type": "text",
                        "required": True,
                        "placeholder": "https://tanium.example.com",
                    },
                ],
            },
            "armis": {
                "display_name": "Armis",
                "integration_type": "asset_security",
                "description": "Armis agentless device visibility",
                "fields": [
                    {
                        "key": "api_key",
                        "label": "API Key",
                        "type": "password",
                        "required": True,
                    },
                    {
                        "key": "base_url",
                        "label": "Base URL",
                        "type": "text",
                        "required": True,
                        "placeholder": "https://armis.example.com/api",
                    },
                ],
            },
            "active_directory": {
                "display_name": "Active Directory",
                "integration_type": "directory_service",
                "description": "On-premises Active Directory for device and user discovery",
                "fields": [
                    {
                        "key": "server",
                        "label": "LDAP Server",
                        "type": "text",
                        "required": True,
                        "placeholder": "ldaps://ad.example.com",
                    },
                    {
                        "key": "domain",
                        "label": "Domain",
                        "type": "text",
                        "required": True,
                        "placeholder": "EXAMPLE.COM",
                    },
                    {
                        "key": "username",
                        "label": "Bind Username",
                        "type": "text",
                        "required": True,
                        "placeholder": "malsift_service",
                    },
                    {
                        "key": "password",
                        "label": "Bind Password",
                        "type": "password",
                        "required": True,
                    },
                ],
            },
            "azure_ad": {
                "display_name": "Azure Active Directory",
                "integration_type": "cloud_directory",
                "description": "Azure AD / Entra ID integration through Microsoft Graph",
                "fields": [
                    {
                        "key": "tenant_id",
                        "label": "Tenant ID",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "key": "client_id",
                        "label": "Client ID",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "key": "client_secret",
                        "label": "Client Secret",
                        "type": "password",
                        "required": True,
                    },
                ],
            },
        }

        self.integrations: Dict[str, Dict[str, Any]] = {}
        for key, definition in self._definitions.items():
            config = self._build_initial_config(key, definition)
            configured = self._is_configured(config, definition["fields"])
            self.integrations[key] = {
                "key": key,
                "name": definition["display_name"],
                "description": definition.get("description"),
                "integration_type": definition.get("integration_type"),
                "enabled": configured,
                "configured": configured,
                "connected": False,
                "last_sync": None,
                "error": None,
                "config": config,
            }

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _initial_env_values(self, integration_key: str) -> Dict[str, Any]:
        if integration_key == "runzero":
            return {
                "api_key": settings.RUNZERO_API_KEY or "",
                "base_url": settings.RUNZERO_BASE_URL or "https://api.runzero.com/v1.0",
            }
        if integration_key == "tanium":
            return {
                "api_key": settings.TANIUM_API_KEY or "",
                "base_url": settings.TANIUM_BASE_URL or "",
            }
        if integration_key == "armis":
            return {
                "api_key": settings.ARMIS_API_KEY or "",
                "base_url": settings.ARMIS_BASE_URL or "",
            }
        if integration_key == "active_directory":
            return {
                "server": settings.AD_SERVER or "",
                "domain": settings.AD_DOMAIN or "",
                "username": settings.AD_USERNAME or "",
                "password": settings.AD_PASSWORD or "",
            }
        if integration_key == "azure_ad":
            return {
                "tenant_id": settings.AZURE_TENANT_ID or "",
                "client_id": settings.AZURE_CLIENT_ID or "",
                "client_secret": settings.AZURE_CLIENT_SECRET or "",
            }
        return {}

    def _build_initial_config(self, integration_key: str, definition: Dict[str, Any]) -> Dict[str, Any]:
        initial_values = self._initial_env_values(integration_key)
        config: Dict[str, Any] = {}
        for field in definition["fields"]:
            field_key = field["key"]
            default_value = field.get("default", "")
            config[field_key] = initial_values.get(field_key, default_value) or ""
        return config

    @staticmethod
    def _is_configured(config: Dict[str, Any], fields: List[Dict[str, Any]]) -> bool:
        if not config:
            return False
        for field in fields:
            if field.get("required") and not config.get(field["key"]):
                return False
        return any(value for value in config.values())

    def _mask_config(self, key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        definition = self._definitions[key]
        masked: Dict[str, Any] = {}
        secret_fields = {field["key"] for field in definition["fields"] if field.get("type") == "password"}
        for field_key, value in config.items():
            if field_key in secret_fields and value:
                masked[field_key] = self.MASK_VALUE
            else:
                masked[field_key] = value
        return masked

    def _apply_config_to_settings(self, key: str, config: Dict[str, Any]) -> None:
        if key == "runzero":
            settings.RUNZERO_API_KEY = config.get("api_key") or None
            if config.get("base_url"):
                settings.RUNZERO_BASE_URL = config["base_url"]
        elif key == "tanium":
            settings.TANIUM_API_KEY = config.get("api_key") or None
            settings.TANIUM_BASE_URL = config.get("base_url") or None
        elif key == "armis":
            settings.ARMIS_API_KEY = config.get("api_key") or None
            settings.ARMIS_BASE_URL = config.get("base_url") or None
        elif key == "active_directory":
            settings.AD_SERVER = config.get("server") or None
            settings.AD_DOMAIN = config.get("domain") or None
            settings.AD_USERNAME = config.get("username") or None
            settings.AD_PASSWORD = config.get("password") or None
        elif key == "azure_ad":
            settings.AZURE_TENANT_ID = config.get("tenant_id") or None
            settings.AZURE_CLIENT_ID = config.get("client_id") or None
            settings.AZURE_CLIENT_SECRET = config.get("client_secret") or None

    # ------------------------------------------------------------------
    # Public service methods
    # ------------------------------------------------------------------
    async def list_integrations(self) -> List[Dict[str, Any]]:
        """List all integrations with sanitized metadata"""
        results: List[Dict[str, Any]] = []
        for key, state in self.integrations.items():
            definition = self._definitions[key]
            results.append(
                {
                    "key": key,
                    "name": definition["display_name"],
                    "integration_type": definition.get("integration_type"),
                    "description": definition.get("description"),
                    "enabled": state["enabled"],
                    "configured": state["configured"],
                    "connected": state["connected"],
                    "last_sync": state["last_sync"],
                    "error": state["error"],
                }
            )
        return results

    async def get_integration_status(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get integration status without exposing secrets"""
        if integration_name not in self.integrations:
            return None
        state = self.integrations[integration_name]
        definition = self._definitions[integration_name]
        return {
            "key": state["key"],
            "name": definition["display_name"],
            "integration_type": definition.get("integration_type"),
            "description": definition.get("description"),
            "enabled": state["enabled"],
            "configured": state["configured"],
            "connected": state["connected"],
            "last_sync": state["last_sync"],
            "error": state["error"],
        }

    async def get_integration_details(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Return detailed configuration metadata for an integration"""
        if integration_name not in self.integrations:
            return None
        state = self.integrations[integration_name]
        definition = self._definitions[integration_name]
        return {
            "key": state["key"],
            "name": definition["display_name"],
            "integration_type": definition.get("integration_type"),
            "description": definition.get("description"),
            "enabled": state["enabled"],
            "configured": state["configured"],
            "connected": state["connected"],
            "last_sync": state["last_sync"],
            "error": state["error"],
            "fields": definition["fields"],
            "config": self._mask_config(integration_name, state["config"]),
        }

    async def update_integration_config(self, integration_name: str, config: Dict[str, Any], enabled: bool) -> bool:
        """Update integration configuration"""
        if integration_name not in self.integrations:
            return False

        definition = self._definitions[integration_name]
        state = self.integrations[integration_name]
        current_config = state["config"].copy()
        secret_fields = {field["key"] for field in definition["fields"] if field.get("type") == "password"}

        config = config or {}

        for field in definition["fields"]:
            field_key = field["key"]
            if field_key not in config:
                continue
            value = config.get(field_key)
            if field_key in secret_fields and (value in (None, "", self.MASK_VALUE)):
                continue  # preserve existing secret
            if isinstance(value, str):
                value = value.strip()
            current_config[field_key] = value

        state["config"] = current_config
        state["enabled"] = bool(enabled)
        state["configured"] = self._is_configured(current_config, definition["fields"])
        state["connected"] = False  # require revalidation after config change
        self._apply_config_to_settings(integration_name, current_config)
        return True

    async def sync_integration(self, integration_name: str, force_full_sync: bool = False) -> str:
        """Trigger integration sync"""
        if integration_name not in self.integrations:
            raise ValueError("Integration not found")

        if not self.integrations[integration_name]["configured"]:
            raise ValueError("Integration is not configured")

        sync_id = f"{integration_name}_sync_{datetime.now().timestamp()}"
        asyncio.create_task(self._perform_sync(integration_name, sync_id, force_full_sync))
        return sync_id

    async def _perform_sync(self, integration_name: str, sync_id: str, force_full_sync: bool):
        """Perform actual sync operation (placeholder implementations)"""
        try:
            self.logger.info("Starting sync for %s", integration_name)

            if integration_name == "runzero":
                await self._sync_runzero(force_full_sync)
            elif integration_name == "tanium":
                await self._sync_tanium(force_full_sync)
            elif integration_name == "armis":
                await self._sync_armis(force_full_sync)
            elif integration_name == "active_directory":
                await self._sync_active_directory(force_full_sync)
            elif integration_name == "azure_ad":
                await self._sync_azure_ad(force_full_sync)

            state = self.integrations[integration_name]
            state["connected"] = True
            state["last_sync"] = datetime.now()
            state["error"] = None
            self.logger.info("Sync completed for %s", integration_name)

        except Exception as e:
            self.logger.error("Sync failed for %s: %s", integration_name, e)
            state = self.integrations[integration_name]
            state["connected"] = False
            state["error"] = str(e)

    # Existing placeholder sync implementations remain unchanged below
