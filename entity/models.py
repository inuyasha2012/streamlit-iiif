from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ImageEntity(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=True)
    used = Column(Boolean, nullable=True, default=False)
    info_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)


class ManifestEntity(Base):
    __tablename__ = 'manifest'
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=True)
    public = Column(Boolean, nullable=True, default=False)
    thumbnail_url = Column(String, nullable=True)
    manifest_url = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    annotated = Column(Boolean, nullable=True, default=False)
    embedded = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)