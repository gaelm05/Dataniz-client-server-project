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

    pipeline =[
        {
            '$match': {
                'payload.parent_asset_uid': '7y3-30g-1m0-ye0',
                'payload.asset_uid': 'c3e-k57-ruu-1e6',
                "payload.time": {
            "$gte": {"$dateSubtract": {"startDate": "$$NOW", "unit": "hour", "amount": 3}}}
                #"payload.time": {"$gte": three_hours_ago}
            },
        },
    {
        '$project': {
            'moisture': {
                '$convert': {
                    'input': '$payload.Moisture Meter - Moisture Meter',
                    'to': 'double',
                    'onError': None,
                    'onNull': None
                }
            }
        }
    }, {
        '$match': {
            'moisture': {
                '$ne': None
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'averageMoisture': {
                '$avg': '$moisture'
            }
        }
    }
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["averageMoisture"] if result else None

def get_average_water(db, collection_name):
    collection = db[collection_name]
    pipeline = [
        {
            "$match": {
                "payload.parent_asset_uid": "2330ce09-40cb-4f53-a87a-f2456a92d519",
                "payload.asset_uid": "0077360b-bf76-4161-998f-4eda10ec5ddf"
            }
        },
        {
            "$project": {
                "waterConsumption": {
                    "$convert": {
                        "input": "$payload.Dishwasher",
                        "to": "double",
                        "onError": None,
                        "onNull": None
                    }
                }
            }
        },
        {
            "$match": {
                "waterConsumption": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": None,
                "averageWaterConsumptionPerCycle": {"$avg": "$waterConsumption"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["averageWaterConsumptionPerCycle"] if result else None

def usage_electricty(db, collection_name):
    collection = db[collection_name]
    pipeline= [
            {
                '$match': {
                    '$or': [
                        {
                            'payload.asset_uid': 'c3e-k57-ruu-1e6'
                        }, {
                            'payload.asset_uid': '5ccff480-b86b-43c0-9d14-e766ccb20b1c'
                        }, {
                            'payload.asset_uid': '0077360b-bf76-4161-998f-4eda10ec5ddf'
                        }
                    ]
                }
            }, {
            '$project': {
                'device': {
                    '$switch': {
                        'branches': [
                            {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', 'c3e-k57-ruu-1e6'
                                    ]
                                },
                                'then': 'Refrigerator 1'
                            }, {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', '5ccff480-b86b-43c0-9d14-e766ccb20b1c'
                                    ]
                                },
                                'then': 'Refrigerator 2'
                            }, {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', '0077360b-bf76-4161-998f-4eda10ec5ddf'
                                    ]
                                },
                                'then': 'Dishwasher'
                            }
                        ],
                        'default': 'Unknown Device'
                    }
                },
                'ElectricityUsed': {
                    '$switch': {
                        'branches': [
                            {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', 'c3e-k57-ruu-1e6'
                                    ]
                                },
                                'then': {
                                    '$convert': {
                                        'input': '$payload.ammeter-fridge',
                                        'to': 'double',
                                        'onError': None,
                                        'onNull': None
                                    }
                                }
                            }, {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', '5ccff480-b86b-43c0-9d14-e766ccb20b1c'
                                    ]
                                },
                                'then': {
                                    '$convert': {
                                        'input': '$payload.ammeter-fridge2',
                                        'to': 'double',
                                        'onError': None,
                                        'onNull': None
                                    }
                                }
                            }, {
                                'case': {
                                    '$eq': [
                                        '$payload.asset_uid', '0077360b-bf76-4161-998f-4eda10ec5ddf'
                                    ]
                                },
                                'then': {
                                    '$convert': {
                                        'input': '$payload.ammeter-dishwasher',
                                        'to': 'double',
                                        'onError': None,
                                        'onNull': None
                                    }
                                }
                            }
                        ],
                        'default': None
                    }
                }
            }
        }, {
            '$match': {
                'ElectricityUsed': {
                    '$ne': None
                }
            }
        }, {
            '$group': {
                '_id': '$device',
                'totalElectricityConsumption': {
                    '$sum': '$ElectricityUsed'
                }
            }
        }, {
            '$sort': {
                'totalElectricityConsumption': -1
            }
        }
        ]
    result = list(collection.aggregate(pipeline))
    return result[0]["totalElectricityConsumption"] if result else None

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
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        try:
            while True:
                client_message = client_socket.recv(1024).decode()
                if not client_message:
                    break
                print(f"Received message: {client_message}")

                if client_message == "1" or client_message == "average moisture":
                    try:
                        avg_moisture = get_average_moisture(db, "DB1_virtual")
                        response = {"average_moisture": avg_moisture}
                    except Exception as e:
                        response = {"error": str(e)}
                elif client_message == "2" or client_message == "average water used":
                    try:
                        avg_water = get_average_water(db, "DB1_virtual")
                        response = {"average_water_consumption": avg_water}
                    except Exception as e:
                        response = {"error": str(e)}
                elif client_message == "3" or client_message == "most electricity used":
                    try:
                        electricity_usage = usage_electricty(db, "DB1_virtual")
                        response = {"electricity_usage": electricity_usage}
                    except Exception as e:
                        response = {"error": str(e)}
                else:
                    response = {"error": f"Unrecognized command: {client_message}"}

                client_socket.sendall(json.dumps(response).encode())

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()


if __name__ == "__main__":
    start_server()