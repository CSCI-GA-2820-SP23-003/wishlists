"""
Models for Wishlists and Items

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask import Flask

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Wishlists.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Wishlists(db.Model):
    """
    Class that represents a Wishlist
    """

    app = None

    # Table Schema
    wishlist_id = db.Column(db.Integer, primary_key=True)
    wishlist_name = db.Column(db.String(63), nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f"<Wishlist {self.wishlist_name} id=[{self.wishlist_id}]>"

    def create(self):
        """
        Creates a Wishlist to the database
        """
        logger.info("Creating %s", self.wishlist_name)
        self.wishlist_id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Saving %s", self.wishlist_name)
        if not self.wishlist_id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        logger.info("Deleting %s", self.wishlist_name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Wishlist into a dictionary """
        return {"wishlist_id": self.wishlist_id,
                "wishlist_name": self.wishlist_name,
                "owner_id": self.owner_id,
                "created_at": self.created_at}

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_name = data["wishlist_name"]
            if isinstance(data["owner_id"], int):
                self.owner_id = data["owner_id"]
            else:
                raise DataValidationError(
                    "Invalid type for integer [owner_id]: "
                    + str(type(data["owner_id"])))
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Wishlists in the database """
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id):
        """ Finds a Wishlist by it's ID """
        logger.info("Processing lookup for id %s ...", wishlist_id)
        return cls.query.get(wishlist_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.wishlist_name == name)

    @classmethod
    def find_by_owner_id(cls, owner_id):
        """Returns all wishlists with the given owner id
        Args:
            name (string): the name of the WishlistsModels you want to match
        """
        logger.info("Processing owner id query for %s ...", str(owner_id))
        return cls.query.filter(cls.owner_id == owner_id)

    @classmethod
    def find_or_404(cls, wishlist_id):
        """ Finds a wishlist item by it's ID """
        logger.info("Processing lookup or 404 for id %s ...", wishlist_id)
        return cls.query.get_or_404(wishlist_id)
