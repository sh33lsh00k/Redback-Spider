from flaskApp.models import User, APIFromJSLinks, CrawledEndpoints, BlacklistJSLinks


from flask import render_template, url_for
from flask import Flask, flash, redirect, request
from flaskApp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskApp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import jinja2, json, secrets, os, re, datetime, sys, subprocess, hashlib, requests, jsbeautifier, tldextract
from PIL import Image

from flaskApp.linkAnalyzer import linkExtractorFromJS

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("$@#admin$@#")
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.template_filter()
def increment(input):
    return int(input) + 1


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	else:
		userObj 	= User.query.filter_by(id=current_user.get_id()).first()
		uid 		= userObj.id
		cookie 		= ""
		for key, vals in request.cookies.items():
			cookie += f"{key}: {vals}; "


	scanName = request.args.get("scanName")
	urlToScan = request.args.get("urlToScan")
	if scanName is not None and urlToScan is not None:

		noOfCrawls = apiHTMLContentForCrawl.query.filter_by(userId=uid, crawlName=scanName).count()
		if noOfCrawls >= 1:
			result = apiHTMLContentForCrawl.query.filter_by(userId=uid, crawlName=scanName).first()
			return render_template('home.html', posts={'cookie': cookie, 'scanName': scanName, 'urlToScan':urlToScan, 'subdomainsIncluded': result.subdomainsIncluded, 'paramsIncluded':result.paramsIncluded})
		else:		
			return render_template('home.html', posts={'cookie': cookie, 'scanName': scanName, 'urlToScan':urlToScan})


	#posts.key
	return render_template('home.html', posts={'cookie': cookie})


@app.route('/register', methods=['GET', 'POST'])
# @auth.login_required
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form 	= RegistrationForm()

	if form.validate_on_submit():
		hashed_pwd 	= bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user 		= User(username=form.username.data, email=form.email.data, password=hashed_pwd)
		
		db.session.add(user)
		db.session.commit()

		flash(f'Your account has been created {form.username.data}! You are now able to log in', 'success')
		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET', 'POST'])
# @auth.login_required
def login():

	if current_user.is_authenticated:
		return redirect(url_for('home'))

	form 	= LoginForm()

	if form.validate_on_submit():
		user 	= User.query.filter_by(email=form.email.data).first()

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page 	= request.args.get('next')

			return redirect(next_page) if next_page else redirect(url_for('home'))

			flash(f'You\'ve been Logged In successfully!', 'success')
			return redirect(url_for('home'))

		else: 
			flash('Login Unsuccessfull. Please check email and password!', 'danger')

	return render_template('login.html', title='Login', form=form)






@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	name 			= secrets.token_hex(12)
	_, f_ext 		= os.path.splitext(form_picture.filename)
	picture_fn 		= name + f_ext
	picture_path 	= os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size 	= (125, 125)
	i 	= Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)
	return picture_fn




@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()

	if form.picture.data:
		picture_file 	= save_picture(form.picture.data)
		current_user.image = picture_file

	if form.validate_on_submit():
		current_user.username 	= form.username.data
		current_user.email 		= form.email.data
		db.session.commit()

		flash('Your account has been updated!', 'success')
		redirect(url_for('account'))

	elif request.method == 'GET':
		form.username.data 	= current_user.username
		form.email.data 	= current_user.email

	image_file 	= url_for('static', filename='profile_pics/' + current_user.image)
	return render_template('account.html', title='Account', image_file=image_file, form=form)





@app.route('/api/resetDB', methods=['GET'])
def resetDB():
	db.drop_all()
	db.create_all()

	flash(f'The Database has been resetted successfully!', 'success')
	return redirect(url_for('home'))




@app.route('/api', methods=['GET', 'POST'])
def mainApi():
	if request.method == 'GET':
		return "Sorry, you're entering a rabbit hole! ;)", 404

	else:
		return "Well, I mean it sirrrrrrrrre! :))", 404


def getHTMLContent(URL):
    r = requests.get(URL)
    htmlContent = r.content.decode('utf-8', 'replace')
    return htmlContent

def isHashExists(uid, JSLinkHash, JSLink, crawlerName):
	result = APIFromJSLinks.query.filter_by(userId=uid, JSLink=JSLink, JSLinkHash=JSLinkHash, crawler=crawlerName).count()
	if len(result) > 0:
		return True

	return False








@app.route('/crawl_settings', methods=['GET'])
def crawl_settings():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	userObj 	= User.query.filter_by(id=current_user.get_id()).first()
	uid 		= userObj.id

	result = BlacklistJSLinks.query.filter_by(userId=uid).all()

	JSLinksList = []

	for element in result:
		JSLinksList.append(element.JSLink)


	return render_template('crawl_settings.html', JSLinksList=JSLinksList), 200


@app.route('/dirsearch', methods=['GET'])
def dirsearch():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	userObj 	= User.query.filter_by(id=current_user.get_id()).first()
	uid 		= userObj.id

	return render_template('dirsearch.html'), 200







InProgressAnalyzerDict = {}

@app.route('/api/linkAnalyzer', methods=['POST'])
def linkAnalyzerApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	JSLink = postBody['URL']
	crawlerName = postBody['crawlerName']

	# currently support only 1 crawl at a time
	# in case of multiple crawls then below dict will contain crawlers' name list
	InProgressAnalyzerDict[uid] = crawlerName


	JSLinkTemp = ""
	#get only URL part of JS link
	if "http://" in JSLink:
		JSLinkTemp = JSLink.split("http://")[1]
	elif "https://" in JSLink:
		JSLinkTemp = JSLink.split("https://")[1]
	else:
		JSLinkTemp = JSLink

	# returns only path from URL
	JSLinkTemp = JSLinkTemp.split("/", 1)[1]

	if BlacklistJSLinks.query.filter_by(userId=uid, JSLink=JSLinkTemp).count() > 0:
		return "", 200

	noOfJSLinks = APIFromJSLinks.query.filter_by(userId=uid, JSLink=JSLink, crawler=crawlerName).count()

	htmlContent = getHTMLContent(JSLink)
	JSLinkHash = hashlib.md5(htmlContent.encode('utf-8')).hexdigest()


	if noOfJSLinks > 0:
		if isHashExists(uid, JSLinkHash, JSLink, crawlerName) == True:
			print("Hash already exists: " + JSLinkHash)		
			#APIs are already extracted from same JS file so return 
			return "", 200
		else:
			# same JS link with different hash already exists in database
			pass
		

	print("New JSlink with hash: " + JSLinkHash)

	d 		 = datetime.datetime.today()
	dateTime = d.strftime('%d-%m-%Y %H:%M:%S')

	allEndPoints = linkExtractorFromJS(htmlContent)

	if len(allEndPoints) > 0:
		for endpoint in allEndPoints:
			APIcontext = endpoint["link"] + "^^^^^^^^" + endpoint["context"]
			addContent = APIFromJSLinks(userId=uid, JSLink=JSLink, APIcontext=APIcontext,
										crawler=crawlerName, dateTime=dateTime, JSLinkHTML=htmlContent, JSLinkHash=JSLinkHash)
			db.session.add(addContent)

		db.session.commit()

		print("Data Added against JS Link: " + JSLink)


	return "", 200


# On crawler stop -> stores all crawled endpoints
@app.route('/api/crawlerStop', methods=['POST'])
def crawlerStopApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id


	crawlerName = request.form.get('crawlerName')
	crawledEndpoints = request.form.get('crawledEndpoints')

	obj = CrawledEndpoints(userId=uid, crawler=crawlerName, crawledEndpoints=crawledEndpoints.strip())
	db.session.add(obj)
	db.session.commit()

	# currently supports only 1 crawl at a time
	# in case of multiple crawls then below dict will just remove completed crawler name from crawlers' list
	del InProgressAnalyzerDict[uid]

	return '', 200




@app.route('/api/blackListJSLink', methods=['POST'])
def blackListJSLinkApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']
	JSLink = postBody['JSLink']


	#get only URL part of JS link
	if "http://" in JSLink:
		JSLink = JSLink.split("http://")[1]
	elif "https://" in JSLink:
		JSLink = JSLink.split("https://")[1]
	else:
		JSLink = JSLink

	# returns only path from URL
	JSLink = JSLink.split("/", 1)[1]

	if BlacklistJSLinks.query.filter_by(userId=uid, JSLink=JSLink).count() == 0: 
		obj1 = BlacklistJSLinks(userId=uid, JSLink=JSLink)
		db.session.add(obj1)
		db.session.commit()
		return json.dumps({"message": "Blacklisted" }) , 200


	return json.dumps({"message": "Already Blacklisted" }) , 200


@app.route('/api/whiteListJSLink', methods=['POST'])
def whiteListJSLinkApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	JSLink = postBody['JSLink']


	if BlacklistJSLinks.query.filter_by(userId=uid, JSLink=JSLink).count() > 0: 
		BlacklistJSLinks.query.filter_by(userId=uid, JSLink=JSLink).delete()
		db.session.commit()
		return json.dumps({"message": "Whitelisted" }) , 200


	return json.dumps({"message": "Already Whitelisted" }) , 200



@app.route('/api/getEndpoints', methods=['POST'])
def getEndpointsApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']

	result = CrawledEndpoints.query.filter_by(userId=uid, crawler=crawlerName).all()
	endpointsList = []

	for row in result:
		endpointsList.append(row.crawledEndpoints)		

	return json.dumps(endpointsList), 200


@app.route('/jsContent', methods=['GET'])
def getJSContentAPI():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	JShash = request.args.get('hash')
	crawlerName = request.args.get('crawlerName')

	if JShash is None or JShash == "" or crawlerName is None or crawlerName == "":
		return render_template("JSContent.html", content={"content":"no result"} ), 200

	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id


	if APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName, JSLinkHash=JShash).count() >= 1:
		result = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName, JSLinkHash=JShash).first()
		data = jsbeautifier.beautify(result.JSLinkHTML)
		return render_template("JSContent.html", content={"content":data, "link":result.JSLink} ), 200 


	return render_template("JSContent.html", content={"content":"no result"} ) , 200




@app.route('/api/isCrawlNameExists', methods=['POST'])
def isCrawlNameExistsApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']

	noOfCrawls = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).count()

	if noOfCrawls == 0:
		return json.dumps({"crawls":0}), 200

	return json.dumps({"crawls":noOfCrawls}), 200



@app.route('/api/compareCrawlers', methods=['POST'])
def compareCrawlersApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']
	crawlerToCompare = postBody['crawlerToCompare']

	noOfCrawls = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).count()
	noOfCrawlsT = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerToCompare).count()


	if noOfCrawls == 0 or noOfCrawlsT == 0:
		return json.dumps({}), 200


	resultOne = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).all()
	resultTwo = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerToCompare).all()

	listOne = []
	for row in resultOne:
		listOne.append(row.APIcontext)

	for row2 in resultTwo:
		if row2.APIcontext in listOne:
			listOne.remove(row2.APIcontext)
	
	JSLinksdict = {}
	for row in resultOne:
		if row.APIcontext in listOne:
			if row.JSLink not in JSLinksdict:
				JSLinksdict[row.JSLink + "^^^^^^^^" + row.JSLinkHash] = []

			JSLinksdict[row.JSLink + "^^^^^^^^" + row.JSLinkHash].append(row.APIcontext)

	return json.dumps(JSLinksdict), 200




@app.route('/api/compareCrawledEndpoints', methods=['POST'])
def compareCrawledEndpointsApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']
	crawlerToCompare = postBody['crawlerToCompare']

	noOfCrawls = CrawledEndpoints.query.filter_by(userId=uid, crawler=crawlerName).count()
	noOfCrawlsT = CrawledEndpoints.query.filter_by(userId=uid, crawler=crawlerToCompare).count()


	if noOfCrawls == 0 or noOfCrawlsT == 0:
		return json.dumps({}), 200


	resultOne = CrawledEndpoints.query.filter_by(userId=uid, crawler=crawlerName).first()
	resultTwo = CrawledEndpoints.query.filter_by(userId=uid, crawler=crawlerToCompare).first()

	listOne = resultOne.crawledEndpoints.split("\n")
	listTwo = resultTwo.crawledEndpoints.split("\n")


	for endpoint in listTwo:
		if endpoint in listOne:
			listOne.remove(endpoint)
	
	return json.dumps(listOne), 200




@app.route('/api/getAllCrawlers', methods=['GET'])
def getAllCrawlersApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	result = APIFromJSLinks.query.filter_by(userId=uid).all()
	Crawlers = {}

	for row in result:
		Crawlers[row.crawler] = row.dateTime		

	return json.dumps(Crawlers), 200



@app.route('/report', methods=['GET'])
def report():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	result = APIFromJSLinks.query.filter_by(userId=uid).all()
	crawlersDict = {}

	for row in result:
		crawlersDict[row.crawler] = row.dateTime


	font_file 	= url_for('static', filename='fonts/poppins/Poppins-Regular.ttf')
	font_file_bold 	= url_for('static', filename='fonts/poppins/Poppins-Bold.ttf')

	return render_template('report.html', title='Report', crawlersDict=crawlersDict,
							 font_file=font_file, font_file_bold=font_file_bold), 200





#get crawler name and returns all JS links data
@app.route('/api/dumpLinks', methods=['POST'])
def dumpLinksApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))


	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']


	result = APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).all()
	JSLinksdict = {}

	for row in result:

		if row.JSLink not in JSLinksdict:
			JSLinksdict[row.JSLink + "^^^^^^^^" + row.JSLinkHash] = []

		JSLinksdict[row.JSLink + "^^^^^^^^" + row.JSLinkHash].append(row.APIcontext)


	# print(JSLinksdict)


	return  json.dumps(JSLinksdict) , 200


@app.route('/api/deleteCrawler', methods=['POST'])
def deleteCrawlerApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']

	if APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).count() > 0:
		APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName).delete()
		db.session.commit()
		return json.dumps({"message": "Deleted"}), 200

	return json.dumps({"message": "Failed"}), 202

@app.route('/api/deleteJSLink', methods=['POST'])
def deleteJSLinkApi():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	userObj = User.query.filter_by(id=current_user.get_id()).first()
	uid = userObj.id

	postBody = request.get_json(silent=True)
	crawlerName = postBody['crawlerName']
	JSLinkHash 		= postBody['JSLinkHash']

	if APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName, JSLinkHash=JSLinkHash).count() > 0:
		APIFromJSLinks.query.filter_by(userId=uid, crawler=crawlerName, JSLinkHash=JSLinkHash).delete()
		db.session.commit()
		return json.dumps({"message": "Deleted"}), 200

	return json.dumps({"message": "Failed"}), 202