import { io } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:5000'

class WebSocketService {
  constructor() {
    this.socket = null
    this.connected = false
    this.listeners = new Map()
  }

  connect() {
    if (this.socket && this.connected) {
      console.log('⚠️ WebSocket déjà connecté')
      return this.socket
    }

    console.log('\n' + '='.repeat(60))
    console.log('🔌 TENTATIVE DE CONNEXION WEBSOCKET')
    console.log('URL:', SOCKET_URL)
    console.log('Transports:', ['websocket', 'polling'])
    console.log('='.repeat(60) + '\n')
    
    this.socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      timeout: 10000
    })

    this.socket.on('connect', () => {
      console.log('\n' + '='.repeat(60))
      console.log('✅ WEBSOCKET CONNECTÉ AVEC SUCCÈS!')
      console.log('Socket ID:', this.socket.id)
      console.log('Transport:', this.socket.io.engine.transport.name)
      console.log('='.repeat(60) + '\n')
      this.connected = true
    })

    this.socket.on('disconnect', (reason) => {
      console.log('\n' + '='.repeat(60))
      console.log('❌ WEBSOCKET DÉCONNECTÉ')
      console.log('Raison:', reason)
      console.log('='.repeat(60) + '\n')
      this.connected = false
    })

    this.socket.on('connect_error', (error) => {
      console.error('\n' + '='.repeat(60))
      console.error('❌ ERREUR DE CONNEXION WEBSOCKET')
      console.error('Message:', error.message)
      console.error('Type:', error.type)
      console.error('Description:', error.description)
      console.error('URL tentée:', SOCKET_URL)
      console.error('='.repeat(60) + '\n')
    })
    
    this.socket.on('connect_timeout', () => {
      console.error('\n' + '='.repeat(60))
      console.error('⏰ TIMEOUT DE CONNEXION WEBSOCKET')
      console.error('Le serveur ne répond pas')
      console.error('='.repeat(60) + '\n')
    })
    
    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`🔄 Tentative de reconnexion #${attemptNumber}...`)
    })
    
    this.socket.on('reconnect_failed', () => {
      console.error('❌ Toutes les tentatives de reconnexion ont échoué')
    })

    this.socket.on('connected', (data) => {
      console.log('Server confirmed connection:', data)
    })

    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.connected = false
      this.listeners.clear()
      console.log('WebSocket disconnected')
    }
  }

  joinAuction(auctionId) {
    if (!this.socket || !this.connected) {
      console.warn('WebSocket not connected, connecting now...')
      this.connect()
    }

    console.log('Joining auction room:', auctionId)
    this.socket.emit('join_auction', { auction_id: auctionId })

    return new Promise((resolve) => {
      this.socket.once('joined_auction', (data) => {
        console.log('Joined auction room:', data.auction_id)
        resolve(data)
      })
    })
  }

  leaveAuction(auctionId) {
    if (this.socket && this.connected) {
      console.log('Leaving auction room:', auctionId)
      this.socket.emit('leave_auction', { auction_id: auctionId })
    }
  }

  onBidPlaced(callback) {
    if (!this.socket) {
      console.warn('Cannot listen for bids, socket not initialized')
      return
    }

    console.log('Listening for bid_placed events')
    this.socket.on('bid_placed', (data) => {
      console.log('📢 New bid received via WebSocket:', data)
      callback(data)
    })

    // Stocker le callback pour pouvoir le retirer plus tard
    this.listeners.set('bid_placed', callback)
  }

  offBidPlaced() {
    if (this.socket) {
      // Retirer tous les listeners pour bid_placed
      this.socket.removeAllListeners('bid_placed')
      this.listeners.delete('bid_placed')
      console.log('Stopped listening for bid_placed events')
    }
  }

  isConnected() {
    return this.connected && this.socket?.connected
  }
}

// Instance singleton
const websocketService = new WebSocketService()

export default websocketService
