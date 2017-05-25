# auctionSys
Class Project for DataBase Systems

1. Install Python and Pip in version 3.x
2. Install psycopg2 and flask
	- Install psycogp2 by following instructions here: http://initd.org/psycopg/docs/install.html
	- Install flask using pip: `pip install flask`

```
cd AuctionWebApp 
python run.py
```
Go to `localhost:5000` to login.

You may login with cheryl@cheryl.com with password 123 or cheryl@mail.mcgill.ca with password 123
   
Pages we have:
1. Login page:  
	-we execute a select sql query on the users table and check to see if the username and password match. ( some examples are:  username: cheryl@cheryl.com password: 123 username: nicolas.velastegui@mail.mcgill.ca password: savage ( this is a suspended user)			
	-if they don't match we catch the exception and give an error message
	-html input types have some restrictions that prevent malicious use.
				
2.All Auctions Page:    
	-In the home directory we can see all actve itemlistings (view all auction, top of page) sorted by auction end time, this was done through a select query on all itemlistings that have an end date later then now().
	-Also we have the option of viewing the current history of the user that is logged in
	-We can log out bringing us back to the login page.
	-The user can add an put an item up for auction as well. This is done through an sql insert statement, after doing checks and printing error messages if there are errors.
				
3.View history: 
	-For the given user, we can see all the items they posted as well as the offers received for each item these are multiple sql select statments on the item(based on item id) and the offers received (based on itemid)
				
4.Details regarding an auction:
	-For a given auction ( click on any auction in the view all auctions page) we see the related information pertaining to the specific auction id. This information was gathered through select statements on the item id for multiple tables (itemlistings, owners and offers table).		
	-We can also place a bid on this item. The bid must be higher then the current highest bid posted otherwise and error message will happen. This is done through an sql insert statement but only after several sql select statements are run to give the current highest bid and compare.
