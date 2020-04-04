from flaskApp import app
import os



if __name__ == '__main__':
	
	# if not os.path.exists("chromedriver.exe"):
	# 	print(getDriver())
	# app.run(debug=True, host = '0.0.0.0',port=5000)
	
	app.config.update(SESSION_COOKIE_HTTPONLY=False)
	# app.run(debug=True)
	app.run(debug=True, host = '0.0.0.0',port=5000)
	
	# app.run(debug=False, host = '0.0.0.0',port=5000)