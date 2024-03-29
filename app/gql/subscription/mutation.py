import datetime

from graphene import Mutation,Float,Int,String,Field,DateTime

from app.gql.subscription.types import SubscriptionInput

from app.db.models import ItemDetailModel,Subscription,SubscribedItems,WalletModel,UserWalletTransactions,UserObject
from app.db.database import Session

from app.gql.types import SubscriptionOutput

from app.utils import get_authenticated_admin



# lets Write Mutation for adding subscription
class AddSubscription(Mutation):
    """
    Mutation for adding subscription for user for milk products like packet of milk,
    packet of lassi and more.
    """
    class Arguments:
        subscription_data = SubscriptionInput()
    
    status = String()
    status_code = Int()
    message = String()
    subscription_output = Field(lambda:SubscriptionOutput())
    
    @staticmethod
    def mutate(root,
               info,
               subscription_data):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return AddSubscription(
                status = "faield",
                status_code = 404,
                message = "failed to Subscribe an Item."
            )
        try:
            with Session() as session:
                
                
                # lets add the data in subscribed order var.
                if session.query(UserObject).filter(UserObject.mobile_number == user.user_mobile_number).first():
                    subscribed_order_data = Subscription(
                        customer_id = subscription_data.customer_id,
                        customer_name = subscription_data.customer_name,
                        customer_address = subscription_data.customer_address,
                        subscription_time = datetime.datetime.now()
                    )
                    session.add(subscribed_order_data)
                    # session.commit()
                    
                    for item_details in subscription_data.subscribed_items_input:
                        subscription_items = SubscribedItems(
                            items_id = item_details.item_id,
                            item_name = item_details.item_name,
                            item_quantity = item_details.item_quantity,
                            item_price = item_details.item_price,
                            item_weight = item_details.item_weight,
                            item_unit = item_details.item_unit,
                            subscription_id = subscribed_order_data.id,
                            frequency = item_details.frequency,
                            subscription_to = datetime.datetime.strptime(item_details.subscription_to,"%Y-%m-%d"),
                            subscription_from = datetime.datetime.strptime(item_details.subscription_from,"%Y-%m-%d")
                        )
                        item_quantity = session.query(ItemDetailModel).filter(ItemDetailModel.id == item_details.item_id).first()
                        wallet_data = session.query(WalletModel).filter(WalletModel.user_id == subscribed_order_data.customer_id).first()
                        wallet_transaction = session.query(UserWalletTransactions).filter(UserWalletTransactions.user_id == subscribed_order_data.customer_id).first()
                        # start_date = subscription_items.subscription_from
                        # end_date = subscription_items.subscription_to
                        if item_details.frequency == "daily":
                            # for date in range(datetime.datetime.strptime(item_details.subscription_from,"%Y-%m-%d"),datetime.datetime.strptime(item_details.subscription_to,"%Y-%m-%d")):
                                current_day = datetime.datetime.now().date()
                                if current_day >= datetime.datetime.strptime(item_details.subscription_from,"%Y-%m-%d").date() and current_day < datetime.datetime.strptime(item_details.subscription_to,"%Y-%m-%d") and item_quantity.quantity == 0 or item_quantity.quantity > item_details.item_quantity and wallet_data.balance > item_details.item_price:
                                    item_quantity.quantity = item_quantity.quantity - item_details.item_quantity
                                    wallet_data.balance = wallet_data.balance - item_details.item_price
                                    wallet_transaction.amount_change = f"-{item_details.item_price}"
                                    
                                else:
                                    return AddSubscription(
                                            status = "failed",
                                            status_code = 404,
                                            message = "failed to place subscription due to item can not match quantity for this subscription."
                                        )
                        else:
                            current_date = datetime.datetime.now().date()
                            if current_date >= datetime.datetime.strptime(item_details.subscription_from,"%Y-%m-%d").date() and current_date < datetime.datetime.strptime(item_details.subscription_to,"%Y-%m-%d") and item_quantity.quantity == 0 or item_quantity.quantity > item_details.item_quantity and wallet_data.balance > item_details.item_price:
                                    item_quantity.quantity = item_quantity.quantity - item_details.item_quantity
                                    wallet_data.balance = wallet_data.balance - item_details.item_price
                                    wallet_transaction.amount_change = f"-{item_details.item_price}"
                            else:
                                return AddSubscription(
                                            status = "failed",
                                            status_code = 404,
                                            message = "failed to place subscription due to item can not match quantity for this subscription."
                                        )
                        
                        subscribed_order_data.subscribed_item.append(subscription_items)
                
                session.add(item_quantity)
                session.add(wallet_data)
                session.add(wallet_transaction)
                session.add(subscribed_order_data)
                session.commit()
                session.refresh(subscribed_order_data)
            
            return AddSubscription(
                status = "success",
                status_code = 201,
                message = f"subscription for user with id {subscribed_order_data.customer_id} has been added.",
                subscription_output = subscribed_order_data
            )
        except:
            session.rollback()
            
            return AddSubscription(
                status = "failed",
                status_code = 404,
                message = "failed to add subscription."
            )
                
                
# lets write mutation for updating the subscription.
class UpdateSubscription(Mutation):
    """
    Mutation for updating the subscription data by its id.
    """        
    class Arguments:
        subscription_id = Int(required = True)
        customer_id = Int()
        customer_name = String()
        customer_address = String()
        item_name = String()
        item_id = Int()
        item_price = Float()
        item_unit = String()
        item_weight = String()
        item_quantity = Int()
        frequency = String()
        subscription_from = String()
        subscription_to = String()
        
    status = String()
    status_code = Int()
    message = String()
    subscription_data = Field(lambda:SubscriptionOutput)
        
        
    @staticmethod
    def mutate(root,info,
            subscription_id,
            customer_id,
            customer_name,
            customer_address,
            item_name,
            item_id,
            item_price,
            item_unit,
            item_weight,
            item_quantity,
            frequency,
            subscription_to,
            subscription_from):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return UpdateSubscription(
                status = "faield",
                status_code = 404,
                message = "failed to update subscription."
            )
        try:
            with Session() as session:
                subscription_data = session.query(Subscription).filter(Subscription.id == subscription_id and Subscription.customer_id == user.user_id).first()
                
                if not subscription_data:
                    return UpdateSubscription(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find subscription with id {subscription_id}."
                    )
                
                if customer_id:
                    subscription_data.customer_id = customer_id
                
                if customer_name:
                    subscription_data.customer_name = customer_name
                    
                if customer_address:
                    subscription_data.customer_address = customer_address
                
                # now adding subscription_item_details to table.
                subscription_items_data = session.query(SubscribedItems).filter(SubscribedItems.subscription_id == subscription_id).first()
                
                if item_name:
                    subscription_items_data.item_name = item_name
                
                if item_id:
                    subscription_items_data.items_id = item_id
                
                if item_price:
                    subscription_items_data.item_price = item_price
                
                if item_unit:
                    subscription_items_data.item_unit = item_unit
                
                if item_weight:
                    subscription_items_data.item_weight = item_weight
                
                if item_quantity:
                    subscription_items_data.item_quantity = item_quantity
                    
                if frequency:
                    subscription_items_data.frequency = frequency
                
                if subscription_from:
                    subscription_items_data.subscription_from = datetime.datetime.strptime(subscription_from,"%Y-%m-%d")
                    
                if subscription_to:
                    subscription_items_data.subscription_to = datetime.datetime.strptime(subscription_to,"%Y-%m-%d")
                
                
                session.add(subscription_data)
                session.add(subscription_items_data)
                session.commit()
                session.refresh(subscription_data)
                
            return UpdateSubscription(
                status = "success",
                status_code = 201,
                message = f"successfully updated subscription for id {subscription_id}",
                subscription_data = subscription_data
            )
        except:
            session.rollback()
            return UpdateSubscription(
                status = "failed",
                status_code = 404,
                message = "failed to update subscription."
            ) 
                                

# Write Mutation to delete subscription.
class DeleteSubscription(Mutation):
    """
    Mutation for deleting the subscription
    """
    class Arguments:
        subscription_id = Int(required = True)
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,subscription_id):
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return DeleteSubscription(
                status = "faield",
                status_code = 404,
                message = "failed to delete Subscription."
            )
        try:
            with Session() as session:
                subscription_data = session.query(Subscription).filter(Subscription.id == subscription_id and Subscription.customer_id == user.user_id).first()
                
                if not subscription_data:
                    return DeleteSubscription(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find subscription with id {subscription_id}"
                    )
                
                session.delete(subscription_data)
                session.commit()
            return DeleteSubscription(
                status = "success",
                status_code = 200,
                message = f"subscription with id {subscription_id} has been deleted."
            )
        except:
            session.rollback()
            
            return DeleteSubscription(
                status = 'failed',
                status_code = 404,
                message = "failed to delete subscription."
            )
        