import socket
import ipaddress

# creates socket object
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIP = input("Enter the IP address of the Server\n:")
serverPort = int(input("Enter the port number of the server\n:"))
connected = False
try:
    myTCPSocket.connect((serverIP, serverPort))
    # this lets the socket send packets to test if the connection is live even when the user doesn't send any messages
    myTCPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    print(f'Connected to {serverIP}')
    connected = True
    print('!!Type "end chat" to quit!!')
    print('!Enter "help" for commands!')
    someData = input("Enter a command\n:")

except socket.error as error:
    print(f'Connection failed: {error}')


maxBytesToReceive = 4096

def help_user():
    print("Try these commands")
    print("what is the average moisture inside my kitchen fridge in the past three hours?\n"
          "what is the average water consumption per cycle in my smart dishwasher?\n"
          "which device consumed more electricity among my three IoT devices?")

while connected & (someData != 'end chat'):
    serverResponse = None

    if someData == "help":
        help_user()
    elif someData == "what is the average moisture inside my kitchen fridge in the past three hours?":
        myTCPSocket.send(bytearray(str('average mositure'), encoding = 'utf-8'))
    elif someData == "what is the average water consumption per cycle in my smart dishwasher?":
        myTCPSocket.send(bytearray(str('average water used'), encoding = 'utf-8'))
    elif someData == "which device consumed more electricity among my three IoT devices?":
        myTCPSocket.send(bytearray(str('most electricity used'), encoding = 'utf-8'))
    else:
        print('Sorry, this query cannot be processed. Try typing "help"')

    #myTCPSocket.send(bytearray(str(someData), encoding = 'utf-8'))

    #serverResponse = myTCPSocket.recv(maxBytesToReceive)

    if serverResponse != None:
        print(f'{serverIP}:')
        print(serverResponse.decode('utf-8'))
    someData = input(":")
    if someData == None:
        someData = ' '


print('quitting chat')
myTCPSocket.close()