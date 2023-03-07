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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...
@app.route("/wishlists/<wishlist_id>", methods = ["PUT"])
def update_wishlist(wishlist_id):
    """ Update a wishlist"""
    app.logger.info(f"Request to update wishlist {wishlist_id}")
    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    body = request.get_json()
    for key, value in body.items():
        setattr(wishlist, key, value)

    wishlist.update()

    return wishlist.serialize(), status.HTTP_200_OK
    