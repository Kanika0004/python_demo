from pyscript import Element

terminal = Element("terminal")
input_box = Element("inputBox")
send_btn = Element("sendBtn")
run_btn = Element("runBtn")

# --- Utility functions for web I/O ---
user_input = ""
waiting_for_input = False

def write(text=""):
    terminal.write(text + "\n")

def ask(prompt):
    global waiting_for_input
    write(prompt)
    waiting_for_input = True
    input_box.element.disabled = False
    send_btn.element.disabled = False
    return wait_for_input()

def wait_for_input():
    from js import Promise
    def executor(resolve, reject):
        def on_click(event):
            global user_input, waiting_for_input
            user_input = input_box.element.value
            input_box.element.value = ""
            waiting_for_input = False
            input_box.element.disabled = True
            send_btn.element.disabled = True
            send_btn.element.removeEventListener("click", on_click)
            resolve(user_input)
        send_btn.element.addEventListener("click", on_click)
    return Promise.new(executor)

# --- Coffee Machine Code ---
logo = r'''
            __  __                                  _     _            
  ___ ___  / _|/ _| ___  ___   _ __ ___   __ _  ___| |__ (_)_ __   ___ 
 / __/ _ \| |_| |_ / _ \/ _ \ | '_ ` _ \ / _` |/ __| '_ \| | '_ \ / _ \
| (_| (_) |  _|  _|  __/  __/ | | | | | | (_| | (__| | | | | | | |  __/
 \___\___/|_| |_|  \___|\___| |_| |_| |_|\__,_|\___|_| |_|_|_| |_|\___|
'''

MENU = {
  "espresso": {"ingredients": {"water": 50, "coffee": 18}, "cost": 1.5},
  "latte": {"ingredients": {"water": 200, "milk": 150, "coffee": 24}, "cost": 2.5},
  "cappuccino": {"ingredients": {"water": 250, "milk": 100, "coffee": 24}, "cost": 3.0}
}

resources = {"water": 300, "milk": 200, "coffee": 100}

def check_resources(drink_name):
    order_ingredients = MENU[drink_name]["ingredients"]
    for item, amt_req in order_ingredients.items():
        if resources.get(item, 0) < amt_req:
            write(f"Sorry there is not enough {item}.")
            return False
    return True

async def process_coins():
    total = 0
    total += int(await ask("how many quarters? :")) * 0.25
    total += int(await ask("how many dimes? :")) * 0.10
    total += int(await ask("how many nickles? :")) * 0.05
    total += int(await ask("how many pennies? :")) * 0.01
    return total

def make_coffee(drink_name):
    order_ingredients = MENU[drink_name]["ingredients"]
    for item, amt_req in order_ingredients.items():
        resources[item] -= amt_req
    write(f"Here is your {drink_name} ☕. Enjoy!")

async def coffee_machine():
    is_on = True
    money_gained = 0
    while is_on:
        write(logo)
        user_ip = (await ask("What would you like? (espresso/latte/cappuccino) 😊 : ")).lower()
        if user_ip == "off":
            write("Coffee Machine turning off...")
            is_on = False
        elif user_ip == "report":
            write("Current resource values 📃:")
            for key in resources:
                write(f"{key}: {resources[key]}")
            write(f"Money: ${money_gained}")
        elif user_ip in ["espresso", "latte", "cappuccino"]:
            if not check_resources(user_ip):
                continue
            inserted_coins = await process_coins()
            if inserted_coins < MENU[user_ip]["cost"]:
                write("Sorry that's not enough money. Money refunded.")
            else:
                money_gained += MENU[user_ip]["cost"]
                change = round(inserted_coins - MENU[user_ip]["cost"], 2)
                write(f"Here is ${change} in change.")
                make_coffee(user_ip)
        else:
            write("Enter a valid input!")

# --- Run when button clicked ---
def start(event):
    run_btn.element.disabled = True
    coffee_machine()

run_btn.element.addEventListener("click", start)
