import psycopg2


def get_all_auctions():
	cur.execute("""SELECT * from itemlistings""")
	rows = cur.fetchall()
	print("All ItemListings:")
	for row in rows:
	    print(row)




#connect to db
def connect_to_db():
	try:
	    conn = psycopg2.connect("dbname='cs421' user='cs421g17' host='comp421.cs.mcgill.ca' password='easterbunny-madness'")
	    cur = conn.cursor()
	except:
	    print("I am unable to connect to the database")



#initialize db and variables
connect_to_db()
input_str = ""

# user picks option and execute the option
while True:
	input_str = input("Please choose an action:\n" \
				"1. See all live auctions\n" \
				"2. Add an item \n" \
				"3. Place a Bid \n" \
				"4. See my history \n" \
				"5. Pay for an item\n"\
				"6. Quit\n")
	option_int = int(input_str.strip())
	get_all_auctions()

	# resolve input 
	if option_int == 6:
		break
	else:
		print("You choose {}".format(option_int))


