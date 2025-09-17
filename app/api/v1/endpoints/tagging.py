"""
Tagging API endpoints for company and site management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.auth_service import AuthService
from app.services.tagging_service import TaggingService

router = APIRouter()
auth_service = AuthService()
tagging_service = TaggingService()


# Request/Response Models
class CompanyCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SiteCreateRequest(BaseModel):
    company_id: str
    name: str
    code: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None


class SiteUpdateRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class DeviceTagRequest(BaseModel):
    company_id: Optional[str] = None
    site_id: Optional[str] = None
    custom_tags: Optional[Dict[str, str]] = None


class ScanTagRequest(BaseModel):
    company_id: Optional[str] = None
    site_id: Optional[str] = None
    custom_tags: Optional[Dict[str, str]] = None


# Company Endpoints
@router.post("/companies", response_model=Dict[str, str])
async def create_company(
    request: CompanyCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new company"""
    try:
        company_id = await tagging_service.create_company(
            name=request.name,
            code=request.code,
            description=request.description,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            address=request.address
        )
        
        return {
            "company_id": company_id,
            "message": f"Company '{request.name}' created successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create company: {str(e)}"
        )


@router.get("/companies", response_model=List[Dict[str, Any]])
async def list_companies(
    active_only: bool = True,
    token: str = Depends(auth_service.verify_token)
):
    """List all companies"""
    try:
        companies = await tagging_service.list_companies(active_only=active_only)
        return companies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list companies: {str(e)}"
        )


@router.get("/companies/{company_id}", response_model=Dict[str, Any])
async def get_company(
    company_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get company by ID"""
    try:
        company = await tagging_service.get_company(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company: {str(e)}"
        )


@router.put("/companies/{company_id}")
async def update_company(
    company_id: str,
    request: CompanyUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update company"""
    try:
        # Convert request to dict, excluding None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        success = await tagging_service.update_company(company_id, **update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {"message": f"Company '{company_id}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update company: {str(e)}"
        )


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Delete company"""
    try:
        success = await tagging_service.delete_company(company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {"message": f"Company '{company_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete company: {str(e)}"
        )


# Site Endpoints
@router.post("/sites", response_model=Dict[str, str])
async def create_site(
    request: SiteCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new site"""
    try:
        site_id = await tagging_service.create_site(
            company_id=request.company_id,
            name=request.name,
            code=request.code,
            description=request.description,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            postal_code=request.postal_code,
            timezone=request.timezone
        )
        
        return {
            "site_id": site_id,
            "message": f"Site '{request.name}' created successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create site: {str(e)}"
        )


@router.get("/sites", response_model=List[Dict[str, Any]])
async def list_sites(
    company_id: Optional[str] = None,
    active_only: bool = True,
    token: str = Depends(auth_service.verify_token)
):
    """List sites, optionally filtered by company"""
    try:
        sites = await tagging_service.list_sites(company_id=company_id, active_only=active_only)
        return sites
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sites: {str(e)}"
        )


@router.get("/sites/{site_id}", response_model=Dict[str, Any])
async def get_site(
    site_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get site by ID"""
    try:
        site = await tagging_service.get_site(site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        return site
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get site: {str(e)}"
        )


@router.put("/sites/{site_id}")
async def update_site(
    site_id: str,
    request: SiteUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update site"""
    try:
        # Convert request to dict, excluding None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        success = await tagging_service.update_site(site_id, **update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        
        return {"message": f"Site '{site_id}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update site: {str(e)}"
        )


@router.delete("/sites/{site_id}")
async def delete_site(
    site_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Delete site"""
    try:
        success = await tagging_service.delete_site(site_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        
        return {"message": f"Site '{site_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete site: {str(e)}"
        )


# Device Tagging Endpoints
@router.post("/devices/{device_id}/tags")
async def tag_device(
    device_id: str,
    request: DeviceTagRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Tag a device with company, site, and custom tags"""
    try:
        success = await tagging_service.tag_device(
            device_id=device_id,
            company_id=request.company_id,
            site_id=request.site_id,
            custom_tags=request.custom_tags,
            user_id=auth_service.get_current_user_id(token)  # You'll need to implement this
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        return {"message": f"Device '{device_id}' tagged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tag device: {str(e)}"
        )


@router.get("/devices/{device_id}/tags", response_model=Dict[str, Any])
async def get_device_tags(
    device_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get all tags for a device"""
    try:
        tags = await tagging_service.get_device_tags(device_id)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device tags: {str(e)}"
        )


# Scan Tagging Endpoints
@router.post("/scans/{scan_id}/tags")
async def tag_scan(
    scan_id: str,
    request: ScanTagRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Tag a scan with company, site, and custom tags"""
    try:
        success = await tagging_service.tag_scan(
            scan_id=scan_id,
            company_id=request.company_id,
            site_id=request.site_id,
            custom_tags=request.custom_tags,
            user_id=auth_service.get_current_user_id(token)  # You'll need to implement this
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        return {"message": f"Scan '{scan_id}' tagged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tag scan: {str(e)}"
        )


@router.get("/scans/{scan_id}/tags", response_model=Dict[str, Any])
async def get_scan_tags(
    scan_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get all tags for a scan"""
    try:
        tags = await tagging_service.get_scan_tags(scan_id)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scan tags: {str(e)}"
        )
