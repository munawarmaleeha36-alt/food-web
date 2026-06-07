// script.js

// Function to add item to cart
async function addToCart(itemId) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ item_id: itemId }),
        });

        if (response.ok) {
            const data = await response.json();
            updateCartCount(data.cart_count);
            alert(data.message);
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to add item to cart');
        }
    } catch (error) {
        console.error('Error adding item to cart:', error);
        alert('An error occurred while adding item to cart');
    }
}

// Function to update cart count display
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('#cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
    });
}

// Function to get cart contents
async function getCart() {
    try {
        const response = await fetch('/api/cart');
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            console.error('Failed to fetch cart');
            return null;
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        return null;
    }
}

// Function to remove item from cart
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`/api/cart/remove/${itemId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message);
            // Refresh cart display if on cart page
            if (window.location.pathname === '/cart') {
                location.reload();
            }
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to remove item from cart');
        }
    } catch (error) {
        console.error('Error removing item from cart:', error);
        alert('An error occurred while removing item from cart');
    }
}

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Update cart count
    const cartData = await getCart();
    if (cartData) {
        const totalItems = cartData.items.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(totalItems);
    }

    // Add event listeners for remove buttons on cart page
    const removeButtons = document.querySelectorAll('.remove-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            removeFromCart(itemId);
        });
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.card, .food-card, .deal-card, .large-card').forEach(card => {
    observer.observe(card);
});

// Hover effects for cards
document.querySelectorAll('.card, .food-card, .deal-card, .large-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
        this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
    });

    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.08)';
    });
});

// Filter functionality for shop by category
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        // Implement filter logic here if needed
    });
});
