import { ref } from "vue";

// Event emitter simple pour notifier les composants des changements d'enchères
class AuctionEventEmitter {
  constructor() {
    this.listeners = {
      "auction:created": [],
      "auction:updated": [],
      "auction:deleted": [],
      "bid:placed": [],
    };
  }

  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(
        (cb) => cb !== callback
      );
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }
}

// Instance globale
const auctionEvents = new AuctionEventEmitter();

// Composable pour utiliser les événements d'enchères
export function useAuctionEvents() {
  const notifyAuctionCreated = (auctionData) => {
    console.log("📢 Event: auction:created", auctionData);
    auctionEvents.emit("auction:created", auctionData);
  };

  const notifyAuctionUpdated = (auctionData) => {
    console.log("📢 Event: auction:updated", auctionData);
    auctionEvents.emit("auction:updated", auctionData);
  };

  const notifyAuctionDeleted = (auctionId) => {
    console.log("📢 Event: auction:deleted", auctionId);
    auctionEvents.emit("auction:deleted", auctionId);
  };

  const notifyBidPlaced = (bidData) => {
    console.log("📢 Event: bid:placed", bidData);
    auctionEvents.emit("bid:placed", bidData);
  };

  const onAuctionCreated = (callback) => {
    auctionEvents.on("auction:created", callback);
    return () => auctionEvents.off("auction:created", callback);
  };

  const onAuctionUpdated = (callback) => {
    auctionEvents.on("auction:updated", callback);
    return () => auctionEvents.off("auction:updated", callback);
  };

  const onAuctionDeleted = (callback) => {
    auctionEvents.on("auction:deleted", callback);
    return () => auctionEvents.off("auction:deleted", callback);
  };

  const onBidPlaced = (callback) => {
    auctionEvents.on("bid:placed", callback);
    return () => auctionEvents.off("bid:placed", callback);
  };

  return {
    notifyAuctionCreated,
    notifyAuctionUpdated,
    notifyAuctionDeleted,
    notifyBidPlaced,
    onAuctionCreated,
    onAuctionUpdated,
    onAuctionDeleted,
    onBidPlaced,
  };
}
