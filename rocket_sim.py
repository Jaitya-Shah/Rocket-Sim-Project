import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import random
import os

GRAVITY = 9.81
DT = 0.05
SIM_TIME = 10


def load_fuels(filename):
    df = pd.read_csv(filename)
    fuels = {}

    for i in range(len(df)):
        fuel_name = df.loc[i, "fuel_name"]
        fuels[fuel_name] = {
            "efficiency": df.loc[i, "efficiency"],
            "stability": df.loc[i, "stability"],
            "thrust_factor": df.loc[i, "thrust_factor"]
        }

    return fuels


def run_simulation(params, fuel):
    mass = params["mass"]
    length = params["length"]
    wing_span = params["wing_span"]

    thrust = 200 * fuel["efficiency"] * fuel["thrust_factor"]
    stability = fuel["stability"]

    x = 0
    y = 0
    velocity = 0
    angle = 0
    angular_velocity = 0

    xs = []
    ys = []

    time = 0
    frozen = False
    spun_out = False

    while time <= SIM_TIME:
        wobble = (1 - stability) * random.uniform(-1, 1)
        angular_velocity = angular_velocity + wobble * 0.1
        angle = angle + angular_velocity

        if abs(angle) > math.pi / 3:
            spun_out = True
            break

        lift_acc = thrust / mass
        velocity = velocity + (lift_acc - GRAVITY) * DT
        y = y + velocity * DT

        x = x + math.sin(angle) * 0.1

        if y < 0:
            y = 0
            velocity = 0

        xs.append(x)
        ys.append(y)

        if abs(velocity) < 0.01 and time > 2:
            frozen = True
            break

        time = time + DT

    max_height = 0
    for h in ys:
        if h > max_height:
            max_height = h

    if spun_out:
        outcome = "Spun out and crashed"
    elif frozen:
        outcome = "Frozen on launch pad"
    elif max_height < 2:
        outcome = "Barely lifted off"
    else:
        outcome = "Successful lift-off"

    return xs, ys, max_height, outcome


def log_run(filename, data):
    new_data = pd.DataFrame([data])

    if os.path.exists(filename):
        old_data = pd.read_csv(filename)
        combined = pd.concat([old_data, new_data], ignore_index=True)
    else:
        combined = new_data

    combined.to_csv(filename, index=False)


def main():
    fuels = load_fuels("fuels.csv")

    print("Available fuels:")
    for f in fuels:
        print(f)

    rocket_name = input("Enter rocket name: ")
    fuel_name = input("Choose fuel: ")

    if fuel_name not in fuels:
        print("Invalid fuel selected")
        return

    mass = float(input("Enter rocket mass (kg): "))
    length = float(input("Enter rocket length (m): "))
    wing_span = float(input("Enter wing span (m): "))

    params = {
        "mass": mass,
        "length": length,
        "wing_span": wing_span
    }

    xs, ys, max_height, outcome = run_simulation(params, fuels[fuel_name])

    print("Outcome:", outcome)
    print("Maximum height:", round(max_height, 2), "meters")

    log_run("rocket_runs.csv", {
        "rocket_name": rocket_name,
        "fuel": fuel_name,
        "mass": mass,
        "length": length,
        "wing_span": wing_span,
        "max_height": round(max_height, 2),
        "outcome": outcome
    })

    plt.plot(xs, ys)
    plt.xlabel("Horizontal deviation")
    plt.ylabel("Height")
    plt.title("Trajectory of " + rocket_name)
    plt.show()


main()
