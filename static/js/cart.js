/*  ---------------------------------------------------
    Cart AJAX Functionality
    Description: Handle real-time cart updates via AJAX
---------------------------------------------------------  */

'use strict';

(function ($) {

    /*-------------------
        Cart Quantity AJAX Update
    --------------------- */

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Add quantity buttons for cart page if they don't exist
    var cartProQty = $('.shoping-cart .pro-qty');
    cartProQty.each(function () {
        var $this = $(this);
        if ($this.find('.qtybtn').length === 0) {
            $this.prepend('<span class="dec qtybtn">-</span>');
            $this.append('<span class="inc qtybtn">+</span>');
        }
    });

    // CRITICAL: Unbind any handlers attached by main.js to prevent double-handling
    // main.js uses delegated events on .pro-qty, so we turn them off here
    $('.shoping-cart .pro-qty').off('click');
    $('.shoping-cart .pro-qty .qtybtn').off('click');

    // Handle quantity button clicks with AJAX
    // We attach to the specific elements directly now to be sure, or delegation on container
    $('.shoping-cart').on('click', '.pro-qty .qtybtn', function (e) {
        e.preventDefault();
        e.stopPropagation();

        var $button = $(this);
        var $proQty = $button.closest('.pro-qty');
        var $input = $proQty.find('input[name="quantity"]');
        var oldValue = parseInt($input.val()) || 1;
        var newVal;

        // Calculate new value
        if ($button.hasClass('inc')) {
            newVal = oldValue + 1;
        } else {
            // Don't allow decrementing below 1
            if (oldValue > 1) {
                newVal = oldValue - 1;
            } else {
                newVal = 1; // Stay at 1
                return; // Do nothing if already at 1
            }
        }

        // Update input immediately
        $input.val(newVal);

        // Get item ID and form data
        var itemId = $proQty.data('item-id');
        var $form = $proQty.find('form');
        var formUrl = $form.attr('action');
        var csrfToken = getCookie('csrftoken');

        // Show loading state
        $button.prop('disabled', true);
        var $row = $proQty.closest('tr');

        // Send AJAX request
        $.ajax({
            url: formUrl,
            type: 'POST',
            data: {
                'quantity': newVal,
                'csrfmiddlewaretoken': csrfToken
            },
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function (response) {
                if (response.success) {
                    if (response.removed) {
                        // Item was removed (quantity was 0)
                        $row.fadeOut(300, function () {
                            $(this).remove();

                            // Check if cart is now empty
                            if ($('.shoping__cart__table tbody tr').length === 0) {
                                location.reload(); // Reload to show empty cart message
                            }
                        });
                    } else {
                        // Update item total
                        $row.find('.item-total').text('$' + response.item_total.toFixed(2));

                        // Add a brief highlight effect
                        $row.find('.item-total').addClass('price-updated');
                        setTimeout(function () {
                            $row.find('.item-total').removeClass('price-updated');
                        }, 600);
                    }

                    // Update cart totals
                    $('.cart-subtotal').text('$' + response.cart_total.toFixed(2));
                    $('.cart-total').text('$' + response.cart_total.toFixed(2));

                    // Add highlight effect to totals
                    $('.cart-subtotal, .cart-total').addClass('price-updated');
                    setTimeout(function () {
                        $('.cart-subtotal, .cart-total').removeClass('price-updated');
                    }, 600);

                    // Show success message (optional)
                    if (window.showCartMessage && response.message) {
                        showCartMessage(response.message, 'success');
                    }
                }

                // Re-enable button
                $button.prop('disabled', false);
            },
            error: function (xhr, status, error) {
                console.error('Error updating cart:', error);

                // Revert input value on error
                $input.val(oldValue);
                $button.prop('disabled', false);

                // Show error message
                alert('Failed to update cart. Please try again.');
            }
        });
    });

    // Optional: Add a visual message system
    window.showCartMessage = function (message, type) {
        var messageClass = type === 'success' ? 'alert-success' : 'alert-danger';
        var $message = $('<div class="alert ' + messageClass + ' cart-message" style="position: fixed; top: 100px; right: 20px; z-index: 9999; min-width: 300px;">' + message + '</div>');

        $('body').append($message);

        setTimeout(function () {
            $message.fadeOut(300, function () {
                $(this).remove();
            });
        }, 2000);
    };

})(jQuery);
