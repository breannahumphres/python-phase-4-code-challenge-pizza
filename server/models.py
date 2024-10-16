from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates = "restaurant", cascade = "all, delete-orphan")
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # add relationship
    serialize_rules = ( "-restaurant_pizzas",)
    # add serialization rules

    def to_dict(self, include_pizzas=False):
        restaurant_dict = {
            "id":self.id,
            "name": self.name,
            "address": self.address,
        }
        if include_pizzas:
            restaurant_dict["restaurant_pizzas"] = [
                rp.to_dict() for rp in self.restaurant_pizzas
                ]
        return restaurant_dict
    
    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates = "pizza", cascade = "all, delete-orphan")
    restaurants = association_proxy("restaurant_pizzas", "restaurant")
    # add relationship
    serialize_rules = ("-restaurant_pizzas",)
    # add serialization rules

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    restaurant = db.relationship("Restaurant", back_populates = "restaurant_pizzas")
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    pizza = db.relationship("Pizza", back_populates = "restaurant_pizzas")
    # add relationships
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")
    # add serialization rules
    @validates("price")
    def validate_price(self, key, value):
        if not type(value) == int:
            raise TypeError("price must be an integer")
        if not (1 <= value <= 30): 
            raise ValueError("price must be between 1 and 30")
        return value
    # add validation
    def to_dict(self, include_related=True):
        restaurant_pizza_dict = {
            "id" : self.id,
            "price": self.price,
            "pizza_id":self.pizza_id,
            "restaurant_id": self.restaurant_id,
        }
        if include_related:
            restaurant_pizza_dict["pizza"] = self.pizza.to_dict()
            restaurant_pizza_dict["restaurant"] = self.restaurant.to_dict()
        return restaurant_pizza_dict
    
    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
