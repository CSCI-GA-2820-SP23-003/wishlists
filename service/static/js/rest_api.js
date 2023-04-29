$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        $("#owner_id").val(res.owner_id);
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
        $("#item_id").val("");
        $("#product_name").val("");
        $("#item_quantity").val("");
        $("#product_id").val("");
        $("#search_results").empty();
        $("#search_item_results").empty();
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
            url: "/api/wishlists",
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

    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {


        let wishlist_id = $("#wishlist_id").val();
        let name = $("#wishlist_name").val();        
        let owner_id = $("#owner_id").val();
        let data = {
            "name": name,
            "owner_id": parseInt(owner_id),
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/wishlists/${wishlist_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){            
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Search for a Wishlist
    // ****************************************

    $("#search-btn").click(function () {

        let id = $("#wishlist_id").val();
        let owner_id = $("#owner_id").val();
        let name = $("#wishlist_name").val();

        let query = ""

        if (id) {
           get_url = `/api/wishlists/${id}`
        }
        else if (owner_id){
            query += 'owner_id=' + owner_id
            get_url = `/api/wishlists?${query}`
        } else if (name) {
            query += 'name=' + name
            get_url = `/api/wishlists?${query}`
        }
        else {
            get_url = `/api/wishlists`
        }
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: get_url,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Wishlist ID</th>'
            table += '<th class="col-md-5">Name</th>'
            table += '<th class="col-md-5">Owner ID</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            if (id) {
                let wishlist = res;
                table +=  `<tr id="row_0"><td>${wishlist.id}</td><td>${wishlist.name}</td><td>${wishlist.owner_id}</td></tr>`;
                firstWishlist = wishlist;
                console.log(firstWishlist)
            } else {
                for(let i = 0; i < res.length; i++) {
                    let wishlist = res[i];
                    table +=  `<tr id="row_${i}"><td>${wishlist.id}</td><td>${wishlist.name}</td><td>${wishlist.owner_id}</td></tr>`;
                    if (i == 0) {
                        firstWishlist = wishlist;
                    }
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_form_data(firstWishlist)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let wishlist_name = $("#wishlist_name").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Empty a Wishlist
    // ****************************************

    $("#empty-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let wishlist_name = $("#wishlist_name").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/wishlists/${wishlist_id}/clear`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            clear_form_data()
            $("#wishlist_id").val(`${wishlist_id}`);
            flash_message(`${wishlist_name} wishlist has been cleared!`)
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ------------------------------------------ Buttons for Wishlist Items ------------------------------------------ 

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
            url: `/api/wishlists/${wishlist_id}/items`,
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
    // Retrieve an Item
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        let item_id = $("#item_id").val();        
        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){            
            update_form_data_item(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Wishlist Item
    // ****************************************

    $("#update-item-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let item_id = $("#item_id").val();
        let product_id = $("#product_id").val();
        let name = $("#product_name").val();
        let quantity = $("#item_quantity").val();

        //Only updates to product-name and quantity
        let data = {
            "product_name": name,
            "item_quantity": parseInt(quantity),
            "product_id": parseInt(product_id),
            "wishlist_id": parseInt(wishlist_id),
            "id": parseInt(item_id),
        };

        $("#flash_message").empty();        

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
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
    // Search for a Wishlist Item
    // ****************************************

    $("#search-item-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();
        let item_id = $("#item_id").val();
        let product_name = $("#product_name").val();

        let queryString = ""

        if(item_id){
            get_url = `/api/wishlists/${item_id}/items/${item_id}`
        } else if (product_name){
            queryString += 'name=' + product_name
            get_url = `/api/wishlists/${wishlist_id}/items?${queryString}`
        } else{
            get_url = `/api/wishlists/${wishlist_id}/items`
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: get_url,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_item_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Item ID</th>'
            table += '<th class="col-md-3">Name</th>'
            table += '<th class="col-md-4">Product ID</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '</tr></thead><tbody>'
            let firstIList = "";
            if(item_id){
                let item = res;
                table +=  `<tr id="row_0"><td>${item.id}</td><td>${item.product_name}</td><td>${item.product_id}</td><td>${item.item_quantity}</td>
                </tr>`;
                firstIList = item;
            } else{
                for(let i = 0; i < res.length; i++) {
                    let item = res[i];
                    table +=  `<tr id="row_${i}"><td>${item.id}</td><td>${item.product_name}</td><td>${item.product_id}</td><td>${item.item_quantity}</td>
                    </tr>`;
                    if (i == 0) {
                        firstIList = item;
                    }
                }
            }

            table += '</tbody></table>';
            $("#search_item_results").append(table);

            // copy the first result to the form
            if (firstIList != "") {
                update_form_data_item(firstIList)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#delete-item-btn").click(function () {

        let item_id = $("#item_id").val();        
        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/wishlists/${wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){            
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

})
