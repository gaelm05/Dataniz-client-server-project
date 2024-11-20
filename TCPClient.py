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
    someData = input("Enter a message you want to send\n:")

except socket.error as error:
    print(f'Connection failed: {error}')


maxBytesToReceive = 4096


while connected & (someData != 'end chat'):
    myTCPSocket.send(bytearray(str(someData), encoding = 'utf-8'))

    serverResponse = myTCPSocket.recv(maxBytesToReceive)

    if serverResponse != None:
        print(f'{serverIP}:')
        print(serverResponse.decode('utf-8'))
    print("You:")
    someData = input()
    if someData == None:
        someData = ' '


print('quitting chat')
myTCPSocket.close()