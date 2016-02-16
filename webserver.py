from __future__ import print_function
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import database.database_operations as database_operations
from urlparse import parse_qs
import re

class WebServerHandler(BaseHTTPRequestHandler):


    def do_GET(self):
        edit_pattern = re.compile(r'/restaurants/(?P<id>(?:\d+))/edit')
        edit_match = edit_pattern.search(self.path)

        delete_pattern = re.compile(r'/restaurants/(?P<id>(?:\d+))/delete')
        delete_match = delete_pattern.search(self.path)

        if self.path.endswith("/hello"):
            self.set_successful_response(200)
            message = ""
            message += "<html><body>"
            message += "<h1>Hello!</h1>"
            message += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                <h2>What would you like me to say?</h2><input name="message" type="text" >
                <input type="submit" value="Submit"> </form>'''
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        elif self.path.endswith("/hola"):
            self.set_successful_response(200)
            message = ""
            message += "<html><body> &#161 Hola ! <a href='/hello'>Back to hello</a></body></html>"
            self.wfile.write(message)
            print(message)
            return

        elif self.path.endswith('/restaurants'):
            self.set_successful_response(200)
            message = self.get_all_restos()
            message += "</br></br><a href='/restaurants/new'>Create a new restaurant</a>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        elif edit_match:
            self.set_successful_response(200)
            message = ""
            message += "<html><body>"
            message += "<h1>Edit restaurant!</h1>"
            message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/edit'>
                <h2>Please rename restaurant</h2><input name="new_restaurant_name" type="text" placeholder="{}" >
                <input type="submit" value="Submit"> </form>'''.format(edit_match.group(1), "blabla")
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        elif delete_match:
            self.set_successful_response(200)
            message = ""
            message += "<html><body>"
            message += "<h1>Do you want to delete the restaurant?</h1>"
            message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/delete'>
                       <input type="submit" value="Submit"> </form>'''.format(delete_match.group(1))
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        elif self.path.endswith('/restaurants/new'):
            self.set_successful_response(200)
            message = ""
            message += "<html><body>"
            message += "<h1>Add new restaurant!</h1>"
            message += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                <h2>What is the name of the new restaurant?</h2><input name="new_restaurant_name" type="text" >
                <input type="submit" value="Submit"> </form>'''
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return
        else:
            self.send_error(404, 'File Not Found: {}'.format(self.path))

    def do_POST(self):
        try:

            edit_pattern = re.compile(r'/restaurants/(?P<id>(?:\d+))/edit')
            edit_match = edit_pattern.search(self.path)

            delete_pattern = re.compile(r'/restaurants/(?P<id>(?:\d+))/delete')
            delete_match = delete_pattern.search(self.path)

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            output = ""
            if self.path.endswith('/restaurants'):
                print('resto')
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                if self.path.endswith('/restaurants/new'):
                    self.set_successful_response(301, '/restaurants')
                    print('resto')
                    messagecontent = fields.get('new_restaurant_name')
                    print(messagecontent)
                    database_operations.insert_restaurant(str(messagecontent[0]))
                elif self.path.endswith('/hello'):
                    self.set_successful_response(301)
                    messagecontent = fields.get('message')
                    output += "<html><body>"
                    output += " <h2> Okay, how about this: </h2>"
                    output += "<h1> {} </h1>".format(messagecontent[0])
                    output += '''<form method='POST' enctype='multipart/form-data' action='/hello'>
                        <h2>What would you like me to say?</h2>
                        <input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                    output += "</body></html>"
                elif edit_match:
                    self.set_successful_response(301, '/restaurants')
                    print('resto changed')
                    messagecontent = fields.get('new_restaurant_name')
                    print(messagecontent)
                    database_operations.edit_restaurant(edit_match.group(1), str(messagecontent[0]))
                elif delete_match:
                    self.set_successful_response(301, '/restaurants')
                    print('resto deleted')
                    database_operations.delete_restaurant(delete_match.group(1))


            self.wfile.write(output)
            print(output)
        except:
            pass


    def set_successful_response(self, status_id, location=None):
        self.send_response(status_id)
        self.send_header('Content-type', 'text/html')
        if location:
            self.send_header('Location', location)
        self.end_headers()

    def get_all_restos(self):
        message = ''
        message += '<html><body> List of all restaurants: </body></html>'
        for restaurant in database_operations.list_all_restaurants():
            message += '''<p>{} <a href='restaurants/{}/edit'>Edit</a> <a href='restaurants/{}/delete'>Delete</a></p>'''.format(restaurant.name, restaurant.id, restaurant.id)
        return message


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print('Web server is running on port {}'.format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()
        raise


if __name__ == '__main__':
    main()
