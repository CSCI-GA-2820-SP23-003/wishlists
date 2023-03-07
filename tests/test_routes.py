"""
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Item, Wishlist
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistsFactory, ItemsFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/wishlists"
######################################################################
#  T E S T   C A S E S
######################################################################
######################################################################
#  T E S T   WISHLIST   S E R V I C E
######################################################################


class TestWishlistService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def __create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistsFactory()
            response = self.app.post(BASE_URL, json=test_wishlist.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test order"
            )
            new_wishlist = response.get_json()
            test_wishlist.id = new_wishlist["id"]
            wishlists.append(test_wishlist)
        return wishlists

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_wishlist(self):
        """It should Read a single Wishlist"""
        # get the id of a order
        test_wishlist = self.__create_wishlists(1)[0]
        response = self.app.get(f"{BASE_URL}/{test_wishlist.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_wishlist.id)

    def test_get_wishlist_not_found(self):
        """It should not Read a Wishlist thats not found"""
        response = self.app.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])


######################################################################
#  T E S T   ITEMS   S E R V I C E
######################################################################
class TestItemService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_rename_wishlist(self):
        """It should rename the wishlist."""
        test_wishlist = WishlistsFactory()
        test_wishlist.create()
        response = self.app.put(
            f"{BASE_URL}/{test_wishlist.id}", json={"name": "Test Rename"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        renamed_wishlist = response.get_json()
        self.assertEqual(renamed_wishlist["name"], "Test Rename")

    def test_update_wishlist_not_found(self):
        """It should not Update a Wishlist who doesn't exist"""
        response = self.app.put(f"{BASE_URL}/0", json={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
