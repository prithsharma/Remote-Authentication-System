import getpass
import socket
import sys
import threading
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


s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #not used
s3 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #not used
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#def funct2(query,data):	#now this client
#	host = data.split('\t')[0] #ip
#	port = int(data.split('\t')[2])+1 #port
#	path = data.split('\t')[1]
#	#print "\cheker2\n"
#	#print query
#	#print data
#	#print host
#	#print port
#	#print path
#	
#	s3.connect((host,port))
#	
#	#print query
#	s3.send(query)
#	#print path
#	s3.send(path)
#	#print "now shud receive on the thread"
#	a = s3.recv(1000)
#	#print query
#	while (a!="aaaaaaa"):
#		f2 = open(query,"wb")
#		f2.write(a)
#		a=s3.recv(1000)
#		f2.close()	
#	#print "now am done on funct2  thread on the thread"
#	
#	
def abcda(c,a):
	#print "Entered thread"
	ptr1 = c.recv(100)
	#print ptr1
	ptr2 = c.recv(100)
	#print ptr2
	try:
		f = open(ptr2+ptr1,"rb")
	#	print "fileopened"
		a = f.read(1024)
		while (a!=''):
			c.send(a)
			c.send(a)
		c.send("aaaaaaa")
		f.close()
	except Exception , e:
	#	print "file did not open"
		c.send("aaaaaaa")
	#print "\ndone with thread"
	return
		
def funct():
	host = ''
	s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	tupl = s.getsockname()
	port = tupl[1] + 1
	#print ("help us\n")
	#print port
	s2.bind((host,port))
	#print("server started bound\n")
	s2.listen(10)	#upto 10
	while 1: 	#the main loop accepting a socket conn and starting a new thread for hhandling it
        	con ,addr=s2.accept()
        #	print "asdads"
        	newt = threading.Thread(target=abcda, args=(con,addr))
        	newt.daemon = True
        	newt.start()


host = sys.argv[1] #server
port = int(sys.argv[2]) #serverport
#servport = int(sys.argv[3]) #peerport
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print("socket started")


host_ip = socket.gethostbyname(host)
s.connect((host,port))	

s.send("connRequest")
print("Requesting Connection...")
request = s.recv(1000)
if request == 'requestDenied':
	print bcolors.FAIL + "Request denied by server (Access from this IP restricted)" + bcolors.ENDC
	sys.exit()
#newt = threading.Thread(target=funct, args=())
#newt.daemon = True
#newt.start()
#
#
#check =0
#check2 = 0

print("\nWelcome!\n1. Register to a server\n2. Login to a server\n3. Close Connection\n")
loggedIn = 0
while 1:	#the main loop
	option = raw_input("\nEnter Option: ");
	if(option == '1'):
		username = raw_input("username: ")
		
		password = getpass.getpass("password: ");
		passwordRepeat = getpass.getpass("password again: ")
		while password != passwordRepeat:
			print("Entries don't match!")
			password = getpass.getpass("password: ");
			passwordRepeat = getpass.getpass("password again: ")
		
		print('Registering...\n')

		#encrypt
		hash = sha256_crypt.encrypt(password)

		s.send("reg\t"+username+"\t"+hash)
		print 'receiving reply'
		message = s.recv(500)
		print message
		#print("Registered")
	elif(option == '2'):
		if loggedIn == 1:
			print "You are already logged in with username: " + loggedUser
			continue
		username = raw_input("username: ")
		password = getpass.getpass("password: ");
		
		s.send("authenticate\t"+username)
		print "Logging in..."
		reply = s.recv(500)
		if reply.split('\n')[0] == 'error':
			print reply.split('\n')[1]
		elif reply.split('\n')[0] == 'hash':
			hash = reply.split('\n')[1]
			if sha256_crypt.verify(password,hash):
				s.send("loginSuccess\t"+username)
				print "Authentication successful"
				loggedIn = 1
				loggedUser = username
			else:
				s.send("loginFail\t"+username)
				print "Wrong password. Try again"
	elif(option == '3'):
		if loggedIn == 1:
			s.send("close\t"+loggedUser)
		else:
			s.send("close\t")
		closeMsg = s.recv(100)
		print closeMsg
		s.close
		s2.close
		s3.close
		exit(1)
	else:
		print "wrong input"
