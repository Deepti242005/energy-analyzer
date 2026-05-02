def slab_cost(units):
    if units <= 100:
        return units * 3
    elif units <= 200:
        return 100*3 + (units-100)*5
    else:
        return 100*3 + 100*5 + (units-200)*8


def analyze(data):
    if not data:
        return {
            "total_units": 0,
            "predicted_units": 0,
            "estimated_cost": 0,
            "insights": [],
            "saving_tip": "",
            "efficiency": {}
        }

    total_units = sum(d['units'] for d in data)
    days = len(set(d['date'] for d in data))
    avg_daily = total_units / days if days else 0

    predicted = avg_daily * 30
    cost = slab_cost(predicted)

    usage = {}
    hours_map = {}

    for d in data:
        usage[d['appliance']] = usage.get(d['appliance'], 0) + d['units']
        hours_map[d['appliance']] = hours_map.get(d['appliance'], 0) + d['hours']

    efficiency = {}
    for app in usage:
        if hours_map[app] > 0:
            efficiency[app] = round(usage[app]/hours_map[app], 2)

    max_app = max(usage, key=usage.get)

    insights = []
    if usage[max_app]/total_units > 0.5:
        insights.append(f"{max_app} consumes most energy")

    avg_units_day = usage[max_app]/days if days else 0
    saving_units = avg_units_day * 0.2 * 30
    saving_money = slab_cost(predicted) - slab_cost(max(predicted-saving_units,0))

    return {
        "total_units": round(total_units,2),
        "predicted_units": round(predicted,2),
        "estimated_cost": round(cost,2),
        "insights": insights,
        "saving_tip": f"Reduce {max_app} usage → Save ₹{round(saving_money,2)}",
        "efficiency": efficiency
    }