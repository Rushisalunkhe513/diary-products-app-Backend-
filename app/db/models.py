from sqlalchemy import Integer,String,Boolean,ARRAY,Column,Float,ForeignKey,DateTime
from sqlalchemy.orm import declarative_base,relationship,validates


Base = declarative_base()

############# lets define user tables first ############

class UserObject(Base):
    """
    define tablename
    """
    __tablename__ = "users"
    
    id = Column(Integer,primary_key=True,autoincrement=True) # id is primary_key of table which will keep all records of no of users, and it will increment automatically.
    first_name = Column(String,nullable=False)
    last_name  = Column(String,nullable = False)
    pin_hash = Column(String,nullable = False,unique=True)
    land_mark = Column(String,default="null")
    city = Column(String,nullable=False)
    pincode = Column(String,nullable = False)
    address = Column(String,nullable = False)
    mobile_number = Column(String,nullable = False)
    
    # we need order placed by users.
    user_orders = relationship(
        "OrderDetails",
        back_populates="users",
        lazy="joined",
        cascade="all,delete"
    )
    
    # lets link subscription with users.
    
    subscriptions = relationship(
        "Subscription",
        back_populates="user",
    )
    
    #relationship with wallet table
    
    wallet_details = relationship(
        "WalletModel",
        back_populates="user_details"
    )
    
    wallet_transaction = relationship(
        "UserWalletTransactions",
        back_populates="user_wallet"
    )
    
    # reltionship with usersessions
    
    user_session = relationship(
        "UserSession",
        back_populates = "user_data"
    )
    
    
############# lets define Item table here ##############

class ItemModel(Base):
    __tablename__ = "items"
    
    id = Column(Integer,autoincrement=True,primary_key=True)
    name = Column(String,nullable = False)
    description = Column(String,nullable=True)
    title = Column(String,nullable = False)
    image_url = Column(String,nullable = False)
    
    # lets relate itemdetailmodel to itemmodel as well.
    item_details = relationship(
        "ItemDetailModel", # to which table it relates to
        back_populates="items",
        lazy = "joined",
        cascade= "all,delete"  
    )
    
    order_items = relationship(
        "OrderItemModel",
        back_populates = "items"
    )
        
"""
        back_populates ensures that this is a bidirectional relationship, meaning changes made on one side will reflect on the other.
        
        lazy="joined": This defines the loading strategy for the relationship. In this case, "joined" means that when 
                        instances of the current model (tem) are loaded, the related items will be loaded as well, in a single query using
                        a SQL JOIN.
        
        cascade = "all,delete" this cascade all delete will be only applicable to parent table. this means that when parent table is deleted then 
        child table will be deleted as well. or when item with id 8 is delered then item_details related to item id 8 will be deleted as well.
"""  
    
    
    
    
class ItemDetailModel(Base):
    __tablename__ = "item_details"
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    mrp = Column(Float,nullable = False)
    discount = Column(Float,nullable = True)
    price = Column(Float,nullable = False)
    quantity = Column(Integer,nullable=False)
    unit = Column(String,nullable = False)
    weight = Column(String,nullable = True)
    item_id = Column(Integer,ForeignKey("items.id"))
    
    @validates("unit")
    def validate_unit(self,key,unit):
        allowed_units = ["kg","gm","pcs"]
        
        if unit not in allowed_units:
            raise ValueError(f"{unit} is not in following allowed_units {allowed_units}.")
        return unit
        
    items = relationship(
        "ItemModel", # specifying the classname of table.(to whivh table itemdeailModel table relates to)
        back_populates="item_details"
    )
        
        
################ Lets Create Banner Images Model Here ####################

class BannerModel(Base):
    __tablename__ = "banners"
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    image_url = Column(String,nullable=False)
    
    
    
################ lets create Subscription table here #####################

class Subscription(Base):
    __tablename__ = "subscription"
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    customer_id = Column(Integer,ForeignKey("users.id"))
    customer_name = Column(String,nullable = False)
    customer_address = Column(String,nullable=False)
    subscription_time = Column(DateTime,nullable = False)
    
    user = relationship(
        "UserObject",
        back_populates="subscriptions",
    )
    
    # with subscribed_items table
    
    subscribed_item = relationship(
        "SubscribedItems",
        back_populates="subscribe",
        cascade="all,delete",
        lazy="joined"
    )
    

############# subscribed utems table. ##############################
class SubscribedItems(Base):
    __tablename__ = "subscribed_items"
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    items_id = Column(Integer,ForeignKey("items.id"),nullable=False)
    item_name = Column(String,nullable=False)
    item_quantity = Column(Integer,nullable= False)
    item_unit = Column(String,nullable=False)
    item_price = Column(Float,nullable=False)
    item_weight = Column(String,nullable = False)
    frequency = Column(String,nullable=False)
    subscription_from = Column(DateTime,nullable = False)
    subscription_to = Column(DateTime,nullable = True)
    subscription_id = Column(Integer,ForeignKey("subscription.id"))
    
    # lets keep frequnecy to = "daily","occasionally".
    @validates("frequency")
    def validate_frequency(self,key,frequency):
        allowed_frequency = ["daily","occasionally"]
        
        if frequency not in allowed_frequency:
            raise  ValueError(f"allowed frequency value are {allowed_frequency}.")
        return frequency
        
    # lets relate table to subscription
    
    subscribe = relationship(
        "Subscription",
        back_populates = "subscribed_item" 
    )    

############### lets create Order table ############################

class OrderDetails(Base):
    __tablename__ = "orders"
    
    
    #let keep order_id unique and primary key and not auto incrementing.
    order_id = Column(String, nullable = False, unique = True, primary_key=True)
    
    customer_id = Column(Integer,ForeignKey("users.id"))
    customer_name  = Column(String,nullable = False)
    customer_mobile_number = Column(String,nullable = False)
    order_time = Column(DateTime,nullable = False)
    order_total = Column(Float, nullable = False)
    order_status = Column(String,nullable = False)
    payment_mode = Column(String,nullable = False)
    payment_status = Column(String, nullable = False)
    shipping_address = Column(String, nullable = True)
    shipping_details = Column(String,nullable = True)
    
    # lets keep payment mode only to cash on delivery and  online.
    @validates("payment_mode")
    def validate_PaymentMode(self,key,payment_mode):
        allowed_payment_modes = ["COD","Online","wallet"]
        
        if payment_mode not in allowed_payment_modes:
            return ValueError(f"payment_mode {payment_mode} is not allowed.")
        
        return payment_mode
    
    
    # lets add relation to users.
    # we dont need users data when we place order so no lazy joined.
    users = relationship(
        "UserObject",
        back_populates="user_orders",
    )
    
    # lets add order_items to the order
    order_items = relationship(
        "OrderItemModel",
        back_populates="orders",
        lazy = 'joined',
        cascade = "all,delete"
    )
    
    
    
########### lets create order_items by user.#################
class OrderItemModel(Base):
    __tablename__ = "orderitems"
    id = Column(Integer,primary_key=True,autoincrement=True)
    # this items will belong to that order.
    order_id = Column(String, ForeignKey("orders.order_id"))
    item_name = Column(String,nullable = False)
    item_quantity = Column(Integer,nullable = False)
    item_price = Column(Float,nullable = False)
    item_mrp = Column(Float,nullable = False)
    item_discount = Column(Float,nullable = False)
    item_id = Column(Integer,ForeignKey("items.id"))
    
    orders = relationship(
        "OrderDetails",
        back_populates = "order_items"
    )
    
    items = relationship(
        "ItemModel",
        back_populates = "order_items"
    )
    
############ lets add Wallet table ######################

class WalletModel(Base):
    __tablename__ = "wallet_details"
    
    wallet_id = Column(String,primary_key=True)
    balance = Column(Float,nullable = True,default = 0)
    user_name = Column(String,nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    user_mobile_number = Column(String,nullable = False)
    created_at = Column(DateTime,nullable = True)
    # updated_at = Column(DateTime,nullable = True)
    
    #relationship with user table
    
    user_details = relationship(
        "UserObject",
        back_populates="wallet_details"
    )
    
    # relationship with wallet_transactions table
    
    wallet_transaction = relationship(
        "UserWalletTransactions",
        back_populates= "wallet"
    )
    
############### add table for adding user wallet transactions ###########
class UserWalletTransactions(Base):
    
    __tablename__ = "wallet_transactions"
    
    # shpuld have amount added
    # shiud have user_id
    # should have wallet_id to refer to wallet
    # should have update_at column.
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    amount_change = Column(String,nullable = False)
    updated_at = Column(DateTime,nullable = False)
    wallet_id = Column(String,ForeignKey("wallet_details.wallet_id"))
    
    # with wallet model.
    wallet = relationship(
        "WalletModel",
        back_populates= "wallet_transaction"
    )
    
    # with user table.
    user_wallet = relationship(
        "UserObject",
        back_populates="wallet_transaction"
    )
    
# lets add admin table for authentication and authorizing actions.
class AdminModel(Base):
    __tablename__ = "admin"
    
    id = Column(Integer,primary_key=True,autoincrement= True)
    admin_name = Column(String,nullable=False)
    admin_mobile_number = Column(String,nullable = False)
    admin_pin_hash = Column(String,nullable = False)
    created_at = Column(DateTime,nullable = False)
    
    admin_session = relationship(
        "AdminSession",
        back_populates="admin_data"
    )
    
# lets add session table for storing user and admins access and refresh jwt token.
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer,primary_key = True,autoincrement=True)
    access_token = Column(String,nullable = False)
    refresh_token = Column(String,nullable = False)
    token_holder_mobile_number = Column(String,nullable = False)
    token_holder_name = Column(String,nullable = False) 
    user_id = Column(Integer,ForeignKey("users.id"))
    
    # lets establish relationship with user table.
    user_data = relationship(
        "UserObject",
        back_populates="user_session"
    )
    
class AdminSession(Base):
    __tablename__ = "admin_session"
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    access_token = Column(String,nullable=False)
    refresh_token = Column(String,nullable = False)
    token_holder_mobile_number = Column(String,nullable = False)
    token_holder_name = Column(String,nullable = False)
    admin_id = Column(Integer,ForeignKey("admin.id"))
    
    # lets establish relationship with admin table.
    
    admin_data = relationship(
        "AdminModel",
        back_populates= "admin_session"
    )