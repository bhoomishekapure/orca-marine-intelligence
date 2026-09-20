import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class LocationModel(Base):
    __tablename__ = "locations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location_name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    category = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    active_vessels = Column(Integer, nullable=True)
    contact = Column(String, nullable=True)

class PFZZoneModel(Base):
    __tablename__ = "pfz_zones"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    reference_centre = Column(String, nullable=False)
    bearing_deg = Column(Float, nullable=False)
    direction = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    depth_range_m = Column(String, nullable=False)
    sst_celsius = Column(Float, nullable=False)
    chlorophyll_mg_m3 = Column(Float, nullable=False)
    target_species = Column(Text, nullable=False)
    coordinates_json = Column(Text, nullable=False)
    valid_from = Column(String, nullable=False)
    valid_to = Column(String, nullable=False)

class RestrictedZoneModel(Base):
    __tablename__ = "restricted_zones"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    restriction_level = Column(String, nullable=False)
    legal_basis = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    authority = Column(String, nullable=False)
    polygon_json = Column(Text, nullable=False)

class ConversationModel(Base):
    __tablename__ = "conversations"

    session_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("conversations.session_id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("ConversationModel", back_populates="messages")
