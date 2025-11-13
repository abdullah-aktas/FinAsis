# NFTManager: ERC-721/1155 minting ve transfer için temel mantık
class NFTManager:
    def __init__(self):
        self.nfts = []
    def mint(self, name, owner):
        token = {'name': name, 'owner': owner, 'token_id': len(self.nfts)+1}
        self.nfts.append(token)
        return token
    def transfer(self, token_id, new_owner):
        for nft in self.nfts:
            if nft['token_id'] == token_id:
                nft['owner'] = new_owner
                return nft
        return None
    def get_nfts(self, owner):
        return [nft for nft in self.nfts if nft['owner'] == owner]
