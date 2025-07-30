#!/usr/bin/env python3
"""
VersionOne MCP Server using FastMCP

A simplified Model Context Protocol server for VersionOne API integration.
"""

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("VersionOne")


class StoryData(BaseModel):
    """VersionOne story data structure."""
    
    id: str
    name: str
    number: str | None = None
    description: str | None = None
    status: str | None = None
    owner: str | None = None
    create_date: str | None = None
    change_date: str | None = None


class FeatureData(BaseModel):
    """VersionOne feature/epic data structure."""
    
    id: str
    name: str
    number: str | None = None
    description: str | None = None
    status: str | None = None
    owner: str | None = None
    create_date: str | None = None
    change_date: str | None = None


class StoriesResponse(BaseModel):
    """Response containing multiple stories."""
    
    total: int
    stories: list[StoryData]


class FeaturesResponse(BaseModel):
    """Response containing multiple features."""
    
    total: int
    features: list[FeatureData]


# VersionOne API client
class VersionOneClient:
    """Simple VersionOne API client."""
    
    def __init__(self):
        self.base_url = os.getenv('VERSIONONE_BASE_URL')
        self.access_token = os.getenv('VERSIONONE_ACCESS_TOKEN')
        
        if not self.base_url or not self.access_token:
            raise ValueError("Missing VERSIONONE_BASE_URL or VERSIONONE_ACCESS_TOKEN environment variables")
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def _make_request(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        """Make HTTP request to VersionOne API."""
        url = f"{self.base_url.rstrip('/')}/rest-1.v1/Data/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    def _extract_story_data(self, asset: dict) -> StoryData:
        """Extract story data from VersionOne asset."""
        attrs = asset.get('Attributes', {})
        return StoryData(
            id=asset.get('id', ''),
            name=attrs.get('Name', {}).get('value', ''),
            number=attrs.get('Number', {}).get('value'),
            description=attrs.get('Description', {}).get('value'),
            status=attrs.get('Status', {}).get('value'),
            owner=self._get_owner_name(attrs),
            create_date=attrs.get('CreateDate', {}).get('value'),
            change_date=attrs.get('ChangeDate', {}).get('value')
        )
    
    def _extract_feature_data(self, asset: dict) -> FeatureData:
        """Extract feature data from VersionOne asset."""
        attrs = asset.get('Attributes', {})
        return FeatureData(
            id=asset.get('id', ''),
            name=attrs.get('Name', {}).get('value', ''),
            number=attrs.get('Number', {}).get('value'),
            description=attrs.get('Description', {}).get('value'),
            status=attrs.get('Status', {}).get('value'),
            owner=self._get_owner_name(attrs),
            create_date=attrs.get('CreateDate', {}).get('value'),
            change_date=attrs.get('ChangeDate', {}).get('value')
        )
    
    def _get_owner_name(self, attrs: dict) -> str | None:
        """Extract owner name from attributes."""
        owner = attrs.get('Owner', {})
        if isinstance(owner.get('value'), dict):
            return owner['value'].get('Name')
        return owner.get('value')


# Global client instance
client = VersionOneClient()


@mcp.tool()
def get_stories(
    where_filter: str = "AssetState!=\"Dead\"",
    select_fields: str = "Name,Number,Status,Owner",
    page_size: int = 20,
    page_start: int = 0
) -> StoriesResponse:
    """Get a list of stories from VersionOne with optional filtering.
    
    Args:
        where_filter: Filter clause (e.g., 'AssetState!="Dead"')
        select_fields: Comma-separated list of fields to select
        page_size: Number of items per page (default: 20)
        page_start: Starting page number (default: 0)
    """
    import asyncio
    
    params = {
        'where': where_filter,
        'sel': select_fields,
        'pageSize': page_size,
        'pageStart': page_start
    }
    
    async def _get_stories():
        result = await client._make_request('Story', params)
        stories = [client._extract_story_data(asset) for asset in result.get('Assets', [])]
        return StoriesResponse(total=result.get('total', 0), stories=stories)
    
    return asyncio.run(_get_stories())


@mcp.tool()
def get_story_details(story_id: str) -> StoryData:
    """Get detailed information about a specific story by ID.
    
    Args:
        story_id: The ID of the story (e.g., 'Story:1234')
    """
    import asyncio
    
    params = {
        'sel': 'Name,Number,Description,Status,Owner,CreateDate,ChangeDate'
    }
    
    async def _get_story_details():
        # Extract just the ID part if full ID is provided
        if ':' in story_id:
            story_num = story_id.split(':')[1]
        else:
            story_num = story_id
            
        result = await client._make_request(f'Story/{story_num}', params)
        return client._extract_story_data(result)
    
    return asyncio.run(_get_story_details())


@mcp.tool()
def get_features(
    where_filter: str = "AssetState!=\"Dead\"",
    select_fields: str = "Name,Number,Status,Owner",
    page_size: int = 20,
    page_start: int = 0
) -> FeaturesResponse:
    """Get a list of features (Epics) from VersionOne with optional filtering.
    
    Args:
        where_filter: Filter clause (e.g., 'AssetState!="Dead"')
        select_fields: Comma-separated list of fields to select
        page_size: Number of items per page (default: 20)
        page_start: Starting page number (default: 0)
    """
    import asyncio
    
    params = {
        'where': where_filter,
        'sel': select_fields,
        'pageSize': page_size,
        'pageStart': page_start
    }
    
    async def _get_features():
        result = await client._make_request('Epic', params)
        features = [client._extract_feature_data(asset) for asset in result.get('Assets', [])]
        return FeaturesResponse(total=result.get('total', 0), features=features)
    
    return asyncio.run(_get_features())


@mcp.tool()
def get_feature_details(feature_id: str) -> FeatureData:
    """Get detailed information about a specific feature by ID.
    
    Args:
        feature_id: The ID of the feature/epic (e.g., 'Epic:1234')
    """
    import asyncio
    
    params = {
        'sel': 'Name,Number,Description,Status,Owner,CreateDate,ChangeDate'
    }
    
    async def _get_feature_details():
        # Extract just the ID part if full ID is provided
        if ':' in feature_id:
            feature_num = feature_id.split(':')[1]
        else:
            feature_num = feature_id
            
        result = await client._make_request(f'Epic/{feature_num}', params)
        return client._extract_feature_data(result)
    
    return asyncio.run(_get_feature_details()) 