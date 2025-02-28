import numpy as np

def calculate_fixed_costs(bus_cost, metro_cost, airline_cost, train_cost, num_paying, num_chaperones):
    """Calculate total fixed transportation costs including chaperones"""
    total_fixed_costs = sum(filter(None, [bus_cost, metro_cost, airline_cost, train_cost]))
    # Calculate cost per person including chaperones
    cost_per_person = total_fixed_costs / (num_paying + num_chaperones) if num_paying + num_chaperones > 0 else 0
    # Distribute chaperone costs among paying participants
    total_per_paying = cost_per_person + (cost_per_person * num_chaperones / num_paying) if num_paying > 0 else 0
    return total_per_paying

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
    if not hotel['cost_per_room']:
        return {}

    base_cost = hotel['cost_per_room']
    tax_amount = base_cost * (hotel['tax_rate'] / 100) if hotel['tax_rate'] else 0
    total_room_cost = base_cost + tax_amount

    # Calculate chaperone rooms cost
    chaperone_rooms = calculate_chaperone_hotel_rooms(num_chaperones)
    chaperone_room_cost = chaperone_rooms * total_room_cost

    costs_by_occupancy = {}
    for occupancy in sorted(hotel['occupancy_options'], reverse=True):
        if occupancy > 0:
            # Calculate rooms needed for paying participants
            paying_rooms = np.ceil(num_paying / occupancy)
            total_room_costs = (paying_rooms * total_room_cost) + chaperone_room_cost
            cost_per_paying = total_room_costs / num_paying if num_paying > 0 else 0
            costs_by_occupancy[occupancy] = cost_per_paying

    return costs_by_occupancy

def calculate_chaperone_count(num_paying, ratio=None, fixed_count=None):
    """Calculate number of free chaperones based on ratio or fixed count"""
    if fixed_count is not None:
        return fixed_count
    elif ratio is not None and ratio > 0:
        return int(np.floor(num_paying / ratio))
    return 0

def calculate_total_per_person(fixed_costs, guide_cost, entry_costs, meal_costs,
                             room_cost, num_paying, driver_tip_per_day=0,
                             num_days=1):
    """Calculate total cost per person"""
    # Calculate driver tips per paying person
    total_driver_tip = driver_tip_per_day * num_days
    driver_tip_per_person = total_driver_tip / num_paying if num_paying > 0 else 0

    total = (fixed_costs + guide_cost/num_paying + entry_costs +
             meal_costs + room_cost + driver_tip_per_person)

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