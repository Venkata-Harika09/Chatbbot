import openai
import tkinter as tk
from tkinter import scrolledtext, messagebox
from geopy.geocoders import Nominatim
import folium
import webbrowser
import os
import openrouteservice  # Import OpenRouteService client

# Set up your OpenAI API key
openai.api_key = "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"

# Set up OpenRouteService client (use your API key)
ORS_API_KEY = "5b3ce3597851110001cf6248868fc98598ee47c7bf5b35b994abbb83"
ors_client = openrouteservice.Client(key=ORS_API_KEY)

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to generate route map and save as HTML file
def create_route_map(start, end):
    try:
        # Get coordinates for start and destination locations
        start_location = geolocator.geocode(start)
        end_location = geolocator.geocode(end)

        if not start_location or not end_location:
            return "Invalid location(s) specified."

        # Extract coordinates
        start_coords = (start_location.latitude, start_location.longitude)
        end_coords = (end_location.latitude, end_location.longitude)

        # Fetch route data from OpenRouteService
        route = ors_client.directions(
            coordinates=[start_coords[::-1], end_coords[::-1]],  # Reverse (lat, lon) to (lon, lat)
            profile='driving-car',
            format='geojson'
        )

        # Extract route geometry (list of coordinates)
        route_coords = route['features'][0]['geometry']['coordinates']

        # Create map centered at the start location
        route_map = folium.Map(location=start_coords, zoom_start=10)

        # Plot route on the map
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in route_coords],  # Reverse again for folium
            color='blue', weight=5, opacity=0.7
        ).add_to(route_map)

        # Add markers for start and destination
        folium.Marker(start_coords, popup=f"Start: {start}").add_to(route_map)
        folium.Marker(end_coords, popup=f"End: {end}").add_to(route_map)

        # Save map to HTML and open in the browser
        map_file = "route_map.html"
        route_map.save(map_file)
        webbrowser.open('file://' + os.path.realpath(map_file))

        return f"Route generated from {start} to {end}!"
    except Exception as e:
        return f"Error fetching route: {e}"

# Function to send user input to OpenAI API or generate route
def get_response(user_input):
    if "route" in user_input.lower():
        try:
            parts = user_input.lower().split("to")
            start = parts[0].split("from")[1].strip()
            end = parts[1].strip()
            return create_route_map(start, end)
        except IndexError:
            return "Please use 'route from <start> to <end>' format."
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error: {e}"

# Function to send a message
def send_message():
    user_input = input_field.get()
    if user_input.strip():
        chat_area.insert(tk.END, f"You: {user_input}\n", "user")
        input_field.delete(0, tk.END)

        response = get_response(user_input)
        chat_area.insert(tk.END, f"Bot: {response}\n\n", "bot")
        chat_area.yview(tk.END)

# Function to open chat window
def open_chat():
    login_window.destroy()

    global chat_area, input_field
    chat_window = tk.Tk()
    chat_window.title("Travel Chatbot")
    chat_window.geometry("500x500")

    chat_area = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD, state='normal', height=20, width=60)
    chat_area.pack(padx=10, pady=10)
    chat_area.insert(tk.END, "Bot: Hello! Ask me for a route using 'route from <start> to <end>'.\n\n")

    input_field = tk.Entry(chat_window, width=60)
    input_field.pack(padx=10, pady=5)

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack(pady=5)

    chat_window.mainloop()

# Login functionality
def check_login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "user" and password == "password":
        open_chat()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Login window setup
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("1500x1500")
login_window.configure(bg="skyblue")

tk.Label(login_window, text="Username:", bg="skyblue", fg="white").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:", bg="skyblue", fg="white").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=check_login, bg="skyblue", fg="black")
login_button.pack(pady=10)

login_window.mainloop()