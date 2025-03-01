from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Group, Quote, Agreement, EntryTicket, Meal, Hotel
import os

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_quote(self, group_data, quote_data):
        session = self.Session()
        try:
            # Create and save group
            group = Group(
                name=group_data['name'],
                num_paying=group_data['num_paying'],
                chaperone_type=group_data['chaperone_type'],
                num_chaperones=group_data['num_chaperones'],
                chaperone_ratio=group_data.get('chaperone_ratio')
            )
            session.add(group)
            session.flush()  # Get the group ID

            # Create and save quote
            quote = Quote(
                group_id=group.id,
                bus_cost=quote_data['bus_cost'],
                metro_cost=quote_data['metro_cost'],
                airline_cost=quote_data['airline_cost'],
                train_cost=quote_data['train_cost'],
                guide_rate=quote_data['guide_rate'],
                guide_days=quote_data['guide_days'],
                guide_tip=quote_data['guide_tip'],
                driver_tip=quote_data['driver_tip'],
                profit_amount=quote_data['profit_amount']
            )
            session.add(quote)
            session.flush()

            # Save entry tickets
            for ticket in quote_data['entry_tickets']:
                entry_ticket = EntryTicket(
                    quote_id=quote.id,
                    name=ticket['name'],
                    cost=ticket['cost']
                )
                session.add(entry_ticket)

            # Save meals
            for meal in quote_data['meals']:
                meal_entry = Meal(
                    quote_id=quote.id,
                    type=meal['type'],
                    cost=meal['cost']
                )
                session.add(meal_entry)

            # Save hotels
            for hotel_data in quote_data['hotels']:
                hotel = Hotel(
                    quote_id=quote.id,
                    name=hotel_data['name'],
                    cost_per_room=hotel_data['cost_per_room'],
                    high_occupancy_cost=hotel_data.get('high_occupancy_cost'),
                    has_high_occupancy=hotel_data['has_high_occupancy'],
                    tax_rate=hotel_data['tax_rate'],
                    occupancy_options=','.join(map(str, hotel_data['occupancy_options'])),
                    high_occupancy_options=','.join(map(str, hotel_data.get('high_occupancy_options', [])))
                )
                session.add(hotel)

            session.commit()
            return quote.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def load_quotes(self):
        session = self.Session()
        try:
            return session.query(Quote).all()
        finally:
            session.close()

    def create_agreement(self, quote_id, status="pending"):
        session = self.Session()
        try:
            agreement = Agreement(quote_id=quote_id, status=status)
            session.add(agreement)
            session.commit()
            return agreement.id
        finally:
            session.close()
