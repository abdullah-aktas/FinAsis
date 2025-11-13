import React, { useState } from 'react';
export default function NFTPanel() {
  const [nfts, setNfts] = useState([]);
  const mintNFT = () => {
    const newNft = { name: 'Demo NFT', tokenId: nfts.length + 1 };
    setNfts([...nfts, newNft]);
  };
  return (
    <div className="bg-white rounded-lg shadow p-4 w-64">
      <h2 className="font-bold text-lg mb-2">NFT Envanteri</h2>
      <button className="px-4 py-2 rounded bg-blue-500 text-white font-bold mb-2" onClick={mintNFT}>
        Demo NFT Mintle
      </button>
      <ul className="text-sm">
        {nfts.map(nft => (
          <li key={nft.tokenId} className="mb-1">{nft.name} (ID: {nft.tokenId})</li>
        ))}
      </ul>
    </div>
  );
}
