from flask import Flask
#from database import database_operations as database_operations
from database import database_operations
app = Flask(__name__)

# Wrapping different URLs to the same page
@app.route('/')
@app.route('/menuitems')
def list_menu_items():
    menu_items = database_operations.list_menu_items()
    html_to_print = ''
    for item in menu_items:
        html_to_print += '<p>{}</br>{}</br>{}</p>'.format(item.name, item.price, item.description)
    return html_to_print

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)