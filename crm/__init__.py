"""CRM module for tracking leads and outreach."""

from .database import LeadDatabase
from .crm_cli import CRMCommands

__all__ = ["LeadDatabase", "CRMCommands"]
