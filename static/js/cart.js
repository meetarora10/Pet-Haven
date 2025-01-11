// Cart functionality
function removeFromCart(cartId) {
    fetch(`/remove_from_cart/${cartId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            location.reload(); // Refresh the page to reflect changes
        } else {
            alert('Error removing item from cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing request');
    });
}

// Update cart total
function updateCartTotal(total) {
    const cartTotal = document.getElementById('cart-total');
    if (cartTotal) {
        cartTotal.textContent = `₹ ${total}`;
    }
}

// Initialize cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners to remove buttons
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cartId = this.getAttribute('data-id');
            removeFromCart(cartId);
        });
    });

    // Add event listener to checkout button
    const checkoutBtn = document.querySelector('.buynow-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            window.location.href = '/details';
        });
    }

    // Add event listeners for quantity changes if needed
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const cartId = this.getAttribute('data-cart-id');
            const newQuantity = this.value;
            updateQuantity(cartId, newQuantity);
        });
    });
});