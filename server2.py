import socket
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta

#get average moisture query
def get_average_moisture(db, collection_name, hours=3):
    """Calculate the average moisture for a given board name in the past given hours."""
    collection = db[collection_name]
    three_hours_ago = datetime.utcnow() - timedelta(hours=hours)

    pipeline = [
        {
            # Match the specific asset IDs
            "$match": {
                "payload.parent_asset_uid": "7y3-30g-1m0-ye0",
                "payload.asset_uid": "c3e-k57-ruu-1e6",
                "Moisture Meter - Moisture Meter": "16.6103"

            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["averageMoisture"] if result else None

def start_server():
    #mongdb connection
    uri = "mongodb+srv://testuser:vmDbYFhZwy65Fgg0@cluster0.py74l.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['test']
    collection = db["DB1_virtual"]
    # Send a ping to confirm a successful connection

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

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
                # Receive the message from the client
                client_message = client_socket.recv(1024).decode()
                if not client_message:
                    break
                print(f"Received message: {client_message}")
                #client option 2
                if client_message == "1" or client_message == "average moisture":
                    # Execute the average moisture query
                    board_name = "Arduino Pro Mini -  refrigerator"  # Example device name
                    hours = 3  # Last 3 hours
                    try:
                        average_moisture = get_average_moisture(db, "DB1_virtual", hours)
                        document = collection.find_one({"payload.parent_asset_uid": "7y3-30g-1m0-ye0"})
                        print(document)
                        print("this is reaching the try statement")
                        response = {"average_moisture": document}
                    except Exception as e:
                        response = {"error": str(e)}
                    client_socket.sendall(json.dumps(response).encode())
                #client option 2
                if client_message == "2" or client_message == "average water used":
                    # Execute the average moisture query
                    board_name = "Arduino Pro Mini -  refrigerator"  # Example device name
                    try:
                        average_moisture = get_average_moisture(db, "DB1_virtual", hours)
                        document = collection.find_one({"payload.parent_asset_uid": "7y3-30g-1m0-ye0"})
                        print(document)
                        print("this is reaching the try statement")
                        response = {"average_moisture": average_moisture}
                    except Exception as e:
                        response = {"error": str(e)}

                    client_socket.sendall(json.dumps(response).encode())
                #client option 3
                if  client_message == "3" or client_message == "most electricty used":
                    # Execute the average moisture query
                    board_name = "Arduino Pro Mini -  refrigerator"  # Example device name
                    try:
                        average_moisture = get_average_moisture(db, "DB1_virtual", hours)
                        document = collection.find_one({"payload.parent_asset_uid": "7y3-30g-1m0-ye0"})
                        print(document)
                        print("this is reaching the try statement")
                        response = {"average_moisture": average_moisture}
                    except Exception as e:
                        response = {"error": str(e)}

                    client_socket.sendall(json.dumps(response).encode())
                else:
                    # Default behavior for other messages
                    message = f"Unrecognized command: {client_message}"
                    client_socket.sendall(message.encode())

        except Exception as e:
                print(f"Error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()