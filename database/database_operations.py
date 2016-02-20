from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


def init_connection():
    engine = create_engine('sqlite:///database/restaurantmenu.db')
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


def insert_restaurant(restaurant_name):
    session = init_connection()
    new_restaurant = Restaurant(name=restaurant_name)
    session.add(new_restaurant)
    session.commit()


def edit_restaurant(restaurant_id, restaurant_name):
    session = init_connection()
    restaurant_to_update = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    restaurant_to_update.name = restaurant_name
    session.add(restaurant_to_update)
    session.commit()


def delete_restaurant(restaurant_id):
    session = init_connection()
    restaurant_to_delete = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    session.delete(restaurant_to_delete)
    session.commit()


def insert_menu_item(name, description, price, course, restaurant_id):
    session = init_connection()
    new_menu_item= MenuItem(name=name, description=description,
                            price=price, course=course, restaurant_id=restaurant_id)
    session.add(new_menu_item)
    session.commit()


def delete_menu_item(menu_item_id):
    session = init_connection()
    menu_item_to_delete = session.query(MenuItem).filter(MenuItem.id == menu_item_id).one()
    session.delete(menu_item_to_delete)
    session.commit()


def get_menu_items_for_restaurant(i_restaurant_id=1):
    session = init_connection()
    query_results = session.query(MenuItem).filter(MenuItem.restaurant_id == i_restaurant_id)
    return query_results


def get_menu_item(item_id):
    session = init_connection()
    item = session.query(MenuItem).filter(MenuItem.id == item_id).one()
    return item


def update_menu_item(menu_id, name='', description='', price=0):
    session = init_connection()
    item_to_edit = session.query(MenuItem).filter_by(id=menu_id).one()
    item_to_edit.name = name if name else item_to_edit.name
    item_to_edit.description = description if description else item_to_edit.description
    item_to_edit.price = price if price else item_to_edit.price
    session.add(item_to_edit)
    session.commit()

