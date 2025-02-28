import streamlit as st
import numpy as np
from utils.calculations import (
    calculate_fixed_costs, calculate_guide_cost, calculate_entry_costs,
    calculate_meal_costs, calculate_total_per_person, calculate_price_tiers
)
from utils.styling import set_page_style, show_header

def main():
    set_page_style()
    show_header()
    
    # Initialize session state for entry tickets and meals
    if 'entry_tickets' not in st.session_state:
        st.session_state.entry_tickets = [None]
    if 'lunches' not in st.session_state:
        st.session_state.lunches = [None]
    if 'dinners' not in st.session_state:
        st.session_state.dinners = [None]

    # Group Information
    with st.expander("Group Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            num_people = st.number_input("Number of People", min_value=1, value=10)
        with col2:
            num_chaperones = st.number_input("Number of FREE Chaperones", 
                                           min_value=0, value=1)

    # Transportation Costs
    with st.expander("Transportation Costs", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            bus_cost = st.number_input("Bus Cost", min_value=0.0, value=0.0)
            metro_cost = st.number_input("Metro Cost", min_value=0.0, value=0.0)
        with col2:
            airline_cost = st.number_input("Airline Cost", min_value=0.0, value=0.0)
            train_cost = st.number_input("Train Cost", min_value=0.0, value=0.0)

    # Guide Costs
    with st.expander("Tour Guide Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            guide_rate = st.number_input("Daily Guide Rate", min_value=0.0, value=0.0)
        with col2:
            guide_days = st.number_input("Number of Guide Days", min_value=0, value=1)

    # Entry Tickets
    with st.expander("Entry Tickets", expanded=True):
        if st.button("Add Entry Ticket"):
            st.session_state.entry_tickets.append(None)
        
        entry_costs = []
        for i in range(len(st.session_state.entry_tickets)):
            cost = st.number_input(f"Entry Ticket {i+1} Cost", 
                                 min_value=0.0, value=0.0, key=f"entry_{i}")
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

    # Hotel Costs
    with st.expander("Hotel Information", expanded=True):
        room_cost = st.number_input("Cost per Room per Night", 
                                  min_value=0.0, value=0.0)

    # Profit Margin
    margin = st.slider("Profit Margin (%)", min_value=0, max_value=100, value=20)

    if st.button("Calculate Quotes", type="primary"):
        # Calculate components
        fixed_costs = calculate_fixed_costs(bus_cost, metro_cost, 
                                         airline_cost, train_cost)
        guide_cost = calculate_guide_cost(guide_rate, guide_days)
        total_entry_costs = calculate_entry_costs(entry_costs)
        total_meal_costs = calculate_meal_costs(lunch_costs, dinner_costs)

        # Calculate for different occupancies
        st.header("Quote Breakdown")
        occupancies = [7, 6, 5, 4, 3]
        
        for occupancy in occupancies:
            st.subheader(f"📋 {occupancy} People per Room")
            
            total_per_person = calculate_total_per_person(
                fixed_costs, guide_cost, total_entry_costs,
                total_meal_costs, room_cost, num_people,
                occupancy, num_chaperones
            )
            
            price_tiers = calculate_price_tiers(total_per_person, margin)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Cost Breakdown (per person)**")
                st.write(f"Fixed Costs: ${fixed_costs/max(num_people-num_chaperones, 1):,.2f}")
                st.write(f"Guide Costs: ${guide_cost/max(num_people-num_chaperones, 1):,.2f}")
                st.write(f"Entry Tickets: ${total_entry_costs:,.2f}")
                st.write(f"Meal Costs: ${total_meal_costs:,.2f}")
                st.write(f"Room Costs: ${total_per_person:,.2f}")
            
            with col2:
                st.markdown("**Price Tiers (including margin)**")
                for group, price in price_tiers.items():
                    st.write(f"{group}: ${price:,.2f}")
            
            st.markdown("---")

if __name__ == "__main__":
    main()
