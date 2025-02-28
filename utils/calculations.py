import numpy as np

def calculate_fixed_costs(bus_cost, metro_cost, airline_cost, train_cost):
    """Calculate total fixed transportation costs"""
    return sum(filter(None, [bus_cost, metro_cost, airline_cost, train_cost]))

def calculate_guide_cost(daily_rate, num_days):
    """Calculate total guide cost"""
    return daily_rate * num_days if daily_rate and num_days else 0

def calculate_entry_costs(entry_costs):
    """Calculate total entry costs per person"""
    return sum(cost for cost in entry_costs if cost)

def calculate_meal_costs(lunch_costs, dinner_costs):
    """Calculate total meal costs per person"""
    return sum(lunch_costs + dinner_costs)

def calculate_room_costs(room_cost, num_people, occupancy):
    """Calculate room costs per person based on occupancy"""
    if not room_cost or not num_people or not occupancy:
        return 0
    num_rooms = np.ceil(num_people / occupancy)
    total_room_cost = num_rooms * room_cost
    return total_room_cost / num_people

def calculate_price_tiers(total_cost_per_person, margin):
    """Calculate final price with margin for different group sizes"""
    base_price = total_cost_per_person * (1 + margin/100)
    
    tiers = {
        "10-13 people": base_price * 1.15,
        "14-16 people": base_price * 1.10,
        "17-20 people": base_price * 1.05,
        "21+ people": base_price
    }
    return tiers

def calculate_total_per_person(fixed_costs, guide_cost, entry_costs, meal_costs,
                             room_cost, num_people, occupancy, num_chaperones):
    """Calculate total cost per person"""
    paying_people = max(num_people - num_chaperones, 1)
    
    # Distribute fixed costs among paying participants
    fixed_per_person = fixed_costs / paying_people
    guide_per_person = guide_cost / paying_people
    
    # Calculate per-person costs
    room_per_person = calculate_room_costs(room_cost, num_people, occupancy)
    
    total = (fixed_per_person + guide_per_person + entry_costs +
             meal_costs + room_per_person)
    
    return total
