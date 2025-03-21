import numpy as np

def calculate_transportation_costs(bus_cost, metro_cost, airline_cost, train_cost, num_paying, num_chaperones):
    """Calculate total transportation costs with proper distribution of chaperone costs"""
    # Bus cost is divided equally among paying participants
    bus_per_paying = bus_cost / num_paying if num_paying > 0 else 0

    # Per person costs (including distribution of chaperone costs)
    per_person_costs = sum(filter(None, [metro_cost, airline_cost, train_cost]))
    if per_person_costs > 0 and num_paying > 0:
        # Add chaperone costs to paying participants
        chaperone_distribution = (per_person_costs * num_chaperones) / num_paying
        per_person_costs = per_person_costs + chaperone_distribution

    return bus_per_paying + per_person_costs

def calculate_guide_cost(daily_rate, num_days, guide_tip_per_day=0):
    """Calculate total guide cost including tips"""
    base_cost = daily_rate * num_days if daily_rate and num_days else 0
    tip_cost = guide_tip_per_day * num_days if guide_tip_per_day and num_days else 0
    return base_cost + tip_cost

def calculate_entry_costs(entry_costs, num_paying, num_chaperones):
    """Calculate total entry costs per paying person, including chaperone costs"""
    cost_per_person = sum(cost for cost in entry_costs if cost)
    # Add chaperone costs to paying participants
    chaperone_distribution = (cost_per_person * num_chaperones / num_paying) if num_paying > 0 else 0
    return cost_per_person + chaperone_distribution

def calculate_meal_costs(lunch_costs, dinner_costs, num_paying, num_chaperones):
    """Calculate total meal costs per paying person, including chaperone meals"""
    total_per_person = sum(lunch_costs + dinner_costs)
    # Add chaperone meal costs to paying participants
    chaperone_distribution = (total_per_person * num_chaperones / num_paying) if num_paying > 0 else 0
    return total_per_person + chaperone_distribution

def calculate_chaperone_hotel_rooms(num_chaperones):
    """Calculate number of hotel rooms needed for chaperones (2 per room)"""
    return np.ceil(num_chaperones / 2)

def calculate_room_costs_by_occupancy(hotel, num_paying, num_chaperones):
    """Calculate room costs for different occupancy scenarios"""
    costs_by_occupancy = {}

    # Get base room costs with tax
    base_tax_rate = hotel['tax_rate'] / 100 if hotel['tax_rate'] else 0
    num_nights = hotel['num_nights'] if hotel['num_nights'] else 1

    # All possible occupancy options
    all_occupancies = list(range(1, 6))  # 1-5 persons
    if hotel['has_high_occupancy']:
        all_occupancies.extend([6, 7, 8])

    # Calculate costs for each occupancy
    if hotel['cost_per_room']:
        standard_room_cost = hotel['cost_per_room'] * num_nights * (1 + base_tax_rate)
        for occupancy in all_occupancies:
            if occupancy <= 5:
                costs_by_occupancy[occupancy] = calculate_room_cost_for_occupancy(
                    standard_room_cost, occupancy, num_paying, num_chaperones
                )

    # High occupancy calculations (6-8 persons)
    if hotel['has_high_occupancy'] and hotel['high_occupancy_cost']:
        high_occupancy_room_cost = hotel['high_occupancy_cost'] * num_nights * (1 + base_tax_rate)
        for occupancy in [6, 7, 8]:
            costs_by_occupancy[occupancy] = calculate_room_cost_for_occupancy(
                high_occupancy_room_cost, occupancy, num_paying, num_chaperones
            )

    return costs_by_occupancy

def calculate_room_cost_for_occupancy(room_cost, occupancy, num_paying, num_chaperones):
    """Helper function to calculate room cost for a specific occupancy"""
    # Calculate chaperone rooms needed (2 per room)
    chaperone_rooms = calculate_chaperone_hotel_rooms(num_chaperones)
    chaperone_room_cost = chaperone_rooms * room_cost

    # Calculate rooms needed for paying participants
    paying_rooms = np.ceil(num_paying / occupancy)
    paying_room_cost = paying_rooms * room_cost

    # Total room costs distributed among paying participants
    total_room_costs = paying_room_cost + chaperone_room_cost
    cost_per_paying = total_room_costs / num_paying if num_paying > 0 else 0

    # Round to 2 decimal places
    return round(cost_per_paying, 2)

def calculate_chaperone_count(num_paying, ratio=None, fixed_count=None):
    """Calculate number of free chaperones based on ratio or fixed count"""
    if fixed_count is not None:
        return fixed_count
    elif ratio is not None and ratio > 0:
        return int(np.floor(num_paying / ratio))
    return 0

def calculate_total_per_person(transportation_costs, guide_cost, entry_costs, meal_costs,
                           room_cost, num_paying, driver_tip_per_day=0,
                           num_days=1):
    """Calculate total cost per person"""
    # Calculate driver tips per paying person
    total_driver_tip = driver_tip_per_day * num_days
    driver_tip_per_person = total_driver_tip / num_paying if num_paying > 0 else 0

    total = (transportation_costs +  # Transportation costs (already includes chaperone distribution)
             guide_cost/num_paying + # Guide costs divided by paying participants
             entry_costs +          # Entry costs (already includes chaperone distribution)
             meal_costs +           # Meal costs (already includes chaperone distribution)
             room_cost +           # Room costs (includes chaperone rooms distributed)
             driver_tip_per_person) # Driver tips per paying person

    return total

def calculate_final_price(total_cost_per_person, profit_amount):
    """Calculate final price with fixed profit amount"""
    participant_ranges = {
        "10-13 paying": 1.15,
        "14-16 paying": 1.10,
        "17-20 paying": 1.05,
        "21+ paying": 1.00
    }

    base_price = total_cost_per_person + profit_amount
    return {range_name: base_price * multiplier for range_name, multiplier in participant_ranges.items()}