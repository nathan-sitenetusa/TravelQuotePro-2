import streamlit as st
import numpy as np
from utils.calculations import (
    calculate_fixed_costs, calculate_guide_cost, calculate_entry_costs,
    calculate_meal_costs, calculate_total_per_person, calculate_final_price,
    calculate_chaperone_count
)
from utils.styling import set_page_style, show_header

def main():
    set_page_style()
    show_header()

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
            'tax_rate': None,
            'occupancy_options': [4, 5, 6, 7, 8]
        }]

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
                'tax_rate': None,
                'occupancy_options': [4, 5, 6, 7, 8]
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
                    "Cost per Room per Night",
                    min_value=0.0,
                    value=0.0,
                    key=f"room_cost_{i}"
                )

            with col2:
                st.session_state.hotels[i]['tax_rate'] = st.number_input(
                    "Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    key=f"tax_rate_{i}"
                )
                st.multiselect(
                    "Available Room Occupancies",
                    options=[3, 4, 5, 6, 7, 8],
                    default=[4, 5, 6, 7, 8],
                    key=f"occupancy_{i}",
                    help="Select all possible room occupancies for this hotel"
                )

    # Profit Amount
    profit_amount = st.number_input("Profit Amount per Person ($)", min_value=0.0, value=50.0)

    if st.button("Calculate Quotes", type="primary"):
        # Calculate components
        fixed_costs = calculate_fixed_costs(bus_cost, metro_cost, airline_cost, train_cost)
        guide_cost = calculate_guide_cost(guide_rate, guide_days, guide_tip)
        total_entry_costs = calculate_entry_costs(entry_costs)
        total_meal_costs = calculate_meal_costs(lunch_costs, dinner_costs)

        st.header("Quote Breakdown")

        for hotel in st.session_state.hotels:
            if hotel['name'] and hotel['cost_per_room']:
                st.subheader(f"📋 {hotel['name']}")

                total_per_person = calculate_total_per_person(
                    fixed_costs, guide_cost, total_entry_costs,
                    total_meal_costs, [hotel], num_paying, num_chaperones,
                    driver_tip, guide_days
                )

                price_tiers = calculate_final_price(total_per_person, profit_amount)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Cost Breakdown (per person)**")
                    st.write(f"Fixed Costs: ${fixed_costs/num_paying:,.2f}")
                    st.write(f"Guide Costs (inc. tips): ${guide_cost/num_paying:,.2f}")
                    st.write(f"Entry Tickets: ${total_entry_costs:,.2f}")
                    st.write(f"Meal Costs: ${total_meal_costs:,.2f}")
                    st.write(f"Room Costs: ${total_per_person:,.2f}")
                    st.write(f"Driver Tips: ${driver_tip*guide_days/num_paying:,.2f}")

                with col2:
                    st.markdown("**Price Tiers (including profit)**")
                    for group, price in price_tiers.items():
                        st.write(f"{group}: ${price:,.2f}")

                st.markdown("---")

if __name__ == "__main__":
    main()