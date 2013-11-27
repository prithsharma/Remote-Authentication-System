import socket
import threading
import Queue
import sqlite3
import sys
from passlib.hash import sha256_crypt

######## Coloured text ###########
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

###############################



check =0
check2 =0 

restrictedIP = []
with open('restrictIP.conf') as inputFile:
	for line in inputFile:
		restrictedIP.append(line.strip())

#print restrictedIP


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
				#print 'process started'
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
				#print bcolors.WARNING + "----> "+ username+ " logging in" + bcolors.ENDC
				cursor2.execute("SELECT * FROM users WHERE username = '" +username+ "'")
			
				res = cursor2.fetchone()
				#print res
				if res == None:
					#print bcolors.FAIL + "----> username: " + username + " not found"
					c.send("error\nUsername doesn't exist")
				else:
					c.send("hash\n"+res[1])
					
	

activeUsers = {}
#the function started by main, enqueues in priority q
def new_client(conn,addr):
    flag = 1
    incom = conn.recv(10000)
    if incom.split('\t')[0] == 'connRequest':
    	if addr[0] in restrictedIP:
    		conn.send("requestDenied")
    		flag = 0
    		conn.close()
    		print bcolors.WARNING + "\n----> Connection request from " +addr[0]+ " denied" + bcolors.ENDC + "\n>>"
    	else:
    		conn.send("requestAccepted")
    		print bcolors.OKGREEN + "\n----> Connection request from " +addr[0]+ " accepted" + bcolors.ENDC + "\n>>"

	if flag == 1:
		while 1:
			incom = conn.recv(10000)
			if addr[0] in restrictedIP:
				incom = 'close\t'
			if incom.split('\t')[0] == 'close':
				if incom.split('\t')[1]:
					print bcolors.OKBLUE + "\n----> "+incom.split('\t')[1]+" logged out" + bcolors.ENDC + "\n>>"
					del activeUsers[incom.split('\t')[1]]

				conn.send('Connection closed.')
				print bcolors.OKBLUE + "\n----> Connection with "+addr[0]+" closed" + bcolors.ENDC + "\n>>"
				
				conn.close()
				break
			elif incom.split('\t')[0] == "reg":
				prio = 2
			elif incom.split('\t')[0] == "authenticate":
				prio = 1
			elif incom.split('\t')[0] == "loginSuccess":
				username = incom.split('\t')[1]
				print bcolors.OKGREEN + "\n----> "+username+" logged in" + bcolors.ENDC + "\n>>"
				activeUsers[username] = addr[0]
			queue.put((conn,addr,incom),prio)


def adminConfig(connSql):
	print "Admin Panel: \n1. See Active Users\n2. Restrict IP\nCtrl-C for Exit\n"
	while(1):
		option = raw_input("Enter option>>")
		if option == '1':
			for user in activeUsers:
				print user+" : "+activeUsers[user]
		elif option == '2':
			ip = raw_input("Enter IP to be restricted: ")
			restrictedIP.append(ip)
			file = open("restrictIP.conf", "ab")
			file.write(ip+"\n")
			file.close()




#sqlite
connSql = sqlite3.connect("users.db",check_same_thread = False)
cursor1 = connSql.cursor()
cursor2 = connSql.cursor()
cursor3 = connSql.cursor()
cursor1.execute('create table if not exists users(username TEXT, password TEXT)')
#cur.execute('create table if not exists peers(peer TEXT, test TEXT)')

#socket establishment
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print bcolors.OKBLUE + "socket started" + bcolors.ENDC

host = ''
port = int(sys.argv[1])
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
print bcolors.OKBLUE + "socket bound" + bcolors.ENDC

s.listen(10)	#upto 10
print bcolors.OKGREEN + "Server Ready, Listening for clients\n" + bcolors.ENDC

newt1 = threading.Thread(target=runthrs, args=(connSql,))
newt1.daemon = True
newt1.start()
        
adminConfig = threading.Thread(target=adminConfig, args=(connSql,))
adminConfig.daemon = True
adminConfig.start()


while 1: 	#the main loop accepting a socket conn and starting a new thread for hhandling it
        con,addr=s.accept()
        newt = threading.Thread(target=new_client, args=(con,addr))
        newt.daemon = True
        newt.start()
        
        #runthrs2 = threading.Thread(target=runthrs, args=(connSql,))
        #runthrs2.daemon = True
        #runthrs2.start()