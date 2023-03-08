"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Wishlist, Item

# Import Flask application
from . import app


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")

    return (
        jsonify(
            name="Wishlists REST API Service",
            version="1.0",
            paths=url_for("list_wishlists", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# GETs Wishlist with a specific wishlist_id
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist
    This endpoint will return a Wishlist based on it's id
    """    

    app.logger.info("Request for Wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")

    items = [item.serialize() for item in wishlist.wishlist_items]    
    app.logger.info("Returning %d items", len(items))
    return jsonify(items), status.HTTP_200_OK

# LIST wishlist
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """
    List all the wishlists
    """    
    app.logger.info("Request for listing all the wishlists")
    wishlists = Wishlist.all()
    results = [wishlist.serialize() for wishlist in wishlists]
    app.logger.info("Returning %d wishlists", len(results))
    return jsonify(results), status.HTTP_200_OK

# Add Wishlist
@app.route("/wishlists", methods=["POST"])
def create_wishlist():
    """
    Creates a Wishlist
    This endpoint will create a wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create a wishlist")
    check_content_type("application/json")
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()
    message = wishlist.serialize()
    location_url = url_for("get_wishlists", wishlist_id=wishlist.id, _external=True)

    app.logger.info("Wishlist with ID [%s] created.", wishlist.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}



# Add an Item to a Wishlist
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_item(wishlist_id):
    """
    Create an item on a wishlist
    This endpoint will add an item to a wishlist
    """
    app.logger.info("Request to create an Item for Wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the wishlist
    wishlist.wishlist_items.append(item)
    wishlist.update()

    # Prepare a message to return
    message = item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)

# delete Wishlist
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """
    Deletes a Wishlist
    This endpoint will delete a Wishlist based on it's id
    """
    app.logger.info("Request to delete wishlist with id")
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
        app.logger.info("Wishlist with ID [%s] delete complete.", wishlist.id)
    return jsonify(wishlist.serialize()), status.HTTP_200_OK

# delete Item from Wishlist
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(wishlist_id, item_id):
    """
    Deletes a Item from Wishlist
    This endpoint will delete an Item from Wishlist based on their id
    """
    app.logger.info("Request to delete item from wishlist")
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )
    item = Item.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"item with id '{item_id}' was not found.",
        )
    if wishlist_id != item.wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND, 
            f"Wishlist with id '{wishlist_id}' do not have it with id '{item_id}'"
        )
    item.delete()
    app.logger.info("Item with ID [%s] deleted from wishlist with ID [%s]", item_id, wishlist_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )