import urllib2
import MySQLdb
import platform,subprocess,re
from collections import defaultdict

def get_ping(hostname_list,tag, timeout):

	"""
	Gets the ping of every IP adress and returns and updated list of IPs mapped to a number indicating availibity
	and another number indicating the number of days since the the last ping

	"""

	ip_val_dict = {}
	ip_time_dict = {}
	all_data = []
	counter = 0
	for hostname in hostname_list:
		#hostname is an ip adress

		ip_time_dict[hostname[0]] = hostname[2]
		ip_val_dict[hostname[0]] = hostname[1]
		#intializes both the avalibility dictionary and the time dictionary of the current IP to its previous values

		######################################
		#If for some reason the database has some IPs wrong related to which is admin and user uncomment this section
		#Then comment out the remaining portion of this function leaving only the return statement
		"""

		if ip_time_dict[hostname[0]] > 0:

			if int(hostname[0].split('.')[3]) < 70:
				ip_val_dict[hostname[0]] = -1

			else:
				ip_val_dict[hostname[0]] = 0
		"""
		######################################
		
		if platform.system() == "Windows":
			command="ping "+hostname[0]+" -n 1 -w "+str(timeout*500)
		else:
			command="ping -i "+str(timeout)+" -c 1 " + hostname[0]
		proccess = subprocess.Popen(command, stdout=subprocess.PIPE)
		matches=re.match('.*time=([0-9]+)ms.*', proccess.stdout.read(),re.DOTALL)
		#returns True if it receives a ping

		#int(hostname[0].split('.')[3]) is the last section of the current ip
		if matches and int(hostname[0].split('.')[3]) < 70:
			ip_val_dict[hostname[0]] = -1
			ip_time_dict[hostname[0]] = 0
		elif matches and int(hostname[0].split('.')[3]) >= 70:
			ip_val_dict[hostname[0]] = 0
			ip_time_dict[hostname[0]] = 0
		else: 
			#if there is no successful ping
			if ip_val_dict[hostname[0]] == 0:
				#if it was not availble before then:
				ip_time_dict[hostname[0]] += 1
				if ip_time_dict[hostname[0]] > 299:
					#if it has been inactive for 300 days, resets it to be availible
					if int(hostname[0].split('.')[3]) < 70:
						ip_val_dict[hostname[0]] = 2
					else:
						ip_val_dict[hostname[0]] = 1
			else:
				ip_time_dict[hostname[0]] = -1
		counter+=1
		print counter
		
	return (ip_val_dict, tag, ip_time_dict)

def read_file(filename):
	#reads the file given

	ip_ap_list = []
	f = open(str(filename), "r")
	for line in f:
		split_data = line.split(',')
		ip = split_data[0]
		ap = split_data[1].strip()
		ip_ap_list.append((ip,ap))
	return ip_ap_list

def write_sql(data):

	#given a list of tuples where the tuples are (dicitonary, string, dictionary)
	#writes to the database the two dictionaries to a table with the name of the string given

	print data[0]
	db = MySQLdb.connect("192.185.******","mrgood_zeecon","*********","mrgood_zipdb" )
	cursor = db.cursor()
	cursor.execute('DROP TABLE IF EXISTS %s' %data[1])
	sql ="""CREATE TABLE %s  (IP TEXT, AVAILIBILITY INT, TIME INT)""" %data[1]
	cursor.execute(sql)

	for key in data[0]:

		sql = ("""INSERT INTO """ + data[1] + """ VALUES (%s,%s,%s)""")
		cursor.execute(sql,(key, data[0][key], data[2][key]))
		db.commit()

	cursor.execute("""SELECT * FROM %s""" %data[1])
	print cursor.fetchall()
	db.close()

def fetch_ip_value_tags(table_names):

	#given a list of table names, returns the data in that table

	temp_list = []
	ip_list = []

	db = MySQLdb.connect("192.185.46.179","mrgood_zeecon","Z33c0nZ@dm1n","mrgood_zipdb" )
	cursor = db.cursor()

	for name in table_names:

		cursor.execute("""SELECT * FROM %s""" %name)
		ip_val_list = cursor.fetchall()
		for item in ip_val_list:
			temp_list.append(item)

		ip_list.append((temp_list,name))
		temp_list = []

	db.close()
	return ip_list

def run(list_of_ip_ap):

	#calls each seperate funciton in the correct order to successfullly run the program
	
	counter = 0
	tag_list = []
	pinged_data = []
	
	for item in list_of_ip_ap:
		if item[1] not in tag_list:
			tag_list.append(item[1])
	print tag_list
	
	fetched_items = fetch_ip_value_tags(tag_list)
	
	for item in fetched_items:
		pinged_data.append(get_ping(item[0],item[1], 1))

	for item in pinged_data:
		print item
		counter += 1
		write_sql(item)
######################
def new_table_write_sql(table_name, ip_str):
	
#Creates a new table; use this for new towers
#It will intialize a new table to incorrect values but in such a way that running the program afterwards will correct it
#Before running the real program again make sure you add the tower code to the ip_ap.txt in the format (some_string, tower_code)

	temp_dict = {}
	for num in range(0,256):
		temp_str = ip_str+str(num)
		if num < 70:

			temp_dict[temp_str] = 2
		else:
			temp_dict[temp_str] = 1
	write_sql((temp_dict, table_name, temp_dict))
#new_table_write_sql('FGM9', '10.10.9.')
#^^^ This line will add a new table ('tower_name', 'first three sections of the ip for that tower')
########################

run(read_file("C:\\Users\\Reagan\\Desktop\\Zeecon\\ip_ap.txt"))
