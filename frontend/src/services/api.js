// Service API pour communiquer avec le backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Récupérer le token JWT du localStorage
  getToken() {
    return localStorage.getItem('authToken')
  }

  // Sauvegarder le token JWT
  setToken(token) {
    localStorage.setItem('authToken', token)
  }

  // Supprimer le token JWT
  removeToken() {
    localStorage.removeItem('authToken')
  }

  // Méthode générique pour faire des requêtes
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getToken()

    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      
      // Gérer les erreurs HTTP
      if (!response.ok) {
        let errorMessage = 'Une erreur est survenue'
        
        try {
          const data = await response.json()
          errorMessage = data.error || data.message || data.msg || errorMessage
        } catch (e) {
          // Si pas de JSON, utiliser le status text
          errorMessage = response.statusText || errorMessage
        }
        
        // Ajouter le code HTTP dans le message pour le débogage
        const error = new Error(errorMessage)
        error.status = response.status
        throw error
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  // --- Auth endpoints ---
  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
    return response
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
    
    if (response.access_token) {
      this.setToken(response.access_token)
    }
    
    return response
  }

  async getCurrentUser() {
    return await this.request('/me')
  }

  logout() {
    this.removeToken()
    localStorage.removeItem('currentUser')
  }

  // --- Auctions endpoints ---
  async getAuctions(filters = {}) {
    const params = new URLSearchParams(filters)
    return await this.request(`/auctions?${params}`)
  }

  async getAuction(id) {
    return await this.request(`/auctions/${id}`)
  }

  async createAuction(auctionData) {
    return await this.request('/auctions', {
      method: 'POST',
      body: JSON.stringify(auctionData),
    })
  }

  async placeBid(auctionId, amount) {
    return await this.request(`/auctions/${auctionId}/bids`, {
      method: 'POST',
      body: JSON.stringify({ amount }),
    })
  }

  // --- Products endpoints ---
  async createProduct(productData) {
    return await this.request('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    })
  }

  // --- Categories endpoints ---
  async getCategories() {
    return await this.request('/categories')
  }
}

export default new ApiService()
