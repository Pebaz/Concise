"""
[ ] Rename project
[ ] Deploy on Zeit
[ ] Map url.pebaz.com wildcard domain to Zeit
[✔] Generate new ID for URL
[✔] Save URL to database
[✔] Return ID/URL to user
[✔] Allow redirecting using IDs
"""

import os
import requests
from flask import Flask, redirect, render_template, request, abort

app = Flask(__name__)
DATABASE_URL = "https://www.jsonstore.io/e9e6153838f3d04ea2843901197e19bcaf72f63a97ec0e26d88c5d1178ac22af"


@app.route('/', methods=['GET', 'POST'])
def shorten_url():
	"""
	Index page to turn a URL into a smaller URL.
	"""

	if request.method == 'GET':
		return render_template('index.html')

	elif request.method == 'POST':
		data = request.get_json()
		the_url = data["the-url"]
		print(f'Going to shorten: {the_url}')

		# Generate new ID
		num_urls = requests.get(f'{DATABASE_URL}/count').json()['result']['value']
		new_id = num_urls + 1
		requests.put(f'{DATABASE_URL}/count', json={ 'value' : new_id })
		new_id = hex(new_id)[2:]

		print(f'Got new ID: {new_id}')

		# Store the URL
		requests.post(f'{DATABASE_URL}/urls/{new_id}', json={ 'value' : the_url })

		# Return the ID

		return f'{{"result":"ok", "urlid":"{new_id}"}}'


@app.route('/<id>')
def get_url(id):
	"""
	GET a previously-shortened URL by ID.

	POST a new URL to shorten.
	"""
	try:
		url = requests.get(f'{DATABASE_URL}/urls/{id}').json()['result']['value']
		print(f'REDIRECTING TO: {url}')
		return redirect(url, code=302)
	except:
		abort(404)
	
		
		

		


if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 9000))
	app.run(host='0.0.0.0', port=port)
