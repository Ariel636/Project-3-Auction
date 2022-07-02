
def find_max_bid(bids):
    """ Finds maximum bid among all listing bids"""
    max_bid = 0
    for bid in bids:
        if bid.bid > max_bid:
            max_bid = bid.bid
    return max_bid
        

def find_winning_bids(bids):
    """ Returns a list of winning bids  bids"""
    winning_bids = []
    for bid in bids:
        #print(f"{bid.listing_id.id} - {bid.listing_id.bid} --- {bid.bid}")
        if bid.listing_id.bid == bid.bid:
            winning_bids.append(bid.listing_id.id)
    #print(winning_bids)
    return winning_bids


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"