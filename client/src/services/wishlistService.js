// Wishlist Service for managing user's saved places
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const wishlistService = {
  /**
   * Get all places in user's wishlist
   * @param {string} userId - User ID from Clerk authentication
   * @returns {Promise<Array>} Array of wishlist items
   */
  async getUserWishlist(userId) {
    if (!userId) {
      console.error('User ID is required for wishlist operations');
      return [];
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wishlist/${userId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          // User has no wishlist items yet
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      return [];
    }
  },

  /**
   * Add place to user's wishlist
   * @param {number|string} placeId - Place ID to add
   * @param {string} userId - User ID from Clerk authentication
   * @param {Object} placeData - Optional place data for non-database places
   * @returns {Promise<Object>} Success response
   */
  async addToWishlist(placeId, userId, placeData = null) {
    if (!userId) {
      throw new Error('User ID is required');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wishlist/${userId}/${placeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: placeData ? JSON.stringify(placeData) : JSON.stringify({}),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      throw error;
    }
  },

  /**
   * Remove place from user's wishlist
   * @param {number|string} placeId - Place ID to remove
   * @param {string} userId - User ID from Clerk authentication
   * @returns {Promise<Object>} Success response
   */
  async removeFromWishlist(placeId, userId) {
    if (!userId) {
      throw new Error('User ID is required');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wishlist/${userId}/${placeId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      throw error;
    }
  },

  /**
   * Check if place is in user's wishlist
   * @param {number|string} placeId - Place ID to check
   * @param {string} userId - User ID from Clerk authentication
   * @returns {Promise<boolean>} True if in wishlist
   */
  async isInWishlist(placeId, userId) {
    if (!userId) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/wishlist/${userId}/${placeId}/check`);
      
      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      return data.in_wishlist;
    } catch (error) {
      console.error('Error checking wishlist status:', error);
      return false;
    }
  }
};

export default wishlistService;