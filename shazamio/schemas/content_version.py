from pydantic import BaseModel, Field


class ContentVersion(BaseModel):
    rtci: int = Field(..., alias="RTCI")
    mz_indexer: int = Field(..., alias="MZ_INDEXER")


class MetaContentVersion(BaseModel):
    content_version: ContentVersion = Field(..., alias="contentVersion")
