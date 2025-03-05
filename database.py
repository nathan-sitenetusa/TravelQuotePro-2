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

    def save_quote(self, group_data, quote_data, existing_group_id=None):
        """Save or update a quote"""
        session = self.Session()
        try:
            if existing_group_id:
                # Update existing group
                group = session.query(Group).filter_by(id=existing_group_id).first()
                if not group:
                    raise ValueError(f"No group found with ID: {existing_group_id}")

                # Update group details
                group.name = group_data['name']
                group.num_paying = group_data['num_paying']
                group.chaperone_type = group_data['chaperone_type']
                group.num_chaperones = group_data['num_chaperones']
                group.chaperone_ratio = group_data.get('chaperone_ratio')

                # Get existing quote
                quote = session.query(Quote).filter_by(group_id=existing_group_id).first()

                # Delete existing related records
                session.query(EntryTicket).filter_by(quote_id=quote.id).delete()
                session.query(Meal).filter_by(quote_id=quote.id).delete()
                session.query(Hotel).filter_by(quote_id=quote.id).delete()
            else:
                # Create new group and quote
                group = Group(
                    name=group_data['name'],
                    num_paying=group_data['num_paying'],
                    chaperone_type=group_data['chaperone_type'],
                    num_chaperones=group_data['num_chaperones'],
                    chaperone_ratio=group_data.get('chaperone_ratio')
                )
                session.add(group)
                session.flush()  # Get the group ID
                quote = Quote(group_id=group.id)
                session.add(quote)
                session.flush()

            # Update quote details
            quote.bus_cost = quote_data['bus_cost']
            quote.metro_cost = quote_data['metro_cost']
            quote.airline_cost = quote_data['airline_cost']
            quote.train_cost = quote_data['train_cost']
            quote.guide_rate = quote_data['guide_rate']
            quote.guide_days = quote_data['guide_days']
            quote.guide_tip = quote_data['guide_tip']
            quote.driver_tip = quote_data['driver_tip']
            quote.profit_amount = quote_data['profit_amount']

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

    def load_groups(self):
        """Load all groups with their latest quotes"""
        session = self.Session()
        try:
            groups = session.query(Group).all()
            return [{'id': group.id, 'name': group.name} for group in groups]
        finally:
            session.close()

    def load_quote(self, group_id):
        """Load a complete quote by group ID"""
        session = self.Session()
        try:
            group = session.query(Group).filter_by(id=group_id).first()
            if not group:
                return None

            quote = session.query(Quote).filter_by(group_id=group_id).first()
            if not quote:
                return None

            # Load entry tickets
            entry_tickets = [
                {'name': ticket.name, 'cost': ticket.cost}
                for ticket in quote.entry_tickets
            ]

            # Load meals
            meals = {
                'lunch': [meal.cost for meal in quote.meals if meal.type == 'lunch'],
                'dinner': [meal.cost for meal in quote.meals if meal.type == 'dinner']
            }

            # Load hotels
            hotels = []
            for hotel in quote.hotels:
                hotel_data = {
                    'name': hotel.name,
                    'cost_per_room': hotel.cost_per_room,
                    'high_occupancy_cost': hotel.high_occupancy_cost,
                    'has_high_occupancy': hotel.has_high_occupancy,
                    'tax_rate': hotel.tax_rate,
                    'occupancy_options': [int(x) for x in hotel.occupancy_options.split(',') if x],
                    'high_occupancy_options': [int(x) for x in hotel.high_occupancy_options.split(',') if x]
                }
                hotels.append(hotel_data)

            return {
                'group': {
                    'id': group.id,  
                    'name': group.name,
                    'num_paying': group.num_paying,
                    'chaperone_type': group.chaperone_type,
                    'num_chaperones': group.num_chaperones,
                    'chaperone_ratio': group.chaperone_ratio
                },
                'quote': {
                    'bus_cost': quote.bus_cost,
                    'metro_cost': quote.metro_cost,
                    'airline_cost': quote.airline_cost,
                    'train_cost': quote.train_cost,
                    'guide_rate': quote.guide_rate,
                    'guide_days': quote.guide_days,
                    'guide_tip': quote.guide_tip,
                    'driver_tip': quote.driver_tip,
                    'profit_amount': quote.profit_amount,
                    'entry_tickets': entry_tickets,
                    'meals': meals,
                    'hotels': hotels
                }
            }
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

    def delete_group(self, group_id):
        """Delete a group and all its associated data"""
        session = self.Session()
        try:
            group = session.query(Group).filter_by(id=group_id).first()
            if not group:
                raise ValueError(f"No group found with ID: {group_id}")

            # Get associated quote
            quote = session.query(Quote).filter_by(group_id=group_id).first()
            if quote:
                # Delete related records
                session.query(EntryTicket).filter_by(quote_id=quote.id).delete()
                session.query(Meal).filter_by(quote_id=quote.id).delete()
                session.query(Hotel).filter_by(quote_id=quote.id).delete()
                session.query(Agreement).filter_by(quote_id=quote.id).delete()
                # Delete quote
                session.delete(quote)

            # Delete group
            session.delete(group)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()