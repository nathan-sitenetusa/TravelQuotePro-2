import streamlit as st
import numpy as np
import os
import math
from utils.calculations import (
    calculate_transportation_costs, calculate_guide_cost, calculate_entry_costs,
    calculate_meal_costs, calculate_total_per_person, calculate_final_price,
    calculate_chaperone_count, calculate_room_costs_by_occupancy
)
from utils.styling import set_page_style, show_header
from utils.pdf_generator import generate_quote_pdf
from database import DatabaseManager

def load_saved_data(db_manager, group_id):
    """Load saved quote data into session state"""
    data = db_manager.load_quote(group_id)
    if data:
        # Update session state with loaded data
        st.session_state.entry_tickets = data['quote']['entry_tickets']
        st.session_state.lunches = data['quote']['meals']['lunch']
        st.session_state.dinners = data['quote']['meals']['dinner']
        st.session_state.hotels = data['quote']['hotels']
        st.session_state.current_group_id = data['group']['id']  # Store current group ID
        return data
    return None

def main():
    set_page_style()
    show_header()

    # Initialize database manager
    db_manager = DatabaseManager()

    # Initialize session state
    if 'entry_tickets' not in st.session_state:
        st.session_state.entry_tickets = [{'name': '', 'cost': None}]
    if 'lunches' not in st.session_state:
        st.session_state.lunches = [None]
    if 'dinners' not in st.session_state:
        st.session_state.dinners = [None]
    if 'hotels' not in st.session_state:
        st.session_state.hotels = [{
            'name': '',
            'cost_per_room': None,
            'high_occupancy_cost': None,
            'has_high_occupancy': False,
            'tax_rate': None,
            'num_nights': 1,  # Added default value
            'occupancy_options': [3, 4, 5],
            'high_occupancy_options': [6, 7, 8]
        }]
    if 'current_group_id' not in st.session_state:
        st.session_state.current_group_id = None

    def clear_form():
        """Reset all form fields to their default values"""
        st.session_state.current_group_id = None
        st.session_state.loaded_data = None
        st.session_state.entry_tickets = [{'name': '', 'cost': None}]
        st.session_state.lunches = [None]
        st.session_state.dinners = [None]
        st.session_state.hotels = [{
            'name': '',
            'cost_per_room': None,
            'high_occupancy_cost': None,
            'has_high_occupancy': False,
            'tax_rate': None,
            'num_nights': 1,  # Added default value
            'occupancy_options': [3, 4, 5],
            'high_occupancy_options': [6, 7, 8]
        }]
        st.rerun()

    # Load Saved Quotes Section
    with st.expander("Load Saved Quote", expanded=False):
        groups = db_manager.load_groups()
        if groups:
            group_names = {f"{group['name']} (ID: {group['id']})": group['id'] for group in groups}
            col1, col2 = st.columns(2)

            with col1:
                selected_group = st.selectbox("Select a group to load", options=list(group_names.keys()))
                selected_group_id = group_names[selected_group]

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    if st.button("Load Quote"):
                        loaded_data = load_saved_data(db_manager, selected_group_id)
                        if loaded_data:
                            st.success("Quote loaded successfully!")
                            st.session_state.loaded_data = loaded_data
                            st.rerun()
                with col2_2:
                    # Initialize delete confirmation state if not exists
                    if 'delete_confirmation' not in st.session_state:
                        st.session_state.delete_confirmation = False

                    if not st.session_state.delete_confirmation:
                        if st.button("Delete Group", type="secondary"):
                            st.session_state.delete_confirmation = True
                            st.rerun()
                    else:
                        st.warning("Are you sure you want to delete this group?")
                        if st.button("Confirm Delete", type="primary"):
                            try:
                                db_manager.delete_group(selected_group_id)
                                st.success("Group deleted successfully!")
                                st.session_state.delete_confirmation = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting group: {str(e)}")
                        if st.button("Cancel", type="secondary"):
                            st.session_state.delete_confirmation = False
                            st.rerun()
        else:
            st.info("No saved quotes found.")

    # Get loaded data if available
    loaded_data = st.session_state.get('loaded_data', None)

    # Group Name (for saving quotes)
    initial_name = loaded_data['group']['name'] if loaded_data else ""
    group_name = st.text_input("Group/Organization Name", value=initial_name)

    # Group Information
    with st.expander("Group Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            initial_num_paying = loaded_data['group']['num_paying'] if loaded_data else 10
            num_paying = st.number_input("Number of Paying Participants",
                                       min_value=1, value=initial_num_paying)

            initial_chaperone_type = loaded_data['group']['chaperone_type'] if loaded_data else "Fixed Number"
            chaperone_type = st.radio("Chaperone Calculation Method",
                                        ["Fixed Number", "Ratio (1 per X paid)"],
                                        index=0 if initial_chaperone_type == "Fixed Number" else 1)

            if chaperone_type == "Fixed Number":
                initial_num_chaperones = loaded_data['group']['num_chaperones'] if loaded_data else 1
                num_chaperones = st.number_input("Number of FREE Chaperones",
                                                min_value=0, value=initial_num_chaperones)
                chaperone_ratio = None
            else:
                initial_ratio = loaded_data['group']['chaperone_ratio'] if loaded_data else 10
                chaperone_ratio = st.number_input("Number of Paying per FREE Chaperone",
                                                 min_value=1, value=initial_ratio)
                num_chaperones = calculate_chaperone_count(num_paying, ratio=chaperone_ratio)

        with col2:
            st.markdown("### Group Summary")
            st.write(f"Paying Participants: {num_paying}")
            st.write(f"Free Chaperones: {num_chaperones}")
            st.write(f"Total Participants: {num_paying + num_chaperones}")

    # Transportation Costs
    with st.expander("Transportation Costs", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            initial_bus = loaded_data['quote']['bus_cost'] if loaded_data else 0.0
            bus_cost = st.number_input("Bus Cost", min_value=0.0, value=initial_bus)

            initial_metro = loaded_data['quote']['metro_cost'] if loaded_data else 0.0
            metro_cost = st.number_input("Metro Cost", min_value=0.0, value=initial_metro)
        with col2:
            initial_airline = loaded_data['quote']['airline_cost'] if loaded_data else 0.0
            airline_cost = st.number_input("Airline Cost", min_value=0.0, value=initial_airline)

            initial_train = loaded_data['quote']['train_cost'] if loaded_data else 0.0
            train_cost = st.number_input("Train Cost", min_value=0.0, value=initial_train)

    # Tour Guide Information
    with st.expander("Tour Guide Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            initial_guide_rate = loaded_data['quote']['guide_rate'] if loaded_data else 0.0
            guide_rate = st.number_input("Daily Guide Rate", min_value=0.0, value=initial_guide_rate)

            initial_guide_days = loaded_data['quote']['guide_days'] if loaded_data else 1
            guide_days = st.number_input("Number of Guide Days", min_value=0, value=initial_guide_days)
        with col2:
            initial_guide_tip = loaded_data['quote']['guide_tip'] if loaded_data else 0.0
            guide_tip = st.number_input("Guide Tip per Day", min_value=0.0, value=initial_guide_tip)

            initial_driver_tip = loaded_data['quote']['driver_tip'] if loaded_data else 0.0
            driver_tip = st.number_input("Driver Tip per Day", min_value=0.0, value=initial_driver_tip)

    # Entry Tickets
    with st.expander("Entry Tickets", expanded=True):
        if st.button("Add Entry Ticket"):
            st.session_state.entry_tickets.append({'name': '', 'cost': None})

        entry_costs = []
        for i, ticket in enumerate(st.session_state.entry_tickets):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.session_state.entry_tickets[i]['name'] = st.text_input(
                    f"Entry Ticket {i+1} Name",
                    value=ticket['name'],
                    key=f"ticket_name_{i}"
                )
            with col2:
                cost = st.number_input(
                    f"Cost",
                    min_value=0.0,
                    value=ticket['cost'] if ticket['cost'] is not None else 0.0,
                    key=f"entry_{i}"
                )
                st.session_state.entry_tickets[i]['cost'] = cost
                entry_costs.append(cost)

    # Meal Costs
    with st.expander("Meal Costs (Per Person)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Lunch"):
                st.session_state.lunches.append(None)
            lunch_costs = []
            for i in range(len(st.session_state.lunches)):
                initial_lunch = st.session_state.lunches[i] if st.session_state.lunches[i] is not None else 0.0
                cost = st.number_input(f"Lunch {i+1} Cost",
                                    min_value=0.0, value=initial_lunch, key=f"lunch_{i}")
                lunch_costs.append(cost)

        with col2:
            if st.button("Add Dinner"):
                st.session_state.dinners.append(None)
            dinner_costs = []
            for i in range(len(st.session_state.dinners)):
                initial_dinner = st.session_state.dinners[i] if st.session_state.dinners[i] is not None else 0.0
                cost = st.number_input(f"Dinner {i+1} Cost",
                                    min_value=0.0, value=initial_dinner, key=f"dinner_{i}")
                dinner_costs.append(cost)

    # Hotel Information
    with st.expander("Hotel Information", expanded=True):
        if st.button("Add Hotel"):
            st.session_state.hotels.append({
                'name': '',
                'cost_per_room': None,
                'high_occupancy_cost': None,
                'has_high_occupancy': False,
                'tax_rate': None,
                'num_nights': 1, # Added default value
                'occupancy_options': [3, 4, 5],
                'high_occupancy_options': [6, 7, 8]
            })

        for i, hotel in enumerate(st.session_state.hotels):
            st.markdown(f"### Hotel {i+1}")
            col1, col2 = st.columns(2)

            with col1:
                st.session_state.hotels[i]['name'] = st.text_input(
                    "Hotel Name",
                    value=hotel['name'],
                    key=f"hotel_name_{i}"
                )

                st.session_state.hotels[i]['cost_per_room'] = st.number_input(
                    "Standard Rate (1-5 persons)",
                    min_value=0.0,
                    value=hotel['cost_per_room'] if hotel['cost_per_room'] is not None else 0.0,
                    key=f"room_cost_{i}"
                )

                st.session_state.hotels[i]['tax_rate'] = st.number_input(
                    "Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=hotel['tax_rate'] if hotel['tax_rate'] is not None else 0.0,
                    key=f"tax_rate_{i}"
                )

            with col2:
                st.session_state.hotels[i]['has_high_occupancy'] = st.checkbox(
                    "Enable 6-8 Person Rate",
                    value=hotel['has_high_occupancy'],
                    key=f"high_occupancy_enabled_{i}"
                )

                if st.session_state.hotels[i]['has_high_occupancy']:
                    st.session_state.hotels[i]['high_occupancy_cost'] = st.number_input(
                        "High Occupancy Rate (6-8 persons)",
                        min_value=0.0,
                        value=hotel['high_occupancy_cost'] if hotel['high_occupancy_cost'] is not None else 0.0,
                        key=f"high_occupancy_cost_{i}"
                    )

            # Occupancy options
            st.session_state.hotels[i]['occupancy_options'] = sorted(
                st.multiselect(
                    "Standard Occupancy Options (1-5)",
                    options=[3, 4, 5],
                    default=hotel['occupancy_options'],
                    key=f"occupancy_{i}"
                )
            )

            #Added Number of Nights input here
            st.session_state.hotels[i]['num_nights'] = st.number_input(
                "Number of Nights",
                min_value=1,
                value=hotel['num_nights'] if 'num_nights' in hotel and hotel['num_nights'] is not None else 1,
                key=f"num_nights_{i}"
            )


            if st.session_state.hotels[i]['has_high_occupancy']:
                st.session_state.hotels[i]['high_occupancy_options'] = sorted(
                    st.multiselect(
                        "High Occupancy Options (6-8)",
                        options=[6, 7, 8],
                        default=hotel['high_occupancy_options'],
                        key=f"high_occupancy_{i}"
                    )
                )
            else:
                st.session_state.hotels[i]['high_occupancy_options'] = []

            if i < len(st.session_state.hotels) - 1:
                st.markdown("---")

    # Profit Amount and Price Adjustments
    col1, col2 = st.columns(2)
    with col1:
        initial_profit = loaded_data['quote']['profit_amount'] if loaded_data else 50.0
        profit_amount = st.number_input("Profit Amount per Person ($)", min_value=0.0, value=initial_profit)
    with col2:
        use_range_factor = st.checkbox("Apply Factor to Higher Ranges", value=False)
        if use_range_factor:
            range_factor = st.number_input("Factor Amount to Subtract ($)", min_value=0.0, value=15.0)
        else:
            range_factor = 0.0

    # Save/Update buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        calculate_button = st.button("Calculate Quotes", type="primary")
    with col2:
        save_button = False  # Initialize save_button
        if group_name:
            if st.session_state.current_group_id:
                save_button = st.button("Update Quote")
            else:
                save_button = st.button("Save New Quote")
    with col3:
        if st.session_state.current_group_id:
            if st.button("Clear Form"):
                clear_form()

    # Always calculate quotes if we have the necessary information
    if num_paying > 0:
        # Initialize room_costs_by_occupancy
        room_costs_by_occupancy = {}

        # Calculate components
        transportation_costs = calculate_transportation_costs(
            bus_cost, metro_cost, airline_cost, train_cost,
            num_paying, num_chaperones
        )
        guide_cost = calculate_guide_cost(guide_rate, guide_days, guide_tip)
        total_entry_costs = calculate_entry_costs(entry_costs, num_paying, num_chaperones)
        total_meal_costs = calculate_meal_costs(lunch_costs, dinner_costs, num_paying, num_chaperones)

        st.header("Quote Breakdown")

        for hotel in st.session_state.hotels:
            if hotel['cost_per_room'] or (hotel['has_high_occupancy'] and hotel['high_occupancy_cost']):
                st.subheader(f"📋 {hotel['name']}")

                # Calculate costs for each occupancy option
                room_costs_by_occupancy = calculate_room_costs_by_occupancy(
                    hotel, num_paying, num_chaperones
                )

                # Create price table
                st.markdown("### Price Table by Occupancy and Group Size")

                # Get all occupancy options
                occupancies = sorted(room_costs_by_occupancy.keys())

                # Create the header row
                header = ["Group Size"] + [f"{occ}/room" for occ in occupancies]

                # Calculate dynamic ranges based on num_paying
                range_size = 5
                range_start = (num_paying // range_size) * range_size
                rows = []
                
                # Generate ranges (2 below median, median, 2 above median)
                for i in range(-2, 3):  # -2, -1, 0, 1, 2
                    start = range_start + (i * range_size)
                    end = start + range_size - 1
                    # Skip ranges that would start below 1
                    if start < 1:
                        continue
                    range_name = f"{start}-{end} paying"
                    multiplier = 1.15 if start < 14 else (1.10 if start < 17 else (1.05 if start < 21 else 1.00))
                    row = [range_name]
                    for occupancy in occupancies:
                        room_cost = room_costs_by_occupancy[occupancy]

                        # Calculate non-hotel costs first
                        base_costs = (
                            transportation_costs +  # Transportation costs
                            guide_cost/num_paying + # Guide costs divided by paying participants
                            total_entry_costs +    # Entry costs (already includes chaperone distribution)
                            total_meal_costs +     # Meal costs (already includes chaperone distribution)
                            driver_tip*guide_days/num_paying  # Driver tips per paying person
                        )

                        # Apply multiplier only to base costs and profit
                        adjusted_base_costs = (base_costs + profit_amount) * multiplier

                        # Add hotel costs separately (no multiplier)
                        final_price = adjusted_base_costs + room_cost

                        # Apply range factor for ranges above median
                        if use_range_factor and i > 0:  # i > 0 means we're above the median range
                            factor_adjustment = range_factor * i  # multiply factor by how many ranges above median
                            final_price = final_price - factor_adjustment
                        
                        # Round to whole dollars
                        final_price = math.ceil(final_price)
                        row.append(f"${final_price:,}")
                    rows.append(row)

                # Display the table
                st.table([header] + rows)

                # Show cost breakdown for reference
                st.markdown("#### Cost Breakdown (per paying person)")
                st.write(f"Transportation Costs: ${transportation_costs:,.2f}")
                st.write(f"Guide Costs (inc. tips): ${guide_cost/num_paying:,.2f}")
                st.write(f"Entry Tickets (inc. chaperones): ${total_entry_costs:,.2f}")
                st.write(f"Meal Costs (inc. chaperones): ${total_meal_costs:,.2f}")
                if any(room_costs_by_occupancy.values()):
                    st.write(f"Room Costs (sample for {list(room_costs_by_occupancy.keys())[0]}/room): ${list(room_costs_by_occupancy.values())[0]:,.2f}")
                st.write(f"Driver Tips: ${driver_tip*guide_days/num_paying:,.2f}")

                st.markdown("---")

        # Store calculated values in session state for PDF generation
        if not hasattr(st.session_state, 'calculated_values'):
            st.session_state.calculated_values = {}

        st.session_state.calculated_values = {
            'transportation_costs': transportation_costs,
            'guide_cost': guide_cost,
            'total_entry_costs': total_entry_costs,
            'total_meal_costs': total_meal_costs,
            'room_costs_by_occupancy': room_costs_by_occupancy,
            #'price_tiers': price_tiers # Removed as price tiers are now in the table
        }

    # Save/Update Quote logic
    if save_button and group_name:
        # Prepare data for saving
        group_data = {
            'name': group_name,
            'num_paying': num_paying,
            'chaperone_type': chaperone_type,
            'num_chaperones': num_chaperones,
            'chaperone_ratio': chaperone_ratio
        }

        quote_data = {
            'bus_cost': bus_cost,
            'metro_cost': metro_cost,
            'airline_cost': airline_cost,
            'train_cost': train_cost,
            'guide_rate': guide_rate,
            'guide_days': guide_days,
            'guide_tip': guide_tip,
            'driver_tip': driver_tip,
            'profit_amount': profit_amount,
            'entry_tickets': [
                {'name': ticket['name'], 'cost': ticket['cost']}
                for ticket in st.session_state.entry_tickets
            ],
            'meals': (
                [{'type': 'lunch', 'cost': cost} for cost in lunch_costs] +
                [{'type': 'dinner', 'cost': cost} for cost in dinner_costs]
            ),
            'hotels': st.session_state.hotels
        }

        try:
            quote_id = db_manager.save_quote(group_data, quote_data, st.session_state.current_group_id)
            if st.session_state.current_group_id:
                st.success(f"Quote updated successfully! Quote ID: {quote_id}")
            else:
                st.success(f"Quote saved successfully! Quote ID: {quote_id}")
        except Exception as e:
            st.error(f"Error saving quote: {str(e)}")

    # PDF Generation Section
    if st.session_state.current_group_id and group_name:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate PDF Quote", key="generate_pdf"):
                try:
                    # Create quotes directory if it doesn't exist
                    os.makedirs("quotes", exist_ok=True)

                    # Generate PDF
                    pdf_path = f"quotes/quote_{st.session_state.current_group_id}.pdf"
                    current_quote = {
                        'group': {
                            'name': group_name,
                            'num_paying': num_paying,
                            'num_chaperones': num_chaperones
                        },
                        'quote': {
                            'bus_cost': bus_cost,
                            'metro_cost': metro_cost,
                            'airline_cost': airline_cost,
                            'train_cost': train_cost,
                            'guide_rate': guide_rate,
                            'guide_days': guide_days,
                            'guide_tip': guide_tip,
                            'driver_tip': driver_tip,
                            'profit_amount': profit_amount,
                            'entry_tickets': st.session_state.entry_tickets,
                            'meals': [{'type':'lunch','cost':cost} for cost in lunch_costs] + 
                                   [{'type':'dinner','cost':cost} for cost in dinner_costs],
                            'hotels': st.session_state.hotels
                        }
                    }

                    generate_quote_pdf(current_quote, pdf_path)
                    st.session_state.pdf_ready = True
                    st.session_state.pdf_path = pdf_path
                    st.success("PDF generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

        # Show download button if PDF is ready
        with col2:
            if hasattr(st.session_state, 'pdf_ready') and st.session_state.pdf_ready:
                with open(st.session_state.pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Quote PDF",
                        data=pdf_file,
                        file_name=f"travel_quote_{group_name.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()