// Service API pour communiquer avec le backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    console.log('[API Service] Initialized with base URL:', this.baseURL)
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

    console.log(`[API Request] ${options.method || 'GET'} ${url}`)
    console.log('[API Base URL]', this.baseURL)
    console.log('[API Token]', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')

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
      
      // Vérifier le type de contenu de la réponse
      const contentType = response.headers.get('content-type')
      console.log('[API Response] Content-Type:', contentType)
      
      if (!contentType || !contentType.includes('application/json')) {
        // La réponse n'est pas du JSON (probablement une page d'erreur HTML)
        const text = await response.text()
        console.error('[API Error] Non-JSON response:', text.substring(0, 200))
        throw new Error(`Erreur serveur: réponse non-JSON (Status ${response.status}). Vérifiez que l'URL du backend est correcte.`)
      }
      
      const data = await response.json()

      if (!response.ok) {
        console.error(`[API Error] ${response.status}:`, data)
        if (response.status === 401) {
          // Token invalide ou expiré
          this.removeToken()
          localStorage.removeItem('currentUser')
          throw new Error('⚠️ Session expirée. Veuillez vous reconnecter.')
        }
        throw new Error(data.error || data.message || 'Une erreur est survenue')
      }

      console.log(`[API Success] ${endpoint}`, data)
      return data
    } catch (error) {
      console.error('[API Error]:', error)
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
    return await this.request(`/auctions/${auctionId}/bid`, {
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
