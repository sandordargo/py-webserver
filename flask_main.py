from flask import Flask, render_template
#from database import database_operations as database_operations
from database import database_operations
app = Flask(__name__)

# Wrapping different URLs to the same page
@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def list_menu_items(restaurant_id):
    menu_items = database_operations.list_menu_items(restaurant_id)
    html_to_print = ''
    return render_template('menu.html',
                           restaurant=database_operations.get_restaurant(restaurant_id),
                           items=menu_items)
    for item in menu_items:
        html_to_print += '<p>{}</br>{}</br>{}</p>'.format(item.name, item.price, item.description)
    return html_to_print

@app.route('/restaurants/<int:restaurant_id>/new/')
def newMenuItem(restaurant_id):
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>>/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)