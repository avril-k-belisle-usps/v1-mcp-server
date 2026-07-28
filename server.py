#!/usr/bin/env python3
"""
VersionOne MCP Server using FastMCP

A simplified Model Context Protocol server for VersionOne API integration.
"""

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP


# Persistent client instance — set during lifespan startup
client: "VersionOneClient | None" = None


@asynccontextmanager
async def lifespan(server):
    global client
    client = VersionOneClient()
    yield
    await client.close()


# Create the FastMCP server
mcp = FastMCP("VersionOne", lifespan=lifespan)


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
        # Persistent HTTP client - connection pool reused across all tool calls
        self._http_client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def close(self):
        """Release the persistent HTTP connection pool."""
        await self._http_client.aclose()

    async def _make_request(self, endpoint: str, params: dict | None = None) -> dict[str, Any]:
        """Make HTTP request to VersionOne API."""
        url = f"{self.base_url.rstrip('/')}/rest-1.v1/Data/{endpoint}"
        response = await self._http_client.get(url, params=params)
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




@mcp.tool()
async def get_stories(
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
    params = {
        'where': where_filter,
        'sel': select_fields,
        'pageSize': page_size,
        'pageStart': page_start
    }
    result = await client._make_request('Story', params)
    stories = [client._extract_story_data(asset) for asset in result.get('Assets', [])]
    return StoriesResponse(total=result.get('total', 0), stories=stories)


@mcp.tool()
async def get_story_details(story_id: str) -> StoryData:
    """Get detailed information about a specific story by ID.
    
    Args:
        story_id: The ID of the story (e.g., 'Story:1234')
    """
    params = {
        'sel': 'Name,Number,Description,Status,Owner,CreateDate,ChangeDate'
    }
    story_num = story_id.split(':')[1] if ':' in story_id else story_id
    result = await client._make_request(f'Story/{story_num}', params)
    return client._extract_story_data(result)


@mcp.tool()
async def get_features(
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
    params = {
        'where': where_filter,
        'sel': select_fields,
        'pageSize': page_size,
        'pageStart': page_start
    }
    result = await client._make_request('Epic', params)
    features = [client._extract_feature_data(asset) for asset in result.get('Assets', [])]
    return FeaturesResponse(total=result.get('total', 0), features=features)


@mcp.tool()
async def get_feature_details(feature_id: str) -> FeatureData:
    """Get detailed information about a specific feature by ID.
    
    Args:
        feature_id: The ID of the feature/epic (e.g., 'Epic:1234')
    """
    params = {
        'sel': 'Name,Number,Description,Status,Owner,CreateDate,ChangeDate'
    }
    feature_num = feature_id.split(':')[1] if ':' in feature_id else feature_id
    result = await client._make_request(f'Epic/{feature_num}', params)
    return client._extract_feature_data(result) 