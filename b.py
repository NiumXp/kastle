import http.client

c = http.client.HTTPConnection("localhost", 3000)
c.connect()
c.request('GET', '/')
print(c.getresponse().read())
