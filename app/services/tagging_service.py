"""
Tagging service for company and site management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from app.core.database import SessionLocal
from app.models.tagging import Company, Site, DeviceTag, ScanTag
from app.models.device import Device
from app.models.scan import Scan


class TaggingService:
    """Service for managing company and site tagging"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.tagging_service")
    
    # Company Management
    async def create_company(self, name: str, code: str, description: str = None,
                           contact_email: str = None, contact_phone: str = None,
                           address: str = None) -> str:
        """Create a new company"""
        db = SessionLocal()
        try:
            # Check if company code already exists
            existing = db.query(Company).filter(Company.code == code).first()
            if existing:
                raise ValueError(f"Company code '{code}' already exists")
            
            company = Company(
                name=name,
                code=code,
                description=description,
                contact_email=contact_email,
                contact_phone=contact_phone,
                address=address
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
            self.logger.info(f"Created company: {name} ({code})")
            return str(company.id)
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to create company: {e}")
            raise
        finally:
            db.close()
    
    async def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company by ID"""
        db = SessionLocal()
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return None
            
            return {
                "id": str(company.id),
                "name": company.name,
                "code": company.code,
                "description": company.description,
                "contact_email": company.contact_email,
                "contact_phone": company.contact_phone,
                "address": company.address,
                "is_active": company.is_active,
                "created_at": company.created_at.isoformat(),
                "updated_at": company.updated_at.isoformat(),
                "sites_count": len(company.sites),
                "devices_count": len(company.devices)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get company: {e}")
            raise
        finally:
            db.close()
    
    async def list_companies(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all companies"""
        db = SessionLocal()
        try:
            query = db.query(Company)
            if active_only:
                query = query.filter(Company.is_active == True)
            
            companies = query.all()
            
            return [
                {
                    "id": str(company.id),
                    "name": company.name,
                    "code": company.code,
                    "description": company.description,
                    "contact_email": company.contact_email,
                    "contact_phone": company.contact_phone,
                    "address": company.address,
                    "is_active": company.is_active,
                    "created_at": company.created_at.isoformat(),
                    "sites_count": len(company.sites),
                    "devices_count": len(company.devices)
                }
                for company in companies
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list companies: {e}")
            raise
        finally:
            db.close()
    
    async def update_company(self, company_id: str, **kwargs) -> bool:
        """Update company"""
        db = SessionLocal()
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Updated company: {company.name}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to update company: {e}")
            raise
        finally:
            db.close()
    
    async def delete_company(self, company_id: str) -> bool:
        """Delete company (soft delete)"""
        db = SessionLocal()
        try:
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return False
            
            company.is_active = False
            company.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Deleted company: {company.name}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to delete company: {e}")
            raise
        finally:
            db.close()
    
    # Site Management
    async def create_site(self, company_id: str, name: str, code: str,
                         description: str = None, address: str = None,
                         city: str = None, state: str = None, country: str = None,
                         postal_code: str = None, timezone: str = None) -> str:
        """Create a new site"""
        db = SessionLocal()
        try:
            # Check if company exists
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise ValueError("Company not found")
            
            # Check if site code already exists for this company
            existing = db.query(Site).filter(
                Site.company_id == company_id,
                Site.code == code
            ).first()
            if existing:
                raise ValueError(f"Site code '{code}' already exists for company {company.name}")
            
            site = Site(
                company_id=company_id,
                name=name,
                code=code,
                description=description,
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                timezone=timezone
            )
            
            db.add(site)
            db.commit()
            db.refresh(site)
            
            self.logger.info(f"Created site: {name} ({code}) for company {company.name}")
            return str(site.id)
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to create site: {e}")
            raise
        finally:
            db.close()
    
    async def get_site(self, site_id: str) -> Optional[Dict[str, Any]]:
        """Get site by ID"""
        db = SessionLocal()
        try:
            site = db.query(Site).filter(Site.id == site_id).first()
            if not site:
                return None
            
            return {
                "id": str(site.id),
                "company_id": str(site.company_id),
                "company_name": site.company.name,
                "company_code": site.company.code,
                "name": site.name,
                "code": site.code,
                "description": site.description,
                "address": site.address,
                "city": site.city,
                "state": site.state,
                "country": site.country,
                "postal_code": site.postal_code,
                "timezone": site.timezone,
                "is_active": site.is_active,
                "created_at": site.created_at.isoformat(),
                "updated_at": site.updated_at.isoformat(),
                "devices_count": len(site.devices)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get site: {e}")
            raise
        finally:
            db.close()
    
    async def list_sites(self, company_id: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """List sites, optionally filtered by company"""
        db = SessionLocal()
        try:
            query = db.query(Site)
            
            if company_id:
                query = query.filter(Site.company_id == company_id)
            
            if active_only:
                query = query.filter(Site.is_active == True)
            
            sites = query.all()
            
            return [
                {
                    "id": str(site.id),
                    "company_id": str(site.company_id),
                    "company_name": site.company.name,
                    "company_code": site.company.code,
                    "name": site.name,
                    "code": site.code,
                    "description": site.description,
                    "address": site.address,
                    "city": site.city,
                    "state": site.state,
                    "country": site.country,
                    "postal_code": site.postal_code,
                    "timezone": site.timezone,
                    "is_active": site.is_active,
                    "created_at": site.created_at.isoformat(),
                    "devices_count": len(site.devices)
                }
                for site in sites
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list sites: {e}")
            raise
        finally:
            db.close()
    
    async def update_site(self, site_id: str, **kwargs) -> bool:
        """Update site"""
        db = SessionLocal()
        try:
            site = db.query(Site).filter(Site.id == site_id).first()
            if not site:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(site, key):
                    setattr(site, key, value)
            
            site.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Updated site: {site.name}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to update site: {e}")
            raise
        finally:
            db.close()
    
    async def delete_site(self, site_id: str) -> bool:
        """Delete site (soft delete)"""
        db = SessionLocal()
        try:
            site = db.query(Site).filter(Site.id == site_id).first()
            if not site:
                return False
            
            site.is_active = False
            site.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Deleted site: {site.name}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to delete site: {e}")
            raise
        finally:
            db.close()
    
    # Device Tagging
    async def tag_device(self, device_id: str, company_id: str = None, site_id: str = None,
                        custom_tags: Dict[str, str] = None, user_id: str = None) -> bool:
        """Tag a device with company, site, and custom tags"""
        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                return False
            
            # Update device company and site associations
            if company_id:
                device.company_id = company_id
            if site_id:
                device.site_id = site_id
            
            # Add custom tags
            if custom_tags:
                for tag_key, tag_value in custom_tags.items():
                    tag = DeviceTag(
                        device_id=device_id,
                        tag_type="custom",
                        tag_key=tag_key,
                        tag_value=tag_value,
                        created_by=user_id
                    )
                    db.add(tag)
            
            db.commit()
            
            self.logger.info(f"Tagged device {device.ip} with company/site/custom tags")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to tag device: {e}")
            raise
        finally:
            db.close()
    
    async def get_device_tags(self, device_id: str) -> Dict[str, Any]:
        """Get all tags for a device"""
        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                return {}
            
            # Get device tags
            device_tags = db.query(DeviceTag).filter(DeviceTag.device_id == device_id).all()
            
            tags = {
                "company": {
                    "id": str(device.company_id) if device.company_id else None,
                    "name": device.company.name if device.company else None,
                    "code": device.company.code if device.company else None
                },
                "site": {
                    "id": str(device.site_id) if device.site_id else None,
                    "name": device.site.name if device.site else None,
                    "code": device.site.code if device.site else None
                },
                "custom_tags": {}
            }
            
            for tag in device_tags:
                if tag.tag_type == "custom":
                    tags["custom_tags"][tag.tag_key] = tag.tag_value
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Failed to get device tags: {e}")
            raise
        finally:
            db.close()
    
    # Scan Tagging
    async def tag_scan(self, scan_id: str, company_id: str = None, site_id: str = None,
                      custom_tags: Dict[str, str] = None, user_id: str = None) -> bool:
        """Tag a scan with company, site, and custom tags"""
        db = SessionLocal()
        try:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return False
            
            # Update scan company and site associations
            if company_id:
                scan.company_id = company_id
            if site_id:
                scan.site_id = site_id
            
            # Add custom tags
            if custom_tags:
                for tag_key, tag_value in custom_tags.items():
                    tag = ScanTag(
                        scan_id=scan_id,
                        tag_type="custom",
                        tag_key=tag_key,
                        tag_value=tag_value,
                        created_by=user_id
                    )
                    db.add(tag)
            
            db.commit()
            
            self.logger.info(f"Tagged scan {scan_id} with company/site/custom tags")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to tag scan: {e}")
            raise
        finally:
            db.close()
    
    async def get_scan_tags(self, scan_id: str) -> Dict[str, Any]:
        """Get all tags for a scan"""
        db = SessionLocal()
        try:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return {}
            
            # Get scan tags
            scan_tags = db.query(ScanTag).filter(ScanTag.scan_id == scan_id).all()
            
            tags = {
                "company": {
                    "id": str(scan.company_id) if scan.company_id else None,
                    "name": scan.company.name if scan.company else None,
                    "code": scan.company.code if scan.company else None
                },
                "site": {
                    "id": str(scan.site_id) if scan.site_id else None,
                    "name": scan.site.name if scan.site else None,
                    "code": scan.site.code if scan.site else None
                },
                "custom_tags": {}
            }
            
            for tag in scan_tags:
                if tag.tag_type == "custom":
                    tags["custom_tags"][tag.tag_key] = tag.tag_value
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Failed to get scan tags: {e}")
            raise
        finally:
            db.close()
