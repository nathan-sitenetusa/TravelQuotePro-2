import streamlit as st
import numpy as np
from utils.calculations import (
    calculate_fixed_costs, calculate_guide_cost, calculate_entry_costs,
    calculate_meal_costs, calculate_total_per_person, calculate_final_price,
    calculate_chaperone_count, calculate_room_costs_by_occupancy
)
from utils.styling import set_page_style, show_header
from database import DatabaseManager

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
            'occupancy_options': [3, 4, 5],
            'high_occupancy_options': [6, 7, 8]
        }]

    # Group Name (for saving quotes)
    group_name = st.text_input("Group/Organization Name")

    # Group Information
    with st.expander("Group Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            num_paying = st.number_input("Number of Paying Participants", min_value=1, value=10)
            chaperone_type = st.radio("Chaperone Calculation Method",
                                    ["Fixed Number", "Ratio (1 per X paid)"])

            if chaperone_type == "Fixed Number":
                num_chaperones = st.number_input("Number of FREE Chaperones",
                                               min_value=0, value=1)
                chaperone_ratio = None
            else:
                chaperone_ratio = st.number_input("Number of Paying per FREE Chaperone",
                                                min_value=1, value=10)
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
            bus_cost = st.number_input("Bus Cost", min_value=0.0, value=0.0)
            metro_cost = st.number_input("Metro Cost", min_value=0.0, value=0.0)
        with col2:
            airline_cost = st.number_input("Airline Cost", min_value=0.0, value=0.0)
            train_cost = st.number_input("Train Cost", min_value=0.0, value=0.0)

    # Tour Guide Information
    with st.expander("Tour Guide Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            guide_rate = st.number_input("Daily Guide Rate", min_value=0.0, value=0.0)
            guide_days = st.number_input("Number of Guide Days", min_value=0, value=1)
        with col2:
            guide_tip = st.number_input("Guide Tip per Day", min_value=0.0, value=0.0)
            driver_tip = st.number_input("Driver Tip per Day", min_value=0.0, value=0.0)

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
                    value=0.0,
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
                cost = st.number_input(f"Lunch {i+1} Cost",
                                    min_value=0.0, value=0.0, key=f"lunch_{i}")
                lunch_costs.append(cost)

        with col2:
            if st.button("Add Dinner"):
                st.session_state.dinners.append(None)
            dinner_costs = []
            for i in range(len(st.session_state.dinners)):
                cost = st.number_input(f"Dinner {i+1} Cost",
                                    min_value=0.0, value=0.0, key=f"dinner_{i}")
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
                'occupancy_options': [3, 4, 5],
                'high_occupancy_options': [6, 7, 8]
            })

        for i, hotel in enumerate(st.session_state.hotels):
            st.markdown(f"### Hotel {i+1}")

            # Hotel Name
            st.session_state.hotels[i]['name'] = st.text_input(
                "Hotel Name",
                value=hotel['name'],
                key=f"hotel_name_{i}"
            )

            col1, col2 = st.columns(2)
            with col1:
                # Standard occupancy rate
                st.session_state.hotels[i]['cost_per_room'] = st.number_input(
                    "Standard Rate (1-5 persons)",
                    min_value=0.0,
                    value=0.0,
                    key=f"room_cost_{i}"
                )

                # Tax rate
                st.session_state.hotels[i]['tax_rate'] = st.number_input(
                    "Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    key=f"tax_rate_{i}"
                )

            with col2:
                # High occupancy option
                st.session_state.hotels[i]['has_high_occupancy'] = st.checkbox(
                    "Enable 6-8 Person Rate",
                    value=hotel['has_high_occupancy'],
                    key=f"high_occupancy_enabled_{i}"
                )

                if st.session_state.hotels[i]['has_high_occupancy']:
                    st.session_state.hotels[i]['high_occupancy_cost'] = st.number_input(
                        "High Occupancy Rate (6-8 persons)",
                        min_value=0.0,
                        value=0.0,
                        key=f"high_occupancy_cost_{i}"
                    )

            # Occupancy options
            st.session_state.hotels[i]['occupancy_options'] = sorted(
                st.multiselect(
                    "Standard Occupancy Options (1-5)",
                    options=[3, 4, 5],
                    default=[3, 4, 5],
                    key=f"occupancy_{i}"
                )
            )

            if st.session_state.hotels[i]['has_high_occupancy']:
                st.session_state.hotels[i]['high_occupancy_options'] = sorted(
                    st.multiselect(
                        "High Occupancy Options (6-8)",
                        options=[6, 7, 8],
                        default=[6, 7, 8],
                        key=f"high_occupancy_{i}"
                    )
                )
            else:
                st.session_state.hotels[i]['high_occupancy_options'] = []

    # Profit Amount
    profit_amount = st.number_input("Profit Amount per Person ($)", min_value=0.0, value=50.0)

    col1, col2 = st.columns(2)
    with col1:
        calculate_button = st.button("Calculate Quotes", type="primary")
    with col2:
        if group_name:
            save_button = st.button("Save Quote")

    if calculate_button:
        # Calculate components
        fixed_costs = calculate_fixed_costs(bus_cost, metro_cost, airline_cost, train_cost,
                                            num_paying, num_chaperones)
        guide_cost = calculate_guide_cost(guide_rate, guide_days, guide_tip)
        total_entry_costs = calculate_entry_costs(entry_costs, num_paying, num_chaperones)
        total_meal_costs = calculate_meal_costs(lunch_costs, dinner_costs, num_paying, num_chaperones)

        st.header("Quote Breakdown")

        for hotel in st.session_state.hotels:
            if hotel['name'] and (hotel['cost_per_room'] or 
                                (hotel['has_high_occupancy'] and hotel['high_occupancy_cost'])):
                st.subheader(f"📋 {hotel['name']}")

                # Calculate costs for each occupancy option
                room_costs_by_occupancy = calculate_room_costs_by_occupancy(
                    hotel, num_paying, num_chaperones
                )

                for occupancy, room_cost in room_costs_by_occupancy.items():
                    st.markdown(f"#### {occupancy} People per Room")

                    total_per_person = calculate_total_per_person(
                        fixed_costs, guide_cost, total_entry_costs,
                        total_meal_costs, room_cost, num_paying, num_chaperones,
                        driver_tip, guide_days
                    )

                    price_tiers = calculate_final_price(total_per_person, profit_amount)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Cost Breakdown (per paying person)**")
                        st.write(f"Fixed Costs (inc. chaperones): ${fixed_costs:,.2f}")
                        st.write(f"Guide Costs (inc. tips): ${guide_cost/num_paying:,.2f}")
                        st.write(f"Entry Tickets (inc. chaperones): ${total_entry_costs:,.2f}")
                        st.write(f"Meal Costs (inc. chaperones): ${total_meal_costs:,.2f}")
                        st.write(f"Room Costs (inc. chaperone rooms): ${room_cost:,.2f}")
                        st.write(f"Driver Tips: ${driver_tip*guide_days/num_paying:,.2f}")

                    with col2:
                        st.markdown("**Price Tiers (including profit)**")
                        for group, price in price_tiers.items():
                            st.write(f"{group}: ${price:,.2f}")

                    st.markdown("---")

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
            quote_id = db_manager.save_quote(group_data, quote_data)
            st.success(f"Quote saved successfully! Quote ID: {quote_id}")
        except Exception as e:
            st.error(f"Error saving quote: {str(e)}")

if __name__ == "__main__":
    main()