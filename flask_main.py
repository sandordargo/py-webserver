from flask import Flask, render_template
from database import database_operations
app = Flask(__name__)

# Wrapping different URLs to the same page
@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def list_menu_items(restaurant_id):
    menu_items = database_operations.list_menu_items(restaurant_id)
    return render_template('menu.html',
                           restaurant=database_operations.get_restaurant(restaurant_id),
                           items=menu_items)

@app.route('/restaurants/<int:restaurant_id>/new/')
def newMenuItem(restaurant_id):
    return "page to create a new menu item. Task 1 complete!"

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

@app.route('/restaurants/<int:restaurant_id>>/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)