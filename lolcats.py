from random import randint

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
	str(randint(0,5))
	return '<img src=\'https://s3-us-west-1.amazonaws.com/randomlolcatz/'+str(randint(0,5))+'.jpg\'>'

if __name__ == "__main__":
    app.run()
