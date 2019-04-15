"""
[✔] Rename project
[ ] Deploy on Zeit
[ ] Map url.pebaz.com wildcard domain to Zeit
[✔] Generate new ID for URL
[✔] Save URL to database
[✔] Return ID/URL to user
[✔] Allow redirecting using IDs
"""

import sys, os, time, io, traceback
import requests
from flask import Flask, redirect, render_template, request, abort, send_file
import qrcode

ctm = lambda: int(round(time.time() * 1000))


app = Flask(__name__)
DATABASE_URL = "https://www.jsonstore.io/e9e6153838f3d04ea2843901197e19bcaf72f63a97ec0e26d88c5d1178ac22af"
cached_urls = dict()


@app.route('/', methods=['GET', 'POST'])
def shorten_url():
	"""
	Index page to turn a URL into a smaller URL.
	"""

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
	print(f'[CONCISE][get_url({id})]')

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
		traceback.print_exc()
		abort(404)


@app.route('/qr/<id>')
def get_qr(id):
	"""
	Generate a QR code image for a given URL id.
	"""
	print(f'[CONCISE][get_qr({id})]')

	try:
		# Generate the QR code and send it as a file
		start = ctm()
		url = f'https://pbz-url.herokuapp.com/{id}'
		qr = qrcode.make(url, box_size=5, border=2)
		in_mem_file = io.BytesIO()
		qr.save(in_mem_file, 'JPEG', quality=100)
		in_mem_file.seek(0)

		print(f'Delay: {ctm() - start} ms')

		return send_file(in_mem_file, mimetype='image/jpeg')

	except Exception as e:
		traceback.print_exc()
		abort(404)
		

@app.route('/admin')
def admin_page():
	"""
	GET a previously-shortened URL by ID.

	POST a new URL to shorten.
	"""
	print('[CONCISE][admin_page()]')

	try:
		try:
			json = requests.get(f'{DATABASE_URL}/urls').json()['result']
			json = { i : json[i]['value'] for i in json if i != 'zero' }
		except:
			json = dict()
		return render_template('admin.html', json=json)
	except Exception as e:
		traceback.print_exc()
		abort(404)
		

@app.route('/clearcache')
def clear_cache():
	cached_urls.clear()
	return ""


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 9001))

	if sys.platform == 'win32':
		app.run(host='0.0.0.0', port=port)
	else:
		import bjoern
		bjoern.run(app, host='0.0.0.0', port=port)

	#app.run(host='0.0.0.0', port=int(os.environ['PORT']))
