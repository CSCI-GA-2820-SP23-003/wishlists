"""
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import db
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistsFactory, ItemsFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/wishlists"
######################################################################
#  T E S T   C A S E S
######################################################################
######################################################################
#  T E S T   WISHLIST   S E R V I C E
######################################################################


class TestWishlistService(TestCase):
    # pylint: disable=too-many-public-methods
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
                response.status_code, status.HTTP_201_CREATED, "Could not create test wishlist"
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

    def test_health(self):
        """It should test health endpoint"""
        resp = self.app.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "Healthy")

    def test_get_wishlist(self):
        """It should Read a single Wishlist"""

        # Get the ID of a wishlist
        test_wishlist = self.__create_wishlists(1)[0]
        response = self.app.get(f"{BASE_URL}/{test_wishlist.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.get_json()
        self.assertEqual(result["id"], test_wishlist.id)

    def test_get_wishlist_not_found(self):
        """It should not Read a Wishlist thats not found"""

        # Read a wishlist which is not yet present
        response = self.app.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_wishlist(self):
        """It should rename the wishlist."""
        test_wishlist = WishlistsFactory()
        response = self.app.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_wishlist = response.get_json()
        new_wishlist["name"] = "new name"
        new_wishlist["owner_id"] = 5
        response = self.app.put(
            f"{BASE_URL}/{new_wishlist['id']}", json=new_wishlist
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_wishlist = response.get_json()
        self.assertEqual(updated_wishlist["name"], "new name")
        self.assertEqual(updated_wishlist["owner_id"], 5)

    def test_update_wishlist_not_found(self):
        """It should not Update a Wishlist who doesn't exist"""
        test_wishlist = WishlistsFactory()
        response = self.app.put(f"{BASE_URL}/{test_wishlist.id}", json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""

        test_wishlist = WishlistsFactory()
        logging.debug("Test Wishlist: %s", test_wishlist.serialize())
        response = self.app.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = response.get_json()
        self.assertEqual(new_wishlist["id"], 1)
        self.assertEqual(new_wishlist["name"], test_wishlist.name)
        self.assertEqual(new_wishlist["owner_id"], test_wishlist.owner_id)

    def test_create_wishlists_with_no_data(self):
        """It should not Create an Wishlist with missing data"""
        response = self.app.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlists_no_content_type(self):
        """It should not Create a Wishlist with no content type"""
        response = self.app.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlists_bad_content_type(self):
        """It should not Create an Wishlist with incorrect content type"""
        response = self.app.post(
            BASE_URL, headers={"Content-Type": "application/octet-stream"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_wishlists(self):
        """ It should list all wishlists"""
        self.__create_wishlists(10)
        response = self.app.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 10)

    def test_list_wishlist_with_owner_id(self):
        """ It should list wishlist with certain owner_id"""
        wishlist = self.__create_wishlists(1)[0]
        owner_id = wishlist.owner_id
        response = self.app.get(f"{BASE_URL}?owner_id={owner_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.get_json()[0]
        self.assertEqual(items["id"], wishlist.id)
        self.assertEqual(items["name"], wishlist.name)
        self.assertEqual(items["owner_id"], wishlist.owner_id)

    def test_list_wishlists_with_wishlist_id(self):
        """ It should list wishlist with certain Id"""
        wishlist = self.__create_wishlists(1)[0]
        wishlist_id = wishlist.id
        response = self.app.get(f"{BASE_URL}?id={wishlist_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.get_json()[0]
        self.assertEqual(items["id"], wishlist.id)
        self.assertEqual(items["name"], wishlist.name)
        self.assertEqual(items["owner_id"], wishlist.owner_id)

    def test_list_wishlist_wih_names(self):
        """It should list a wishlist by name"""
        wishlist = self.__create_wishlists(2)[0]
        resp = self.app.get(f'{BASE_URL}?name={wishlist.name}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        items = resp.get_json()[0]
        self.assertEqual(items["id"], wishlist.id)
        self.assertEqual(items["name"], wishlist.name)
        self.assertEqual(items["owner_id"], wishlist.owner_id)

    def test_delete_wishlist(self):
        """It should Delete a Wishlist"""
        # create 1 wishlist with id
        wishlist = self.__create_wishlists(1)[0]
        # delete wishlist with its id
        response = self.app.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the wishlist is deleted
        response = self.app.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  P L A C E   T E S T   C A S E S  F O R  ITEM   H E R E
    ######################################################################

    def test_add_item(self):
        """It should Add an item to a wishlist"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        # add item
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["product_name"], item.product_name)
        self.assertEqual(data["item_quantity"], item.item_quantity)

    def test_add_item_no_wishlist(self):
        """It should not Create a item when wishlist can't be found"""
        wishlist_id = 5
        item = ItemsFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item(self):
        """It should Get an item from a Wishlist"""
        # create an item
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item_id = data["id"]

        # retrieve the item back
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["item_quantity"], item.item_quantity)
        self.assertEqual(data["product_name"], item.product_name)

    def test_get_item_incorrect_wishlist(self):
        """It should not Get an item by id if wishlist exists"""
        # create an item
        wishlists = self.__create_wishlists(2)

        item_0 = ItemsFactory()
        response = self.app.post(
            f"{BASE_URL}/{wishlists[0].id}/items",
            json=item_0.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_wishlist_0 = response.get_json()["id"]

        item_1 = ItemsFactory()
        response = self.app.post(
            f"{BASE_URL}/{wishlists[1].id}/items",
            json=item_1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_wishlist_1 = response.get_json()["id"]

        temp_wishlist_id = 199
        response = self.app.get(
            f"{BASE_URL}/{temp_wishlist_id}/items/{item_id_wishlist_1}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(f"Wishlist with id '{temp_wishlist_id}' was not found.", response.get_json()["message"])
        # self.assertEqual(response.get_json()["message"],
        #                  f"404 Not Found: Wishlist with id '{temp_wishlist_id}' was not found.")

        # retrieve the items with wrong wishlist id
        response = self.app.get(
            f"{BASE_URL}/{wishlists[0].id}/items/{item_id_wishlist_1}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.get_json()["message"], f"404 Not Found: Item with id '{item_id_wishlist_1}' was not found.")
        self.assertIn(f"Item with id '{item_id_wishlist_1}' was not found.", response.get_json()["message"])


        response = self.app.get(
            f"{BASE_URL}/{wishlists[1].id}/items/{item_id_wishlist_0}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.get_json()["message"], f"404 Not Found: Item with id '{item_id_wishlist_0}' was not found.")
        self.assertIn(f"Item with id '{item_id_wishlist_0}' was not found.", response.get_json()["message"])

        # Now retrieve them with correct wishlist id
        response = self.app.get(f"{BASE_URL}/{wishlists[0].id}/items/{item_id_wishlist_0}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.app.get(f"{BASE_URL}/{wishlists[1].id}/items/{item_id_wishlist_1}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_items_list(self):
        """It should Get a list of Items"""
        wishlist = self.__create_wishlists(1)[0]
        item_list = ItemsFactory.create_batch(2)
        item_one_response = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(item_one_response.status_code, status.HTTP_201_CREATED)
        item_two_response = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[1].serialize(),
            content_type="application/json"
        )
        self.assertEqual(item_two_response.status_code, status.HTTP_201_CREATED)
        resp = self.app.get(f"{BASE_URL}/{wishlist.id}/items", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_item_by_name(self):
        """It should Get a item by the item name"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory.create()
        self.app.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item.serialize(),
            content_type="application/json"
        )
        resp = self.app.get(f"{BASE_URL}/{wishlist.id}/items?name={item.product_name}", content_type="application/json")
        self.assertEqual(resp.get_json()[0]["product_name"], item.product_name)

    def test_get_items_list_no_wishlist_id(self):
        """It should not Get a list of Items when a wishlist is not found"""
        response = self.app.get(f"{BASE_URL}/0/items", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_delete_item_wishlist(self):
        """It should delete an item from wishlist"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        response = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        item_id = data["id"]

        # make sure item exists before delete
        response = self.app.get(f"{BASE_URL}/{wishlist.id}/items", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.get_json()[0]
        self.assertEqual(items['id'], item_id)

        # delete the item
        response = self.app.delete(f"{BASE_URL}/{wishlist.id}/items/{item_id}",)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # make sure item does not exist after delete
        response = self.app.get(f"{BASE_URL}/{wishlist.id}/items", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.get_json()
        self.assertEqual(len(items), 0)

    def test_delete_item_nonexistent_wishlist(self):
        """It should not delete a item when wishlist can't be find"""
        wishlist_id, item_id = 3, 10
        response = self.app.delete(f"{BASE_URL}/{wishlist_id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        # self.assertEqual(data["message"], f"404 Not Found: Wishlist with id '{wishlist_id}' was not found.")
        self.assertIn(f"Wishlist with id '{wishlist_id}' was not found.", data["message"])

    def test_update_item(self):
        """It should Update an item"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        # add item
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        item.id = data["id"]
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["item_quantity"], item.item_quantity)
        self.assertEqual(data["product_name"], item.product_name)
        # update item wishlist id
        updated_item = ItemsFactory()
        updated_item.wishlist_id = item.wishlist_id
        updated_item.id = item.id
        resp = self.app.put(
            f"{BASE_URL}/{wishlist.id}/items/{item.id}",
            json=updated_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_item = resp.get_json()
        self.assertIsNotNone(resp_item["id"])
        self.assertEqual(resp_item["wishlist_id"], wishlist.id)
        self.assertEqual(resp_item["product_id"], updated_item.product_id)
        self.assertEqual(resp_item["item_quantity"], updated_item.item_quantity)
        self.assertEqual(resp_item["product_name"], updated_item.product_name)

    def test_update_item_not_found(self):
        """It should not Update an item given wrong wishlist id and non-existent item"""
        wishlist = self.__create_wishlists(1)[0]
        item_id = 4
        # update non-existent item id
        item = ItemsFactory()
        response = self.app.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn(f"Item with id '{item_id}' was not found.", data["message"])
        # self.assertEqual(data["message"], f"404 Not Found: Item with id '{item_id}' was not found.")

    def test_update_item_nonexistent_wishlist(self):
        """It should not Update an item given wrong wishlist id"""
        wishlist = self.__create_wishlists(1)[0]
        item = ItemsFactory()
        item.wishlist_id = wishlist.id

        # add item
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update item with wrong wishlist id
        updated_item = ItemsFactory()
        updated_item.wishlist_id = item.wishlist_id + 123
        updated_item.id = item.id
        resp = self.app.put(
            f"{BASE_URL}/{updated_item.wishlist_id}/items/{updated_item.id}",
            json=updated_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertIn(f"Wishlist with id '{updated_item.wishlist_id}' was not found.", data["message"])
        # self.assertEqual(data["message"], f"404 Not Found: Wishlist with id '{updated_item.wishlist_id}' was not found.")

    def test_clear_items_of_wishlist(self):
        """It should clear the existing wishlist and make wishlist empty"""
        wishlist = self.__create_wishlists(1)[0]

        # create a wishlist
        resp = self.app.post(
            f"{BASE_URL}",
            json=wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item = ItemsFactory()
        item.wishlist_id = wishlist.id

        # add item to the wishlist
        resp = self.app.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # retrieve the wishlist
        resp = self.app.get(
            f"{BASE_URL}/{wishlist.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        data = resp.get_json()

        # make sure wishlist is non empty
        self.assertEqual(len(data['wishlist_items']), 1)
        resp = self.app.put(
            f"{BASE_URL}/4/clear",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # clear the wishlist and make wishlist empty
        resp = self.app.put(
            f"{BASE_URL}/{wishlist.id}/clear",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # check if wishlist is empty or not
        self.assertEqual(len(wishlist.wishlist_items), 0)
