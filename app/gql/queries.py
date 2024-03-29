from graphene import ObjectType,List,Field,Int,String,Float
from app.db.models import UserObject,ItemDetailModel,ItemModel,BannerModel,OrderDetails,OrderItemModel,Subscription,WalletModel,UserWalletTransactions
from app.gql.users.types import UserInfo
from app.gql.types import ItemType,SubscriptionOutput
from app.gql.banner.types import BannerOutpt
from app.db.database import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from app.gql.types import ErrorResponse

from app.gql.orders.types import OrderData
from app.gql.wallet.types import WalletDetails

from app.gql.wallet.types import RecentUserTransactions

from app.utils import admin_privaleges,get_authenticated_admin



class Query(ObjectType):
    
    """
    Query are used to fetch the Information from the database.
    """
    
    get_users_profiles = List(UserInfo)
    get_user_profile = Field(UserInfo,id = Int(required = True))
    get_items = List(ItemType)
    get_item_by_id = Field(ItemType,id = Int(required = True))
    get_banners = List(BannerOutpt)
    get_banner_by_id = Field(BannerOutpt,id = Int(required = True))
    get_orders = List(OrderData)
    get_order_by_id = Field(OrderData,order_id = String(required = True))
    get_orders_by_status = List(OrderData,order_status = String(required = True))
    get_orders_placed_by_customer = List(OrderData,customer_id = Int(required = True))
    get_orders_by_payment_mode = List(OrderData,payment_mode = String(required = True))
    get_orders_by_payment_status = List(OrderData, payment_status = String(required = True))
    get_orders_by_shipping_details = List(OrderData, shipping_details = String(required = True))
    get_subscriptions = List(SubscriptionOutput)
    get_subscription_by_id = Field(SubscriptionOutput, id = Int(required = True))
    get_subscriptions_by_user = List(SubscriptionOutput,user_id = Int())
    get_wallet_by_user_id = List(WalletDetails,user_id = Int(required = True))
    get_recent_user_transaction = List(RecentUserTransactions)
    get_items_with_less_quantity = List(ItemType)
    get_item_by_search = List(ItemType,name = String(required = True))
    get_wallet_with_less_balance = List(WalletDetails,balance = Float(required = True))
    get_recent_user_orders = List(OrderData,user_id = Int(required = True))
    
    
    @staticmethod
    def resolve_recent_user_transaction(root,info):
        """
        get recent transaction by user.
        """
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return {
                "status":"failed",
                "status_code":404,
                "message":"failed to find user."
            }
        else:
            with Session() as session:
                user_transactions = session.query(UserWalletTransactions).filter(UserWalletTransactions.user_id == user.id).all()
            return user_transactions 
    
    
    
    
    @staticmethod
    def resolve_get_items_with_less_quantity(root,info):
        """
        get items with quantity abount to finish
        """
        admin =  admin_privaleges(info.context,Session)
        if not admin:
            return {
                "status":"failed",
                "status_code":404,
                "message":"admin not verified."
            }

        with Session() as session:
            items_with_less_quantity = session.query(ItemModel).join(ItemDetailModel).filter(ItemDetailModel.quantity < 10).all()
        return items_with_less_quantity
    
    @staticmethod
    def resolve_get_recent_user_orders(root,info,user_id):
        """
        query to get user latest orders.
        """ 
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            user_recent_orders = session.query(OrderDetails).filter(OrderDetails.customer_id  == user_id).order_by(desc(OrderDetails.order_time)).all()
        return user_recent_orders
    
    @staticmethod
    def resolve_get_wallet_with_less_balance(root,info,balance):
        """
        wallet query to get wallet with less balance.
        """
        
        admin =  admin_privaleges(info.context,Session)
        if not admin:
            return {
                "status":"failed",
                "status_code":404,
                "message":"admin not verified."
            }
        
        with Session() as session:
            wallet_data = session.query(WalletModel).filter(WalletModel.balance < balance).all()
        return wallet_data
    
    @staticmethod
    def resolve_get_item_by_search(root,info,name):
        """
        Search query for searching items by there name.
        """
        with Session() as session:
            item_by_search = session.query(ItemModel).options(joinedload(ItemModel.item_details)).filter(ItemModel.name.ilike(f"%{name}%")).all()
        return item_by_search
    
    
    @staticmethod
    def resolve_get_wallet_by_user_id(root,info,user_id):
        """
        get wallet of user by there id.
        """
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            user_wallets = session.query(WalletModel).filter(WalletModel.user_id == user_id).all()
        
        return user_wallets
    
    @staticmethod
    def resolve_get_subscription(root,info):
        """
        query for getting all subscriptions from database.
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            subscriptions = session.query(Subscription).options(joinedload(Subscription.subscribed_items)).all()
        return subscriptions
    
    @staticmethod
    def resolve_get_subscription_by_id(root,info,id):
        """
        get specific subscription by id
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            subscription_by_id = session.query(Subscription).options(joinedload(Subscription.subscribed_items)).filter(Subscription.id == id).first()
        return subscription_by_id
    
    @staticmethod
    def resolve_get_subscriptions_by_user(root,info,user_id):
        """
        get subscription placed by specific user from database.
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            subscription_by_user = session.query(Subscription).options(joinedload(Subscription.subscribed_items)).filter(Subscription.customer_id == user_id).all()
        return subscription_by_user
    
    @staticmethod
    def resolve_get_orders(root,info):
        """
        get all orders by this query
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            orders = Session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).all()
        return orders

    @staticmethod
    def resolve_get_order_by_id(root,info,order_id):
        """
        get specific order by this query using order_id
        """
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            order_by_id = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.order_id == order_id).first()
        return order_by_id
    
    @staticmethod
    def resolve_get_orders_by_status(root,info,order_status):
        """
        get orders by order_status using this query
        """
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            orders_by_status = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.order_status == order_status).all()
        return orders_by_status

    @staticmethod
    def resolve_get_orders_placed_by_customer(root,info,customer_id):
        """
        get all orders by customer_id using this query
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            order_by_customers = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.customer_id == customer_id).all()
        return order_by_customers

    @staticmethod
    def resolve_get_orders_by_payment_mode(root,info,payment_mode):
        """
        get all orders by using this query based on mode of payment
        """
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            order_by_payment_mode = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.payment_mode == payment_mode).all()
        return order_by_payment_mode

    @staticmethod
    def resolve_get_orders_by_payment_status(root,info,payment_status):
        """
        get all orders by payment_status by this query
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            order_by_payment_status = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.payment_status == payment_status).all()
        return order_by_payment_status
    
    @staticmethod
    def resolve_get_orders_by_shipping_details(root,info,shipping_details):
        """
        get all orders by there shipping_details by using this query.
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            order_by_shipping_details = session.query(OrderDetails).options(joinedload(OrderDetails.order_items)).filter(OrderDetails.shipping_details == shipping_details).all()
        return order_by_shipping_details
    
    @staticmethod
    def resolve_get_banners(root,info):
        """
        get all banner images using this query.
        """
        admin = admin_privaleges(info.context,Session)
        if not admin:
            return {
                "status":"failed",
                "status_code":404,
                "message":"admin not verified."
            }
        
        with Session() as session:
            banners = session.query(BannerModel).all()
            return banners
    
    @staticmethod
    def resolve_get_banner_by_id(root,info,id):
        """
        get single banner image using id by this query.
        """
        admin =  admin_privaleges(info.context,Session)
        if not admin:
            return {
                "status":"failed",
                "status_code":404,
                "message":"admin not verified."
            }
        with Session() as session:
            banner = session.query(BannerModel).filter(BannerModel.id == id).first()
            return banner
        
    @staticmethod
    def resolve_get_users_profiles(root,info):
        
        """
        get all users profile using this query
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            users = session.query(UserObject).all()
            return users
        
    @staticmethod
    def resolve_get_user_profile(root,info,id):
        
        """
        get single user profile by this query
        """
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
            
        with Session() as session:
            user = session.query(UserObject).filter(UserObject.id == id).first()
            return user
        
    @staticmethod
    def resolve_get_items(root,info):
        """
        get all items from database by using this query.
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        with Session() as session:
            items = session.query(ItemModel).options(joinedload(ItemModel.item_details)).all()
            # options(joinedload(ItemModel.item_details)) is used for loading each items item_deatails along with that item. rather than 
            # querying each item for its item_details.
            
            return items
        
    @staticmethod
    def resolve_get_item_by_id(root,info,id):
        """
        get specific item by its id using this query. 
        """
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return {
                "status": "failed",
                "status_code" : 404,
                "message" :"not verified user."
            }
        
        with Session() as session:
            item = session.query(ItemModel).options(joinedload(ItemModel.item_details)).filter(ItemModel.id == id).first()
            
            return item
    
        