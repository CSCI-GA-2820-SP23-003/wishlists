$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_owner_id").val(res.owner_id);
    }

    // Updates the form with data from the Wishlist Item response
    function update_form_data_item(res) {
        $("#wishlist_id").val(res.wishlist_id);
        $("#item_id").val(res.id);
        $("#product_name").val(res.product_name);
        $("#product_id").val(res.product_id);
        $("#item_quantity").val(res.item_quantity);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_id").val("");
        $("#wishlist_name").val("");
        $("#owner_id").val("");
        $("product_name").val("");
        $("item_quantity").val("");
        $("product_id").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let owner_id = $("#owner_id").val();

        let data = {
            "name": name,
            "owner_id": parseInt(owner_id),
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // Buttons for Wishlist Items

    // ****************************************
    // Add Item to a Wishlist
    // ****************************************

    $("#create-item-btn").click(function () {

        console.log("Hello")
        let id = $("#item_id").val();
        let wishlist_id = $("#wishlist_id").val();
        let name = $("#product_name").val();
        let product_id = $("#product_id").val();
        let item_quantity;
        if( ($("#item_quantity").val()) == ""){
            item_quantity = 1;
        } else{
            item_quantity = $("#item_quantity").val();
        }
        
        let data = {
            "id": null,
            "product_name": name,
            "product_id": parseInt(product_id),
            "item_quantity": parseInt(item_quantity),
            "wishlist_id": parseInt(wishlist_id),
        };

        console.log(data);

        $("#flash_message").empty();
        console.log(wishlist_id);
        let ajax = $.ajax({
            type: "POST",
            url: `/wishlists/${wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data_item(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

})
