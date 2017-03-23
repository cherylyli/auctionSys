from flask import render_template, request, redirect, url_for
from app import app
import psycopg2
from time import gmtime, strftime
import json

#connect to db
def connect_to_db():
    try:
        conn = psycopg2.connect("dbname='cs421' user='cs421g17' host='comp421.cs.mcgill.ca' password='easterbunny-madness'")
        cur = conn.cursor()
    except:
        print("I am unable to connect to the database")
    return cur, conn

cur, conn = connect_to_db()

# prompt user to login
@app.route('/')
def hello():
    return render_template("login.html", message="")

# login and redirect
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cur.execute("select * from users where users.email='"+email+"' and users.password='"+password+"';")
    user = cur.fetchall()

    # if user with the password and email exists in db, log the person in.
    if len(user) == 1:
        return redirect(url_for('get_all_auctions', email=email))
    else:
        return render_template("login.html", message="Login failed, please try again.")

# get all auctions
@app.route('/auctions')
def get_all_auctions():
    # get info on all auction items that have an end time greater than now()
    cur.execute("select itemid, auctionendtime, itemdescription from itemlistings where auctionendtime > now() order by auctionendtime;")
    auctions = cur.fetchall()

    # sometimes messages are passed to this function by other functions calling this function
    email = request.args.get('email')
    message = request.args.get('message')
    if message is None:
        message = ""
    return render_template('auctions.html', title="auctions", auctions=auctions, email=email, message=message)

# get owner's info, item's info, and bids on item 
@app.route('/auction/<auctionid>')
def get_detail_auction(auctionid):

    # get the item
    cur.execute("""select * from itemlistings where itemid="""+auctionid+""";""")
    auction_description = cur.fetchone()

    # get the offers made on that item
    cur.execute("""select amount,o.time,madebyuser 
                from offers o, owners own, itemlistings i 
                where o.itemid="""+auctionid+""" And own.email=i.seller and o.itemid=i.itemid order by o.time;""")
    offers = cur.fetchall()

    # get the seller's average rating and email
    cur.execute("""select own.email,avgrating
                from owners own, itemlistings i 
                where i.itemid="""+auctionid+"""And own.email=i.seller;
                """)
    owner_description = cur.fetchone()


    email = request.args.get('email')
    message = request.args.get('message')
    if message is None:
        message = ""

    return render_template('detailed_auction.html', title="auction", auction=auction_description, offers=offers, owner=owner_description, email=email, message=message)


# place a bid
@app.route('/placebid', methods=['POST'])
def make_bid():
    auctionid = request.form['auctionid']
    email = request.form['email']
    bid = int(request.form['bid'])

    if bid<0:
        return redirect(url_for("get_detail_auction", message="Invalid bid number", email=email, auctionid=auctionid)) 


    # check if current user is suspended
    cur.execute("select * from suspendedusers s where s.useremail='"+email+"';")
    suspended = cur.fetchone()
    if suspended:
        return redirect(url_for("get_detail_auction", message="Your account has been suspended due to suspicious activity", email=email, auctionid=auctionid)) 

    # check if auction has ended
    cur.execute("Select * from itemlistings where itemid="+auctionid+" and auctionendtime>now();")
    auction = cur.fetchone()
    if not auction:
        return redirect(url_for("get_detail_auction", message="Auction has ended.", email=email, auctionid=auctionid))
    
    # select max bid and check if this bid surpasses previous bid
    cur.execute("Select max(amount) from offers where itemid="+auctionid+";")
    highest_bid = cur.fetchone()
    if highest_bid and highest_bid[0] >= bid:
        return redirect(url_for("get_detail_auction", message="Bid amount did not exceed previous bids.", email=email, auctionid=auctionid))
    else:
        cur.execute("Insert into offers values ("+auctionid+ "," +str(bid)+",now(),'"+email+"')")
        conn.commit() 
        return redirect(url_for("get_detail_auction", message="Successfully placed bid", email=email, auctionid=auctionid))


# Add an item. If user not in seller table, add them first
@app.route('/additem', methods=['POST'])
def add_item():
    email = request.form['email']
    item_description = request.form['item_description']
    end_time_date = request.form['end_time_date']
    end_time_time = request.form['end_time_time']
    end_time = end_time_date + " " + end_time_time + ":00"

    # check if current user is suspended
    cur.execute("select * from suspendedusers where useremail='"+email+"';")
    suspended = cur.fetchone()
    if suspended:
        return redirect(url_for("get_all_auctions", email=email, message="Your account has been suspended due to suspicious activity."))

    # check if current user is a seller, if not, insert into sellers table
    cur.execute("select * from owners where email='"+email+"';")
    new_owner = cur.fetchone()

    if new_owner is None:
        try:
            print('insert into "owners" (email, numberratings, avgrating) values (\''+email+'\', 0, 0);')
            cur.execute('insert into "owners" (email, numberratings, avgrating) values (\''+email+'\', 0, 0);')
        except Exception as e:
            return redirect(url_for("get_all_auctions", email=email, message=e))

    # check if current seller has >5 reviews and <3.0/5 rating    
    cur.execute("select * from owners o where o.email='"+email+"' and (o.numberratings<5 or o.avgrating>3 ); ")
    good_user = cur.fetchone()

    if good_user is None:
        return redirect(url_for("get_all_auctions", email=email, message="Your seller rating is lacking so you cannot add items anymore."))


    # get the next available item id
    cur.execute("select max(itemid) from itemlistings")
    max_id = cur.fetchone()[0] + 1

    # add the item
    try:
        print("Insert into itemlistings values("+str(max_id)+", '"+str(end_time) + strftime("%z", gmtime())+"', "+ str(0) + ", '"+ item_description+ "', '"+ email+ "', now() );")
        cur.execute("Insert into itemlistings values("+str(max_id)+", '"+str(end_time) + strftime("%z", gmtime())+"', "+ str(0) + ", '"+ item_description+ "', '"+ email+ "', now() );")
    except Exception as e:
        return redirect(url_for("get_all_auctions", email=email, message=e))


    # commit changes in local cached db to remote db
    conn.commit() 
    return redirect(url_for("get_all_auctions", email=email, message="Successfully posted your item!"))


# retreive user's history
@app.route('/history')
def see_history():
    # retreive user's email, passed as argument from request
    email = request.args.get('email')
    offers = {}
    posted_items = []

    # get all items that user has posted
    try:
        cur.execute("select itemid, auctionendtime, itemdescription from itemlistings where seller ='" + email + "';")
        posted_items = cur.fetchall() 
        

        # for each item that the use has posted, get all the offers that have been made on it
        for i in posted_items:
            print(i[0])
            print("Select amount, time, madebyuser from offers where itemid=" +str(i[0])+";")
            cur.execute("Select amount, time, madebyuser from offers where itemid=" +str(i[0])+";")
            offers_on_item = cur.fetchall()
            offers[i[0]] = offers_on_item

    except Exception as e:
        print(e)

    return render_template('history.html', email=email, posted_items=posted_items, offers=offers)


# let user change the item description. Problem is the item description cannot have any " or ' in it. Otherwise fails.
@app.route('/changeitemdes', methods=['POST'])
def change_itemDescription():
    # get parameters passed from request
    email = request.form['email']
    item_description = request.form['item_description']
    itemid = request.form['itemid']


    # update the itemdescription for the item
    try:
        cur.execute("update \"itemlistings\" set itemdescription=\'" + item_description + "\' where itemid=" + str(itemid) + ";")
    except Exception as e:
        print(e)


    # commit the changes from local db (cached version) to remote db
    conn.commit()
    return redirect(url_for("see_history", email=email))


