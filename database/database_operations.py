from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


def init_connection():
    engine = create_engine('sqlite:///database/restaurantmenu.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def list_all_restaurants_mock():
    session = init_connection()
    list_of_restaurants = list()
    list_of_restaurants.append('Costes')
    list_of_restaurants.append('Borkonyha')
    return list_of_restaurants


def list_all_restaurants():
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


def list_menu_items(i_restaurant_id=1):
    session = init_connection()
    query_results = session.query(MenuItem).filter(MenuItem.restaurant_id == i_restaurant_id)
    return query_results


def get_restaurant(restaurant_id):
    session = init_connection()
    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one()
    return restaurant

