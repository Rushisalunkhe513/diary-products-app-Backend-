from graphene import ObjectType

from app.gql.items.mutation import AddProduct,UpdateItem,DeleteItem,DeleteItems
from app.gql.banner.mutation import AddBanner,UpdateBanner,DeleteBanner
from app.gql.orders.mutation import PlaceOrder,UpdateOrder,DeleteOrder
from app.gql.subscription.mutation import AddSubscription,UpdateSubscription,DeleteSubscription
from app.gql.wallet.mutation import AddBalance,AddWallet,UpdateWalletDetails,DeleteWallet

from app.gql.users.mutation import (UserRegistartion,
                                    UserLogin,
                                    ForgetPin,
                                    UpdateUserDetails,
                                    AdminLogin,
                                    RefreshToken,
                                    Logout,
                                    ResetAdminPin,
                                    ResetPin,
                                    UpdateAdminDetails)

class Mutation(ObjectType):
    
    # User Mutation
    register_user = UserRegistartion.Field()
    user_login = UserLogin.Field()
    forget_pin = ForgetPin.Field()
    update_user_details = UpdateUserDetails.Field()
    admin_login = AdminLogin.Field()
    refresh_token = RefreshToken.Field()
    log_out = Logout.Field()
    reset_admin_pin = ResetAdminPin.Field()
    reset_pin = ResetPin.Field()
    update_admin_details = UpdateAdminDetails.Field()
    
    # Item Mutation
    add_item = AddProduct.Field()
    update_item = UpdateItem.Field()
    delete_items = DeleteItems.Field()
    delete_item = DeleteItem.Field()
    
    # Banner Mutation
    add_banner = AddBanner.Field()
    update_banner = UpdateBanner.Field()
    delete_banner = DeleteBanner.Field() 
    
    # Order Mutation
    place_order = PlaceOrder.Field()
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
    
    # Subscription Mutation
    add_subscription = AddSubscription.Field()
    update_subscription = UpdateSubscription.Field()
    delete_subscription = DeleteSubscription.Field()
    
    # Wallet Mutation
    add_wallet =  AddWallet.Field()
    add_balance = AddBalance.Field()
    update_wallet = UpdateWalletDetails.Field()
    delete_wallet = DeleteWallet.Field()
    