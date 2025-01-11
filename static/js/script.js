// Add to cart functionality
function initializeAddToCartButtons() {
    const buttons = document.querySelectorAll('.add-to-cart');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const serviceId = this.getAttribute('data-id');
            addToCart(serviceId);
        });
    });
}

function addToCart(serviceId) {
    const button = document.querySelector(`button[data-id="${serviceId}"]`);
    button.disabled = true;

    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ service_id: serviceId })
    })
    .then(response => response.json())
    .then(data => {
        showNotification(data.message, data.message.includes('already') ? 'red' : 'blue');
        if (data.total_price !== undefined) {
            const cartTotal = document.getElementById('cart-total');
            if (cartTotal) {
                cartTotal.textContent = `₹ ${data.total_price}`;
            }
        }
    })
    .catch(error => {
        showNotification('An error occurred. Please try again.', 'red');
        console.error('Error:', error);
    })
    .finally(() => {
        button.disabled = false;
    });
}

// Notification system
function showNotification(message, color) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        left: 50%;
        top: 20px;
        transform: translateX(-50%);
        padding: 15px 30px;
        background-color: ${color};
        color: white;
        border-radius: 15px;
        font-size: 16px;
        font-weight: normal;
        z-index: 1000;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        min-width: 300px;
        opacity: 0;
        transition: opacity 0.3s ease, top 0.3s ease;
    `;

    document.body.appendChild(notification);
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
    });

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 2000);
}

// Registration form functionality
let selectedCategory = "";

function showRegistrationForm(category) {
    selectedCategory = category;
    document.getElementById("registration-form").style.display = "flex";
    alert(`You selected: ${category}`);
}

function submitRegistration() {
    const dogName = document.getElementById("dog-name").value;
    const breed = document.getElementById("breed").value;
    const age = document.getElementById("age").value;
    const achievements = document.getElementById("achievements").value;

    if (dogName && breed && age) {
        alert("Registration Details Submitted\n\n" +
              `Category: ${selectedCategory}\n` +
              `Dog Name: ${dogName}\n` +
              `Breed: ${breed}\n` +
              `Age: ${age}\n` +
              `Achievements: ${achievements}`);
        document.getElementById("payment-section").style.display = "block";
        document.getElementById("registration-form").style.display = "none";
    } else {
        alert("Please fill out all fields.");
    }
}

// Initialize all event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAddToCartButtons();
});