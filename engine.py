def slab_cost(units):
    if units <= 100:
        return units * 3
    elif units <= 200:
        return 100 * 3 + (units - 100) * 5
    else:
        return 100 * 3 + 100 * 5 + (units - 200) * 8


def analyze(data):
    if not data:
        return {
            "total_units": 0,
            "predicted_units": 0,
            "estimated_cost": 0,
            "insights": ["No data available"],
            "saving_tip": "",
            "efficiency": {}
        }

    # ---------------- TOTAL CALCULATION ----------------
    total_units = sum(d['units'] for d in data)

    days = len(set(d['date'] for d in data))
    avg_daily = total_units / days if days else 0

    predicted = avg_daily * 30
    cost = slab_cost(predicted)

    insights = []

    # ---------------- APPLIANCE USAGE ----------------
    usage = {}
    for d in data:
        usage[d['appliance']] = usage.get(d['appliance'], 0) + d['units']

    max_app = max(usage, key=usage.get)
    max_units = usage[max_app]

    # ---------------- PEAK DETECTION ----------------
    last_day = data[-1]['date']
    last_day_usage = sum(d['units'] for d in data if d['date'] == last_day)

    if last_day_usage > avg_daily * 1.5:
        insights.append("⚠️ Unusual high usage detected")

    if max_units / total_units > 0.5:
        insights.append(f"{max_app} consumes majority energy")

    # ---------------- SAVINGS CALCULATION (FIXED) ----------------
    total_hours = sum(d['hours'] for d in data if d['appliance'] == max_app)
    total_app_units = usage[max_app]

    units_per_hour = total_app_units / total_hours if total_hours else 0

    saving_units = units_per_hour * 2 * 30
    saving_units = min(saving_units, predicted)

    saving_money = slab_cost(predicted) - slab_cost(predicted - saving_units)
    saving_money = max(0, saving_money)

    saving_tip = f"Reduce {max_app} usage by ~2 hrs/day → Save ₹{round(saving_money, 2)}/month"

    # ---------------- EFFICIENCY CALCULATION ----------------
    efficiency = {}
    hours_map = {}
    for app in usage:
        total_units_app = usage[app]
        total_hours_app = sum(d['hours'] for d in data if d['appliance'] == app)

        hours_map[app] = round(total_hours_app, 2)
        
        if total_hours_app > 0:
            efficiency_score = total_units_app / total_hours_app
        else:
            efficiency_score = 0

        efficiency[app] = round(efficiency_score, 3)

    # Identify best and worst appliances
    if efficiency:
        worst_app = max(efficiency, key=efficiency.get)
        best_app = min(efficiency, key=efficiency.get)

        insights.append(f"⚡ Least efficient appliance: {worst_app}")
        insights.append(f"✅ Most efficient appliance: {best_app}")

    # ---------------- FINAL OUTPUT ----------------
    return {
        "total_units": round(total_units, 2),
        "predicted_units": round(predicted, 2),
        "estimated_cost": round(cost, 2),
        "insights": insights,
        "saving_tip": saving_tip,
        "efficiency": efficiency
    }