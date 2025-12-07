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
      console.log('WebSocket already connected')
      return this.socket
    }

    console.log('Connecting to WebSocket:', SOCKET_URL)
    
    this.socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected:', this.socket.id)
      this.connected = true
    })

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason)
      this.connected = false
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
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
