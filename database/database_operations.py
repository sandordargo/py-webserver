from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc
from database_setup import Base, Restaurant, MenuItem, User


def query_single_item(session, db_object, filter_column, filter_value):
    try:
        return session.query(db_object).filter(filter_column == filter_value).one()
    except exc.NoResultFound:
        return None


def init_connection():
    engine = create_engine('sqlite:///database/restaurantmenuwithusers.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def list_all_restaurants_mock():
    session = init_connection()
    list_of_restaurants = list()
    list_of_restaurants.append('Costes')
    list_of_restaurants.append('Borkonyha')
    return list_of_restaurants


def get_restaurant(restaurant_id):
    session = init_connection()
    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    return restaurant


def get_all_restaurants():
    session = init_connection()
    query_results = session.query(Restaurant).all()
    return query_results


def insert_restaurant(restaurant_name, user_id):
    session = init_connection()
    new_restaurant = Restaurant(name=restaurant_name, user_id=user_id)
    session.add(new_restaurant)
    session.commit()


def edit_restaurant(restaurant_id, restaurant_name, user_id):
    session = init_connection()
    restaurant_to_update = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    restaurant_to_update.name = restaurant_name
    restaurant_to_update.name = user_id
    session.add(restaurant_to_update)
    session.commit()


def delete_restaurant(restaurant_id):
    session = init_connection()
    restaurant_to_delete = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    session.delete(restaurant_to_delete)
    session.commit()


def insert_menu_item(name, description, price, course, restaurant_id, user_id):
    session = init_connection()
    new_menu_item= MenuItem(name=name, description=description,
                            price=price, course=course,
                            restaurant_id=restaurant_id, user_id=user_id)
    session.add(new_menu_item)
    session.commit()


def delete_menu_item(menu_item_id):
    session = init_connection()
    menu_item_to_delete = session.query(MenuItem).filter(MenuItem.id == menu_item_id).one()
    session.delete(menu_item_to_delete)
    session.commit()


def get_menu_items_for_restaurant(i_restaurant_id=1):
    session = init_connection()
    try:
        return session.query(MenuItem).filter(MenuItem.restaurant_id == i_restaurant_id)
    except exc.NoResultFound:
        return None


def get_menu_item(item_id):
    session = init_connection()
    item = session.query(MenuItem).filter(MenuItem.id == item_id).one()
    return item


def update_menu_item(menu_id, user_id, name='', description='', price=0):
    session = init_connection()
    item_to_edit = session.query(MenuItem).filter_by(id=menu_id).one()
    item_to_edit.name = name if name else item_to_edit.name
    item_to_edit.description = description if description else item_to_edit.description
    item_to_edit.price = price if price else item_to_edit.price
    item_to_edit.user_id = user_id if user_id else item_to_edit.user_id
    session.add(item_to_edit)
    session.commit()


def add_user(user_name, email_address, picture):
    session = init_connection()
    new_user = User(name=user_name, email=email_address, picture=picture)
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email_address).one()
    return user.id


def get_user(user_id):
    session = init_connection()
    print user_id
    return query_single_item(session, User, User.id, user_id)
    # query_results = session.query(User).filter(User.id == user_id).one()
    # return query_results


def get_user_id(email):
    session = init_connection()
    try:
        query_results = session.query(User).filter(User.email == email).one()
        return query_results.id
    except exc.NoResultFound:
        return None
