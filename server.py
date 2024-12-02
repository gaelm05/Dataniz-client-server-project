import socket
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from datetime import datetime, timezone, timedelta

# Conversion functions
def convert_to_rh(moisture):
    return moisture * 0.5  # Example conversion factor

def convert_to_pst(utc_time):
    pst = timezone(timedelta(hours=-8))
    return utc_time.astimezone(pst)

def convert_to_gallons(liters):
    return liters * 0.264172

def start_server():
    #mongdb connection
    uri = "mongodb+srv://testuser:vmDbYFhZwy65Fgg0@cluster0.py74l.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
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
        while True:
            # Receive the message from the client
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                break
            print(f"Received message: {client_message}")
            # Convert the message to uppercase our response we will send
            message = client_message.upper()
            # Send the response back to the client
            client_socket.sendall(message.encode())
        client_socket.close()

if __name__ == "__main__":
    start_server()
