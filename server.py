import socket
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from datetime import datetime, timezone, timedelta

#binary search tree node
class BSTNode:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

#binary search tree setuo
class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key, data):
        if not self.root:
            self.root = BSTNode(key, data)
        else:
            self._insert(self.root, key, data)

    def _insert(self, node, key, data):
        if key < node.key:
            if node.left:
                self._insert(node.left, key, data)
            else:
                node.left = BSTNode(key, data)
        elif key > node.key:
            if node.right:
                self._insert(node.right, key, data)
            else:
                node.right = BSTNode(key, data)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if not node or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

# Conversion functions
def convert_to_rh(moisture):
    return moisture * 0.5  # Example conversion factor

def convert_to_pst(utc_time):
    pst = timezone(timedelta(hours=-8))
    return utc_time.astimezone(pst)

def convert_to_gallons(liters):
    return liters * 0.264172

COMMAND_MAPPING = {
    "average moisture": {"device": "refrigerator", "metric": "Moisture Meter - Moisture Meter", "timeframe": 3},
    "average water used": {"device": "dishwasher", "metric": "Water Consumption", "timeframe": None},
    "most electricity used": {"metric": "ammeter-fridge", "action": "max_consumption"}
}
def handle_query(command, bst, collection):
    if command not in COMMAND_MAPPING:
        return {"error": f"Unrecognized command: '{command}'."}

    query = COMMAND_MAPPING[command]
    device = query.get("device")
    metric = query.get("metric")
    timeframe = query.get("timeframe")
    action = query.get("action")

    if action == "max_consumption":
        # Handle electricity consumption comparison
        max_consumption = 0
        max_device = None
        for device_data in collection.find():
            total = float(device_data.get("payload", {}).get("ammeter-fridge", 0))
            if total > max_consumption:
                max_consumption = total
                max_device = device_data.get("payload", {}).get("board_name")
        return {"max_consumption_device": max_device, "consumption": max_consumption}

    # Search BST for the device
    if device:
        node = bst.search(device)
        if not node:
            return {"error": f"Device '{device}' not found."}

        readings = node.data.get("payload", {}).get("readings", [])
        total_value, count = 0, 0
        for reading in readings:
            record_time = datetime.fromtimestamp(int(reading.get("timestamp", 0)))
            if timeframe and datetime.now(timezone.utc) - record_time > timedelta(hours=timeframe):
                continue
            total_value += float(reading.get(metric, 0))
            count += 1

        if count == 0:
            return {"error": f"No data found for metric '{metric}' in the specified timeframe."}

        if metric == "Moisture Meter - Moisture Meter":
            total_value = convert_to_rh(total_value / count)
        elif metric == "Water Consumption":
            total_value = convert_to_gallons(total_value / count)

        return {"device": device, "metric": metric, "average_value": total_value}

def start_server():
    #mongdb connection
    uri = "mongodb+srv://testuser:vmDbYFhZwy65Fgg0@cluster0.py74l.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    db = client['test']
    collection = db['DB1_virtual']
    metadata_collection = db['DB1_metadata']

    # Binary search tree to manage IoT data
    bst = BinarySearchTree()

    # Fetch and populate BST with IoT data
    for item in collection.find():
        key = item.get('device_id', 'unknown')
        bst.insert(key, item)
    #tests the connection to the database
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    #server set up

    # Get server IP and port
    server_ip = input("Enter the server IP address: ")
    #which port number our server will use
    server_port = int(input("Enter the port number to start the server: "))
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server listening on port {server_port}...")

    while True:
        # Accept a connection from an IP address and socket
        client_socket, client_address = server_socket.accept()
        print(f"Established connection to {server_ip} and port: {server_port}")
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                query = json.loads(data)
                device_id = query.get("device_id")
                bst_node = bst.search(device_id)
                if bst_node:
                    device_data = bst_node.data

                    # Fetch metadata from the metadata collection
                    metadata = metadata_collection.find_one({"device_id": device_id})
                    if not metadata:
                        client_socket.sendall(json.dumps({"error": "Metadata not found"}).encode())
                        continue
                    # Process and convert data
                    result = {
                        "device_id": device_id,
                        "readings": [],
                        "metadata": metadata,  # Include metadata in response
                    }
                    for reading in device_data.get("readings", []):
                        rh = convert_to_rh(reading["moisture"])
                        pst_time = convert_to_pst(datetime.fromisoformat(reading["timestamp"]))
                        gallons = convert_to_gallons(reading["liters"])
                        result["readings"].append({
                            "timestamp": pst_time.isoformat(),
                            "rh": rh,
                            "gallons": gallons
                        })
                    client_socket.sendall(json.dumps(result).encode())
                else:
                    client_socket.sendall(json.dumps({"error": "Device not found"}).encode())
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()



def parse_query(query):
    #parsing the queries to help find device that it is asking for
    keywords = query.lower().split()
    device = None
    metric = None
    timeframe = None

    # Identify the device
    if "fridge" in keywords or "refrigerator" in keywords:
        device = "refrigerator"
    elif "dishwasher" in keywords:
        device = "dishwasher"

    # Identify the metric
    if "moisture" in keywords:
        metric = "Moisture Meter - Moisture Meter"
    elif "water" in keywords:
        metric = "Water Consumption"
    elif "electricity" in keywords or "power" in keywords:
        metric = "ammeter-fridge"

    # Identify the timeframe
    if "past" in keywords and "hours" in keywords:
        try:
            idx = keywords.index("hours")
            timeframe = int(keywords[idx - 1])
        except (ValueError, IndexError):
            timeframe = None  # Invalid or unspecified timeframe

    return device, metric, timeframe

if __name__ == "__main__":
    start_server()
