import api from "./api";

/**
 * Service pour gérer les données du profil utilisateur
 */

/**
 * Récupérer les informations de l'utilisateur connecté
 */
export async function getMyProfile() {
  const response = await api.request("/me");
  return response;
}

/**
 * Récupérer toutes les enchères où l'utilisateur a participé (placé une enchère)
 */
export async function getMyParticipations() {
  try {
    const user = await api.request("/me");
    const bidsDoc = await api.request("/auctions");

    // Récupérer toutes les enchères et tous les bids
    const allAuctions = bidsDoc.auctions || [];
    const allBids = [];

    // Pour chaque enchère, récupérer les bids
    for (const auction of allAuctions) {
      try {
        const bidsData = await api.request(`/auctions/${auction.id}/bids`);
        const userBids = bidsData.bids.filter((bid) => bid.user.id === user.id);

        if (userBids.length > 0) {
          // Trouver l'enchère maximale de l'utilisateur
          const maxBid = Math.max(...userBids.map((b) => b.amount));
          allBids.push({
            ...auction,
            myBid: maxBid,
            myBidsCount: userBids.length,
          });
        }
      } catch (error) {
        console.error(`Error fetching bids for auction ${auction.id}:`, error);
      }
    }

    return allBids;
  } catch (error) {
    console.error("Error fetching participations:", error);
    return [];
  }
}

/**
 * Récupérer les enchères créées par l'utilisateur
 */
export async function getMyAuctions() {
  try {
    const user = await api.request("/me");
    const auctionsDoc = await api.request("/auctions");

    const auctions = auctionsDoc.auctions || [];

    // Filtrer les enchères créées par l'utilisateur
    const myAuctions = auctions.filter((auction) => {
      return auction.product && auction.product.owner_id === user.id;
    });

    return myAuctions;
  } catch (error) {
    console.error("Error fetching my auctions:", error);
    return [];
  }
}

/**
 * Récupérer les enchères gagnées par l'utilisateur
 */
export async function getMyWonAuctions() {
  try {
    const user = await api.request("/me");
    const auctionsDoc = await api.request("/auctions?status=closed");

    const auctions = auctionsDoc.auctions || [];

    // Filtrer les enchères où l'utilisateur est le gagnant
    const wonAuctions = auctions.filter((auction) => {
      return auction.winner_id === user.id;
    });

    return wonAuctions;
  } catch (error) {
    console.error("Error fetching won auctions:", error);
    return [];
  }
}

/**
 * Récupérer les achats de l'utilisateur (produits gagnés)
 */
export async function getMyPurchases() {
  try {
    const response = await api.request("/my/purchases");
    return response.products || [];
  } catch (error) {
    console.error("Error fetching purchases:", error);
    return [];
  }
}

/**
 * Créditer le compte de l'utilisateur
 */
export async function creditAccount(amount) {
  try {
    const response = await api.request("/me/credit", {
      method: "POST",
      body: JSON.stringify({ amount }),
    });
    return response;
  } catch (error) {
    console.error("Error crediting account:", error);
    throw error;
  }
}
