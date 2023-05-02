"""
My Service

Describe what your service does here
"""

from flask import jsonify
from flask_restx import fields, reqparse, Resource
from service.common import status  # HTTP Status Codes
from service.models import Wishlist, Item

# Import Flask application
from . import app, api

# MODELS

create_item_model = api.model('WishlistItem', {
    'wishlist_id': fields.Integer(required=True, description='The Unique ID of the wishlist for the item'),
    'product_name': fields.String(required=True, description='The name of the product in the wishlist'),
    'product_id': fields.Integer(required=True, description='The ID of the product in the wishlist'),
    'item_quantity': fields.Integer(required=True, description='The quantity of the product in the wishlist')
    }
)

item_model = api.inherit(
    'ItemModel',
    create_item_model,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
    }
)


create_wishlist_model = api.model('Wishlist', {
    'name': fields.String(required=True, description='The Name of the wishlist'),
    'owner_id': fields.Integer(required=True, description='The owner id of the wishlist'),
})

wishlist_model = api.inherit(
    'WishlistModel',
    create_wishlist_model,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
        'created_at': fields.Date(readOnly=True, description='The day the wishlist was created'),
        'wishlist_items': fields.List(fields.Nested(item_model), required=False,
                                      description='The items that the wishlist contains'),
    }
)

# Query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument('name', type=str, location='args', required=False, help='List Wishlists by name')
wishlist_args.add_argument('owner_id', type=int, location='args', required=False, help='List Wishlists by Owner ID')
wishlist_args.add_argument('product_name', type=int, location='args', required=False,
                           help='List Wishlist Items by product name')

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def health():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  PATH: /wishlists/{wishlist_id}
######################################################################


@api.route("/wishlists/<int:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """Handles all routes for the wishlist model."""

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlist")
    @api.response(404, "Wishlist not found.")
    @api.marshal_list_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieves a Wishlist.
        This endpoint will return a wishlist based on its ID.
        """

        app.logger.info("Request to get wishlist with id %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Updates a Wishlist.
        This endpoint will update a Wishlist based the body that is posted.
        """
        app.logger.info("Request to update wishlist %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        wishlist.deserialize(data)
        wishlist.id = wishlist_id
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_wishlists")
    @api.response(204, "Wishlist Deleted")
    def delete(self, wishlist_id):
        """
        Deletes a Wishlist.
        This endpoint will delete a wishlist based on the ID specified in the path.
        """
        app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)

        if wishlist:
            wishlist.delete()
            app.logger.info('Wishlist with ID [%s] delete complete.', wishlist_id)
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /wishlists
######################################################################


@api.route('/wishlists', strict_slashes=False)
class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """
    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @api.doc('list_wishlists')
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """
        Lists all Wishlists.
        This endpoint will list all available Wishlists.
        """
        app.logger.info('Request to list Wishlists...')
        wishlists = []
        args = wishlist_args.parse_args()
        if args['owner_id']:
            app.logger.info('Filtering by owner id: %s', args['owner_id'])
            wishlists = Wishlist.find_by_owner_id(args['owner_id'])
        elif args['name']:
            app.logger.info('Filtering by product id: %s', args['name'])
            wishlists = Wishlist.find_by_name(args['name'])
        else:
            app.logger.info('Returning unfiltered list...')
            wishlists = Wishlist.all()

        results = [wishlist.serialize() for wishlist in wishlists]
        app.logger.info('[%s] WishlistS returned', len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW WISHLIST
    # ------------------------------------------------------------------
    @api.doc('create_wishlists')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist.
        This endpoint will create a Wishlist based on the data in the body that is posted.
        """
        app.logger.info('Request to Create a Wishlist')
        wishlist = Wishlist()
        wishlist.deserialize(api.payload)
        wishlist.create()
        location_url = api.url_for(WishlistResource, wishlist_id=wishlist.id, _external=True)
        app.logger.info('Wishlist with ID [%s] created.', wishlist.id)
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /wishlists/{wishlist_id}/clear
######################################################################


@api.route("/wishlists/<int:wishlist_id>/clear", strict_slashes=False)
@api.param("wishlist_id", "The wishlist ID")
class ClearWishlistResource(Resource):
    """ Clear action on a Wishlist """

    @api.doc("clear_wishlist")
    @api.response(204, "Wishlist Cleared.")
    @api.marshal_list_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Clears a Wishlist of all its Items.
        This endpoint will remove all items in a Wishlist and make it unavailable.
        """
        app.logger.info("Request to clear wishlist %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f'Wishlist with id {wishlist_id} was not found.')

        while wishlist.wishlist_items:
            item = wishlist.wishlist_items[0]
            wishlist.wishlist_items.remove(item)
            item.delete()

        app.logger.info(f"Wishlist {wishlist_id} cleared.")
        return "", status.HTTP_204_NO_CONTENT

######################################################################
# Item handling
######################################################################

######################################################################
#  PATH: /wishlists/{wishlist_id}/items/{item_id}
######################################################################


@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The Wishlist Item identifier")
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Wishlist Item
    GET /wishlists/{wishlist_id}/items/{item_id} - Returns a Wishlist Item with the id
    PUT /wishlists/{wishlist_id}/items/{item_id} - Update a Wishlist Item with the id
    DELETE /wishlists/{wishlist_id}/items/{item_id} -  Deletes a Wishlist Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.doc("get_wishlist_items")
    @api.response(404, "Wishlist Item not found")
    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Retrieves an Item from a Wishlist.
        This endpoint will return a wishlist item based on its ID.
        """
        app.logger.info('Request to retrieve an Item %s from Wishlist with id: %s', item_id, wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = Item.find_by_wishlist_and_item_id(wishlist_id, item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )
        app.logger.info('Returning wishlist item: %s', item.product_name)
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_wishlist_items")
    @api.response(204, "Wishlist Item Deleted")
    def delete(self, wishlist_id, item_id):
        """
        Deletes an Item from a Wishlist.
        This endpoint will delete a Wishlist Item based on the ID specified in the path.
        """

        app.logger.info('Request to delete item with wishlist_id [%s] and item_id [%s] ...', item_id, wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")
        item = Item.find(item_id)
        if item:
            item.delete()
            app.logger.info('Item with ID [%s] and wishlist ID [%s] is deleted.', item_id, wishlist_id)

        return "", status.HTTP_204_NO_CONTENT

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.doc("update_item")
    @api.response(404, 'Wishlist not found')
    @api.response(400, 'The posted Wishlist data was not valid')
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """
        Updates an Item in a Wishlist.
        This endpoint will update a Wishlist Item based on the body that is posted.
        """

        app.logger.info("Request to update product %d in wishlist %d", wishlist_id, item_id)
        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")

        wishlist_products = Item.find_by_wishlist_and_item_id(wishlist_id, item_id)

        if not wishlist_products:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        data = api.payload
        wishlist_products.deserialize(data)
        wishlist_products.id = item_id
        wishlist_products.wishlist_id = wishlist_id
        wishlist_products.update()

        app.logger.info('Item with wishlist_id [%s] and item_id [%s] updated.', wishlist.id, wishlist_products.id)
        return wishlist_products.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{wishlist_id}/items
######################################################################


@api.route('/wishlists/<int:wishlist_id>/items', strict_slashes=False)
@api.param('wishlist_id', 'The Wishlist identifier')
class ItemCollection(Resource):
    """
    Handles all interactions with collections of Wishlist Items
    """
    # ------------------------------------------------------------------
    # LIST ALL ITEMS FOR A WISHLIST
    # ------------------------------------------------------------------
    @api.doc('list_wishlist_items')
    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """
        Lists all Items in a Wishlist.
        This endpoint lists all Items in a Wishlist.
        """
        app.logger.info('Request to list Items for Wishlist with id: %s', wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")

        results = [item.serialize() for item in wishlist.wishlist_items]
        app.logger.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM TO A WISHLIST
    # ------------------------------------------------------------------
    @api.doc('create_wishlist_items')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Create an Item in a Wishlist.
        This endpoint will add a new item to a wishlist.
        """
        app.logger.info('Request to create an Item for Wishlist with id: %s', wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")

        item = Item()
        item.deserialize(api.payload)
        item.wishlist_id = wishlist_id
        item.create()

        location_url = api.url_for(ItemResource, wishlist_id=wishlist.id, item_id=item.id, _external=True)
        app.logger.info('Item with ID [%s] created for wishlist: [%s].', item.id, wishlist.id)
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
