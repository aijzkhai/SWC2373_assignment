from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)
WEBEX_API_URL = "https://webexapis.com/v1"

# Route to serve the homepage (index.html)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        return redirect(url_for('menu', token=access_token))
    return render_template('index.html')

# Route for menu options
@app.route('/menu/<token>', methods=['GET'])
def menu(token):
    return render_template('menu.html', token=token)

# Option 0: Test Connection
@app.route('/test_connection/<token>', methods=['GET'])
def test_connection(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)
    if response.status_code == 200:
        return render_template('menu.html', token=token, message="Connection successful!", connection_status=True)
    else:
        return render_template('menu.html', token=token, message="Failed to connect to the Webex server.", connection_status=False)

# Option 1: Display User Info
@app.route('/display_user_info/<token>', methods=['GET'])
def display_user_info(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return render_template('user_info.html', user_info=user_info, access_token=token)
    else:
        return render_template('menu.html', token=token, message="Failed to retrieve user information.")

# Option 2: List Rooms
@app.route('/list_rooms/<token>', methods=['GET'])
def list_rooms(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    rooms_response = requests.get(f"{WEBEX_API_URL}/rooms", headers=headers)
    if rooms_response.status_code == 200:
        rooms = rooms_response.json().get('items', [])[:7]  # Limit to 5 rooms
        rooms_info = []
        for room in rooms:
            rooms_info.append({
                "id": room['id'],
                "title": room['title'],
                "created": datetime.fromisoformat(room['created'][:-1]),  # Remove 'Z' for datetime
                "last_activity": datetime.fromisoformat(room['lastActivity'][:-1])  # Remove 'Z' for datetime
            })
        return render_template('rooms.html', rooms=rooms_info, access_token=token)
    else:
        return render_template('menu.html', token=token, message="Failed to retrieve rooms.")

# Option 3: Create Room
@app.route('/create_room/<token>', methods=['GET', 'POST'])
def create_room(token):
    if request.method == 'POST':
        title = request.form['title']
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"{WEBEX_API_URL}/rooms", headers=headers, json={"title": title})
        if response.status_code == 200:
            return render_template('create_room.html', access_token=token, message="Room created successfully!", status=True)
        else:
            return render_template('create_room.html', access_token=token, message="Failed to create the room.", status=False)
    return render_template('create_room.html', access_token=token)

# Option 4: Send Messages
@app.route('/send_message/<token>', methods=['GET', 'POST'])
def send_message(token):
    if request.method == 'POST':
        access_token = request.form['access_token']
        room_id = request.form['room_id']
        message_content = request.form['message']
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        message_data = {
            "roomId": room_id,
            "text": message_content
        }
        
        # Send the message to the specified room
        response = requests.post(f'{WEBEX_API_URL}/messages', headers=headers, json=message_data)
        
        if response.status_code == 200:
            message = f"Message sent to room {room_id} successfully!"
        else:
            message = "Failed to send the message. Please try again."
        
        return render_template('send_message.html', message=message, access_token=token)
    
    return render_template('send_message.html', access_token=token)

    
if __name__ == "__main__":
    app.run(debug=True)
