"""
# Setting up SQLite3 DB

from flaskApp import db
db.create_all()

# For interacting with the DB
# from <flaskMainFileName> import User, Post
from flaskApp import User, Post


# Creating new users
user1 	= User(username='John Doe', email='jd@demo.com', password='p@ssw0rd')
user2	= User(username='Tmp User', email='tu@demo.com', password='p@ssw0rd')

db.session.add(user1)
db.session.add(user2)

# After adding users, commiting them to the Database
db.session.commit()

# Listing all of our Users:
User.query.all()

# Listing only the first User:
User.query.first()

# Filtering results by usernames
User.query.filter_by(username='Corey').all()

# Declaring results in a var
user 	= User.query.filter_by(username='Corey').first()
user 	= User.query.filter_by(username='asdfasdf').first()

# Printing the object and seeing its attributes
print(user)
print(user.id)

# Printing some user essentials from the User object
user 	= User.query.get(1)
print(user)
print(user.id)
print(user.username)
print(user.posts)

---

# Creating a new post
post_1 = Post(title='Blog 1', content='First Page Content!', user_id=user.id)
post_2 = Post(title='Blog 2', content='Second Post Content', user_id=user.id)

db.session.add(post_1)
db.session.add(post_2)

db.session.commit()

---

# Printing Them Posts:
user.posts

# Printing Posts stuff
for post in user.posts:
	print(post.title)

# Querying the First Post
post = 	Post.query.first()
print(post)
print(post.user_id)
print(post.author)



--- 

# Dropping everything from the DB
db.drop_all()

# Recreating the Tables/Columns in the DB again
db.create_all()

# Now the following will return empty because, everything's resetted.
User.query.all()
Post.query.all()

[]

---
"""

"""
Password Hashing and stuff using bcrypt

$ pip install flask-bcrypt

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
bcrypt.generate_password_hash('testing')

# Generating Password Hash // Its different everytime though!
passwd_hash = bcrypt.generate_password_hash('testing')

# Checking password with hash
bcrypt.check_password_hash(hashed_pwd, 'password')
bcrypt.check_password_hash(hashed_pwd, 'testing')






---



	# code 		= ApiCalls(pythonCode=json.dumps(apiData))
	# db.session.add(code)
	# db.session.commit()

	# print(ApiCalls.query.all())







	# seleniumCodeWithCalls 	= substituteSeleniumCode(apiData)
	# print(json.loads(json.dumps(seleniumCodeWithCalls))['substitdPythonCode']) # Print Beautified Code

	# pythonCode 	= json.loads(json.dumps(seleniumCodeWithCalls))['substitdPythonCode']

	# print(pythonCode)
	# exec(json.loads(json.dumps(seleniumCodeWithCalls))['substitdPythonCode'])


	# scriptFPath = os.path.join(os.getcwd(), scriptPath, scriptName)
	# sys.path.insert(1, os.path.join(os.getcwd(), scriptPath))

	# with open(scriptFPath, 'w+') as f:
	# 	f.write(pythonCode)





	

	descCode 	= ApiCalls.query.order_by(ApiCalls.id.desc())
	entry 		= descCode.first()
	code 		= entry.pythonCode

	# print(descCode)
	# print(entry)
	# print(json.loads(code)['pythonCode'])





https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/


https://flask.palletsprojects.com/en/1.1.x/templating/



"""