import urllib2
import MySQLdb
import platform,subprocess,re
from collections import defaultdict

import Queue
import threading

"""
This code uses a given txt file to access certain tables in a database and from those tables retrieves a list of ips which
are then pinged to determine if they are still in use. This new data is then uploaded back into the database
"""

def get_ping(hostname_list,tag, timeout):

	ip_val_dict = {}
	ip_time_dict = {}
	all_data = []
	counter = 0
	counts = 0
	for hostname in hostname_list:
		if hostname[0] not in ip_time_dict:
			ip_time_dict[hostname[0]] = 0 #if its a new hostname, initialize it to 0
		ip_val_dict[hostname[0]] = hostname[1]
		if platform.system() == "Windows": #different for different operating systems
			command="ping "+hostname[0]+" -n 1 -w "+str(timeout*250)
		else:
			command="ping -i "+str(timeout)+" -c 1 " + hostname[0]
		proccess = subprocess.Popen(command, stdout=subprocess.PIPE)
		matches=re.match('.*time=([0-9]+)ms.*', proccess.stdout.read(),re.DOTALL)
		if matches: #if the ping succeeded
			#print hostname[0], matches.group(1)
			counter+=1
			ip_val_dict[hostname[0]] = 0
			ip_time_dict[hostname[0]] = 0
		else: 
			if ip_val_dict[hostname[0]] == 0:
				ip_time_dict[hostname[0]] +=1
				if ip_time_dict[hostname[0]] > 299: #if it has been more than 300 days since last successful ping
					if int(hostname[0].split('.')[3]) < 70:
						ip_val_dict[hostname[0]] = 2 #2 is business, 1 is customer
					else:
						ip_val_dict[hostname[0]] = 1
			else:
				ip_time_dict[hostname[0]] = -1
			#print hostname[0], False
		counts+=1
		print counts

	pinged_data.append((ip_val_dict, tag, ip_time_dict))


def read_file(filename):
#reads in a statndard file and splits it into a list of the ip and access point
	ip_ap_list = []
	f = open(str(filename), "r")
	for line in f:
		split_data = line.split(',')
		ip = split_data[0]
		ap = split_data[1].strip()
		ip_ap_list.append((ip,ap))
	return ip_ap_list



def read_IP(url):
#opens a webpage based on the inputeted url

	username = 'zstaff'
	password = '***********'
	p = urllib2.HTTPPasswordMgrWithDefaultRealm()
	p.add_password(None, url, username, password)
	handler = urllib2.HTTPBasicAuthHandler(p)
	opener = urllib2.build_opener(handler)
	urllib2.install_opener(opener)
	page = urllib2.urlopen(url).read()
	return page

def write_sql(data):


	db = MySQLdb.connect("192.185.******","mrgood_zeecon","*********","mrgood_zipdb" )
	cursor = db.cursor()
	cursor.execute('DROP TABLE IF EXISTS %s' %data[1]) 

	

	sql ="""CREATE TABLE %s  (IP TEXT, AVAILIBILITY INT, TIME INT)""" %data[1]
	cursor.execute(sql)
	for key in data[0]: #for each access point

		sql = ("""INSERT INTO """ + data[1] + """ VALUES (%s,%s,%s)""")
		cursor.execute(sql,(key, data[0][key], data[2][key])) #inserts the ip and thr availibility of the ip into the table
		db.commit()

	
	cursor.execute("""SELECT * FROM %s""" %data[1])
	
	print cursor.fetchall()
	db.close()

def fetch_ip_value_tags(table_names):

	temp_list = []
	ip_list = []

	db = MySQLdb.connect("192.185.46.179","mrgood_zeecon","***********","***********" )
	cursor = db.cursor()

	for name in table_names:

		cursor.execute("""SELECT * FROM %s""" %name)
		ip_val_list = cursor.fetchall()
		for item in ip_val_list: #retrieves every ip in the table and adds it to a list of ips 
			temp_list.append(item)

		ip_list.append((temp_list,name))
		temp_list = []

	db.close()
	return ip_list

def get_ip_tag(data):

	temp_list = []
	ip_tag_list = []

	for item in data:
		for ip_val in item[0]:
			temp_list.append(ip_val[0])
		ip_tag_list.append((temp_list, item[1]))
		temp_list = []
	return ip_tag_list



list_of_ip_ap = read_file("C:\\Users\\Reagan\\Desktop\\Zeecon\\ip_ap.txt")
pinged_data = []
tag_list = []

for item in list_of_ip_ap:
	if item[1] not in tag_list:
		tag_list.append(item[1])

fetched_items = fetch_ip_value_tags(tag_list) #fetches the ips and their values

counter = 0
for item in fetched_items:
	counter+=1
	print counter
	get_ping(item[0], item[1], 1) #pings every ip


for item in pinged_data:

	write_sql(item)#adds the new data to the database


