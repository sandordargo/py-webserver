from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
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


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        database_operations.insert_menu_item(name=request.form['name'],
                                             description=request.form['description'],
                                             price=request.form['price'],
                                             course=request.form['course'],
                                             restaurant_id=restaurant_id)

        flash("New menu item has been created!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu_item.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',  methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        database_operations.update_menu_item(menu_id, request.form['name'],
                                             request.form['description'], request.form['price'])
        flash("Menu item has been updated!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('edit_menu_item.html', restaurant_id=restaurant_id,
                               item=database_operations.get_menu_item(menu_id))


@app.route('/restaurants/<int:restaurant_id>>/<int:menu_id>/delete/',  methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if request.method == 'POST':
        database_operations.delete_menu_item(menu_id)
        flash("Menu item has been deleted!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('delete_menu_item.html', restaurant_id=restaurant_id,
                               item=database_operations.get_menu_item(menu_id))


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurant_menu_json(restaurant_id):
    menu_items = database_operations.list_menu_items(restaurant_id)
    return jsonify(items=[item.serialize for item in menu_items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def get_menu_item_json(restaurant_id, menu_id):
    menu_item = database_operations.get_menu_item(menu_id)
    return jsonify(menu_item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)