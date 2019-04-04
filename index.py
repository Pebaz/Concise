"""
[✔] Rename project
[ ] Deploy on Zeit
[ ] Map url.pebaz.com wildcard domain to Zeit
[✔] Generate new ID for URL
[✔] Save URL to database
[✔] Return ID/URL to user
[✔] Allow redirecting using IDs
"""

import sys, os, time
import requests
from flask import Flask, redirect, render_template, request, abort

ctm = lambda: int(round(time.time() * 1000))


app = Flask(__name__)
DATABASE_URL = "https://www.jsonstore.io/e9e6153838f3d04ea2843901197e19bcaf72f63a97ec0e26d88c5d1178ac22af"
cached_urls = dict()


@app.route('/', methods=['GET', 'POST'])
def shorten_url():
	"""
	Index page to turn a URL into a smaller URL.
	"""

	return "<h1>Hello World</h1>"

	print('[CONCISE][shorten_url()]')

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
	print('[CONCISE][get_url()]')

	try:
		start = ctm()

		if id in cached_urls:
			url = cached_urls[id]
		else:
			url = requests.get(f'{DATABASE_URL}/urls/{id}').json()['result']['value']
			cached_urls[id] = url

		print(f'Delay: {ctm() - start} ms')

		print(f'REDIRECTING TO: {url}')
		return redirect(url, code=302)
	except Exception as e:
		print(e)
		abort(404)
	
		
@app.route('/admin')
def admin_page():
	"""
	GET a previously-shortened URL by ID.

	POST a new URL to shorten.
	"""
	print('[CONCISE][admin_page()]')

	try:
		json = requests.get(f'{DATABASE_URL}/urls').json()['result']
		json = { i : json[i]['value'] for i in json }
		print(json)
		return render_template('admin.html', json=json)
	except Exception as e:
		print(e)
		abort(404)
		


if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	# if sys.platform == 'win32':
	# 	port = int(os.environ.get('PORT', 9001))
	# 	app.run(host='0.0.0.0', port=port)
	# else:
	# 	print(f'Serving on: 0.0.0.0:{port}')
	# 	import bjoern
	# 	bjoern.run(app, host='0.0.0.0', port=port)

	app.run(host='0.0.0.0', port=int(os.environ['PORT']))
