from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session as login_session
import random
import string
from database import database_operations


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Create a state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    if not database_operations.get_user_id(data['email']):
        print data['email']
        login_session['user_id'] = database_operations.add_user(user_name=data['name'],
                                                                email_address=data['email'],
                                                                picture=data['picture'])
    else:
        login_session['user_id'] = database_operations.get_user_id(data['email'])
    login_session['access_token'] = credentials.access_token

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    #access_token = credentials.access_token
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


# Wrapping different URLs to the same page
@app.route('/')
@app.route('/restaurants/')
def list_restaurants():
    return render_template('restaurants_list.html',
                           restaurants=database_operations.get_all_restaurants())


@app.route('/restaurants/<int:restaurant_id>/edit/',  methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        database_operations.update_restaurant(restaurant_id=restaurant_id,
                                              restaurant_name=request.form['name'],
                                              user_id=login_session['user_id'])
        flash("Restaurant has been updated!")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('edit_restaurant.html', item=database_operations.get_restaurant(restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/delete/',  methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        database_operations.delete_restaurant(restaurant_id)
        flash("Restaurant item has been deleted!")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('delete_restaurant.html', restaurant_id=restaurant_id,
                               item=database_operations.get_restaurant(restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/')
def list_menu_items(restaurant_id):
    creator = database_operations.get_user(restaurant_id)
    if creator.id == login_session['user_id']:
        print 'private'
        return render_template('menu.html',
                               restaurant=database_operations.get_restaurant(restaurant_id),
                               items=database_operations.get_menu_items_for_restaurant(restaurant_id))
    else:
        print 'public'
        return render_template('public_menu.html',
                               items = database_operations.get_menu_items_for_restaurant(restaurant_id),
                               restaurant = database_operations.get_restaurant(restaurant_id),
                               creator= creator)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def add_new_restaurant():
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        database_operations.insert_restaurant(restaurant_name=request.form['name'],
                                              user_id=login_session['user_id'])
        flash("New restaurant has been created!")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('new_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def add_new_menu_item(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        database_operations.insert_menu_item(name=request.form['name'],
                                             description=request.form['description'],
                                             price=request.form['price'],
                                             course=request.form['course'],
                                             restaurant_id=restaurant_id,
                                             user_id=login_session['user_id'])
        flash("New menu item has been created!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('new_menu_item.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',  methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if database_operations.get_user(restaurant_id).id != login_session['user_id']:
        flash("You don't have the permission to edit this menu item")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    if request.method == 'POST':
        database_operations.update_menu_item(menu_id=menu_id,
                                             name=request.form['name'],
                                             description=request.form['description'],
                                             price=request.form['price'],
                                             user_id=login_session['user_id'])
        flash("Menu item has been updated!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('edit_menu_item.html', restaurant_id=restaurant_id,
                               item=database_operations.get_menu_item(menu_id))


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',  methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect(url_for('show_login'))
    if database_operations.get_user(restaurant_id).id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item');} </script>" \
               "<body onload='myFunction()'>"
    if request.method == 'POST':
        database_operations.delete_menu_item(menu_id)
        flash("Menu item has been deleted!")
        return redirect(url_for('list_menu_items', restaurant_id=restaurant_id))
    else:
        return render_template('delete_menu_item.html', restaurant_id=restaurant_id,
                               item=database_operations.get_menu_item(menu_id))


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurant_menu_json(restaurant_id):
    menu_items = database_operations.get_menu_items_for_restaurant(restaurant_id)
    return jsonify(items=[item.serialize for item in menu_items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def get_menu_item_json(restaurant_id, menu_id):
    menu_item = database_operations.get_menu_item(menu_id)
    return jsonify(menu_item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)