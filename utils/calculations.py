import numpy as np

def calculate_fixed_costs(bus_cost, metro_cost, airline_cost, train_cost):
    """Calculate total fixed transportation costs"""
    return sum(filter(None, [bus_cost, metro_cost, airline_cost, train_cost]))

def calculate_guide_cost(daily_rate, num_days, guide_tip_per_day=0):
    """Calculate total guide cost including tips"""
    base_cost = daily_rate * num_days if daily_rate and num_days else 0
    tip_cost = guide_tip_per_day * num_days if guide_tip_per_day and num_days else 0
    return base_cost + tip_cost

def calculate_entry_costs(entry_costs):
    """Calculate total entry costs per person"""
    return sum(cost for cost in entry_costs if cost)

def calculate_meal_costs(lunch_costs, dinner_costs):
    """Calculate total meal costs per person"""
    return sum(lunch_costs + dinner_costs)

def calculate_room_costs(hotels, num_people):
    """Calculate room costs per person based on hotel options"""
    if not hotels or not num_people:
        return 0

    min_cost_per_person = float('inf')
    selected_hotel = None
    selected_occupancy = None

    for hotel in hotels:
        if not hotel['cost_per_room']:
            continue

        base_cost = hotel['cost_per_room']
        tax_amount = base_cost * (hotel['tax_rate'] / 100) if hotel['tax_rate'] else 0
        total_room_cost = base_cost + tax_amount

        for occupancy in hotel['occupancy_options']:
            if occupancy > 0:
                num_rooms = np.ceil(num_people / occupancy)
                cost_per_person = (total_room_cost * num_rooms) / num_people

                if cost_per_person < min_cost_per_person:
                    min_cost_per_person = cost_per_person
                    selected_hotel = hotel['name']
                    selected_occupancy = occupancy

    return min_cost_per_person if min_cost_per_person != float('inf') else 0

def calculate_chaperone_count(num_paying, ratio=None, fixed_count=None):
    """Calculate number of free chaperones based on ratio or fixed count"""
    if fixed_count is not None:
        return fixed_count
    elif ratio is not None and ratio > 0:
        return int(np.floor(num_paying / ratio))
    return 0

def calculate_total_per_person(fixed_costs, guide_cost, entry_costs, meal_costs,
                             hotels, num_paying, num_chaperones, driver_tip_per_day=0,
                             num_days=1):
    """Calculate total cost per person"""
    total_participants = num_paying + num_chaperones

    # Distribute fixed costs among paying participants
    fixed_per_person = fixed_costs / num_paying if num_paying > 0 else 0
    guide_per_person = guide_cost / num_paying if num_paying > 0 else 0

    # Calculate driver tips
    total_driver_tip = driver_tip_per_day * num_days
    driver_tip_per_person = total_driver_tip / num_paying if num_paying > 0 else 0

    # Calculate room costs
    room_per_person = calculate_room_costs(hotels, total_participants)

    total = (fixed_per_person + guide_per_person + entry_costs +
             meal_costs + room_per_person + driver_tip_per_person)

    return total

def calculate_final_price(total_cost_per_person, profit_amount):
    """Calculate final price with fixed profit amount"""
    base_price = total_cost_per_person + profit_amount

    tiers = {
        "10-13 people": base_price * 1.15,
        "14-16 people": base_price * 1.10,
        "17-20 people": base_price * 1.05,
        "21+ people": base_price
    }
    return tiers