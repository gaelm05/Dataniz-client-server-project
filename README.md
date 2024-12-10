# CECS_327_Assignment8
Assingment 8

Dataniz 

  -Set up the devices , broker, and database conection
  -Had to go into MongoDB to set up the metadata
  
MongoDB

  -database that holds meta and virtual data 
  -asset id's specific for each device used to be able to query succesfully.
  
Server

  -set up 3 distinct functions for our 3 distinct prompts
  -when connected to the client , recieves keywords and decides which query to run
  -if no keywords match will display an error 
  
  Setup: 
  
    -server must have a valid IP address 
    -server must be ran on an open port 
    -server must have connection string to database 
  -Main goal of the server is to recieve queries , access the database and send the correct answer back to the client.
  Done by usinfg different pipelines depending on what the user is asking for. 
  
Client

  - 
