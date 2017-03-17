import psycopg2
import datetime

def get_all_auctions(cur):
	cur.execute("""select itemid, auctionendtime, itemdescription
				from itemlistings
				where auctionendtime > now()
				order by auctionendtime
	""")
	rows = cur.fetchall()
	print("All ItemListings:")
	for row in rows:
		print(row)


	return






#connect to db
def connect_to_db():
	try:
	    conn = psycopg2.connect("dbname='cs421' user='cs421g17' host='comp421.cs.mcgill.ca' password='easterbunny-madness'")
	    cur = conn.cursor()
	except:
	    print("I am unable to connect to the database")
	return cur



#initialize db and variables
cur = connect_to_db()
input_str = ""

# user picks option and execute the option
while True:
	input_str = input("Please choose an action:\n" \
				"1. See all live auctions\n" \
				"2. See detailed auction\n" \
				"3. Add an item \n" \
				"4. Place a Bid \n" \
				"5. See my history \n" \
				"6. Quit\n")
	option_int = int(input_str.strip())
	

	# resolve input 
	if option_int == 6:
		break
	elif option_int == 1:
		get_all_auctions(cur)
	else:
		print("You choose {}".format(option_int))


