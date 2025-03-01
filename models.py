from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

Base = declarative_base()

class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=True)  # Made nullable for reusable hotels
    name = Column(String)
    cost_per_room = Column(Float)
    high_occupancy_cost = Column(Float)
    has_high_occupancy = Column(Boolean, default=False)
    tax_rate = Column(Float)
    occupancy_options = Column(String)  # Store as comma-separated string
    high_occupancy_options = Column(String)  # Store as comma-separated string
    is_reusable = Column(Boolean, default=False)  # New field for reusable hotels

    # Relationships
    quote = relationship('Quote', back_populates='hotels')

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    num_paying = Column(Integer, nullable=False)
    chaperone_type = Column(String)  # "Fixed Number" or "Ratio"
    num_chaperones = Column(Integer)
    chaperone_ratio = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quotes = relationship('Quote', back_populates='group')

class Quote(Base):
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    
    # Transportation costs
    bus_cost = Column(Float)
    metro_cost = Column(Float)
    airline_cost = Column(Float)
    train_cost = Column(Float)
    
    # Guide information
    guide_rate = Column(Float)
    guide_days = Column(Integer)
    guide_tip = Column(Float)
    driver_tip = Column(Float)
    
    # Profit
    profit_amount = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group = relationship('Group', back_populates='quotes')
    agreements = relationship('Agreement', back_populates='quote')
    entry_tickets = relationship('EntryTicket', back_populates='quote')
    meals = relationship('Meal', back_populates='quote')
    hotels = relationship('Hotel', back_populates='quote')

class Agreement(Base):
    __tablename__ = 'agreements'
    
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    status = Column(String)  # e.g., "pending", "accepted", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quote = relationship('Quote', back_populates='agreements')

class EntryTicket(Base):
    __tablename__ = 'entry_tickets'
    
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    name = Column(String)
    cost = Column(Float)
    
    # Relationships
    quote = relationship('Quote', back_populates='entry_tickets')

class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    type = Column(String)  # "lunch" or "dinner"
    cost = Column(Float)
    
    # Relationships
    quote = relationship('Quote', back_populates='meals')

# Database connection and initialization
def init_db():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine