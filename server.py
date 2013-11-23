

import socket
import threading
import Queue
import sqlite3
import sys
from passlib.hash import sha256_crypt

check =0
check2 =0 

queue = Queue.PriorityQueue()

#th1 function wchich handles the various requests and stores and retrieves from db....runs all the tim
def runthrs(connSql):
	while 1:
		if (queue.empty() != True):
			#print "here"
			msg = queue.get()
			c = msg[0]
			a = msg[1]
			incom = msg[2]
			if (incom.split('\t')[0] == "reg"):
				username = incom.split('\t')[1]
				password = incom.split('\t')[2]
				print 'process started'
				#print "username: "+username+"\npassword: "+password+'\n'
				cursor1.execute("SELECT * FROM users WHERE username = \"" +username+ "\"")
				#print "trying to find already existing user"
				new = cursor1.fetchone()
				if new != None:
					#print new
					c.send("ERROR: username already exists")
				else:
					#print 'registering'
					with connSql:
						cursor1.execute( "INSERT INTO users VALUES ('" +username+ "','" +password+ "')" )		
					c.send("Registered")
			elif (incom.split('\t')[0] == "authenticate"):
				username = incom.split('\t')[1]
				print username+" logging in"
				cursor2.execute("SELECT * FROM users WHERE username = '" +username+ "'")
			
				res = cursor2.fetchone()
				print res
				if res == None:
					c.send("Username doesn't exist")
				else:
					c.send(res[1])
					
	
	
#the function started by main, enqueues in priority q
def new_client(c,a):
    #incom = c.recv(10000)
    while 1:
    	incom = c.recv(10000)
    	if incom.split('\t')[0] == 'close':
    		c.send('Connection closed.')
    		print "connection with "+a[0]+" closed."
    		c.close()
    		break
    	elif incom.split('\t')[0] == "reg":
    		prio = 2
    	elif incom.split('\t')[0] == "authenticate":
    		prio = 1
    	queue.put((c,a,incom),prio)

#sqlite
connSql = sqlite3.connect("users.db",check_same_thread = False)
cursor1 = connSql.cursor()
cursor2 = connSql.cursor()
cursor3 = connSql.cursor()
cursor1.execute('create table if not exists users(username TEXT, password TEXT)')
#cur.execute('create table if not exists peers(peer TEXT, test TEXT)')

#socket establishment
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("socket started")

host = ''
port = int(sys.argv[1])
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
print("socket bound")

s.listen(10)	#upto 10
print("Server Ready, Listening for clients")

newt1 = threading.Thread(target=runthrs, args=(connSql,))
newt1.daemon = True
newt1.start()
        
while 1: 	#the main loop accepting a socket conn and starting a new thread for hhandling it
        con,addr=s.accept()
        newt = threading.Thread(target=new_client, args=(con,addr))
        newt.daemon = True
        newt.start()
        
        runthrs2 = threading.Thread(target=runthrs, args=(connSql,))
        runthrs2.daemon = True
        runthrs2.start()