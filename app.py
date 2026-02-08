from flask import Flask, render_template, request

app = Flask(__name__)


def co2_per_km(fuel):
    mapping = {"Petrol": 180, "Diesel": 150, "Hybrid": 90, "Electric": 0}
    return mapping.get(fuel, 160)

def estimate_daily_co2(fuel, hours, avg_speed=40):
    km_driven = hours * avg_speed
    return round(co2_per_km(fuel) * km_driven, 1)

def calculate_score(co2):
    if co2 == 0:
        return 95
    score = 100 - (co2 / 50)
    return max(10, min(95, int(score)))

def color_index(score):
    if score <= 49:
        return "red", "High CO₂ impact"
    elif score <= 65:
        return "yellow", "Moderate CO₂ impact"
    else:
        return "green", "Low CO₂ impact"


def calculate_personal_carbon(transport, diet, household_size, trashbags):
    transport = transport.lower().strip()
    diet = diet.lower().strip()
    
    # Transport emissions
    if transport in ["car", "drive"]:
        transport_emission = 88.5
    elif transport == "bus":
        transport_emission = 25.2
    elif transport == "train":
        transport_emission = 12.6
    elif transport in ["bike", "walk", "cycle"]:
        transport_emission = 0.0
    else:
        return None, None, "Invalid transport mode. Use car, bus, train, or bike."
    
    # Diet emissions
    if diet == "veg":
        diet_emission = 7.2
    elif diet in ["non-veg", "non veg"]:
        diet_emission = 26.6
    else:
        return None, None, "Invalid diet. Use Veg or Non-Veg."
    
    # Waste emissions
    waste_emission = trashbags * 0.18
    
    # Multiply by household size
    transport_emission *= household_size
    diet_emission *= household_size
    waste_emission *= household_size
    
    total_emission = transport_emission + diet_emission + waste_emission
    
    # Insight
    if transport_emission >= diet_emission and transport_emission >= waste_emission:
        insight = f"Transport ({transport.title()}) contributes the most."
    elif diet_emission >= transport_emission and diet_emission >= waste_emission:
        insight = "Diet contributes the most."
    else:
        insight = "Waste contributes the most."
    
    details = (
        f"Transport: {transport_emission:.2f} kg CO₂e, "
        f"Diet: {diet_emission:.2f} kg CO₂e, "
        f"Waste: {waste_emission:.2f} kg CO₂e"
    )
    
    return round(total_emission, 2), details, insight

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/driving", methods=["GET", "POST"])
def driving():
    result = None
    if request.method == "POST":
        brand = request.form["brand"].strip()
        fuel = request.form["fuel"]
        hours = float(request.form["hours"])
        co2 = estimate_daily_co2(fuel, hours)
        score = calculate_score(co2)
        color, explanation = color_index(score)
        result = {"brand": brand, "fuel": fuel, "hours": hours, "co2": co2, 
                  "score": score, "color": color, "explanation": explanation}
    return render_template("driving.html", result=result)

@app.route("/personal", methods=["GET", "POST"])
def personal():
    result = None
    error = None
    if request.method == "POST":
        try:
            transport = request.form["transport"]
            diet = request.form["diet"]
            household_size = float(request.form["household"])
            trashbags = float(request.form["trashbags"])
            
            total, details, insight_or_error = calculate_personal_carbon(transport, diet, household_size, trashbags)
            if total is None:
                error = insight_or_error
            else:
                result = {"total": total, "details": details, "insight": insight_or_error}
        except ValueError:
            error = "Please enter valid numeric values."
    return render_template("personal.html", result=result, error=error)

@app.route("/game")
def game():
    return render_template("game.html")

if __name__ == "__main__":
    app.run(debug=True)
