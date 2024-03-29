from graphene import Int,Float,String,ObjectType,InputObjectType,DateTime



# wallet Output Type

class WalletDetails(ObjectType):
    wallet_id = String()
    balance = Float()
    created_at = DateTime()
    # updated_at = DateTime()
    user_name = String()
    user_id = Int()
    user_mobile_number = String()
    

# wallet type for adding data
class WalletDetailsInputType(InputObjectType):
    balance = Float()
    user_name = String()
    user_id = Int()
    user_mobile_number = String()
    
    
# type to show recent user transactions.

class RecentUserTransactions(ObjectType):
    user_id = Int()
    Wallet_id = String()
    amount_change = String()
    updated_at = DateTime()
    