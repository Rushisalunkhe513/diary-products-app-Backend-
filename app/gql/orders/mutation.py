from graphene import Int,String,Field,List,Float,ObjectType,Mutation

from app.utils import genrate_order_id

from app.db.models import OrderDetails,OrderItemModel,ItemDetailModel,WalletModel,UserWalletTransactions,UserObject
from app.db.database import Session

from app.gql.orders.types import OrderData,OrderDataInput

from datetime import datetime

from app.utils import get_authenticated_admin




# leys write mutation to add order to database.
class PlaceOrder(Mutation):
    
    """
    Mutation to place the order.
    """
    class Arguments:
        order_data = OrderDataInput()
    
    status = String()
    status_code = Int()
    message = String()
    order_output = Field(lambda:OrderData)
    
    @staticmethod
    def mutate(root, info, order_data):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return PlaceOrder(
                status = "faield",
                status_code = 404,
                message = "failed to place order."
            )
            
        try:
            with Session() as session:
                gen_order_id = genrate_order_id()
                payment_status = "pending" if order_data.payment_mode == "COD" else "successful"
                user = session.query(UserObject).filter(UserObject.mobile_number == user.user_mobile_number).first()
                if user:
                    order_details = OrderDetails(
                        order_id=gen_order_id,
                        customer_id=order_data.customer_id,
                        customer_mobile_number=order_data.customer_mobile_number,
                        customer_name=order_data.customer_name,
                        order_time=datetime.now(),
                        order_status=order_data.order_status,
                        payment_mode=order_data.payment_mode,
                        payment_status=payment_status,
                        shipping_address=order_data.shipping_address,
                        shipping_details=order_data.shipping_details,
                    )

                    total_order_price = 0  # Move this outside the loop

                    for item_details in order_data.order_items:
                        order_items_data = OrderItemModel(
                            order_id=gen_order_id,
                            item_name=item_details.item_name,
                            item_id=item_details.item_id,
                            item_quantity=item_details.item_quantity,
                            item_price=item_details.item_price,
                            item_mrp=item_details.item_mrp,
                            item_discount=item_details.item_discount
                        )
                        total_order_price += item_details.item_price  # Accumulate total order price
                        
                        # Check if item quantity is sufficient
                        item_quantity = session.query(ItemDetailModel).filter(ItemDetailModel.id == item_details.item_id).first()
                        if not item_quantity or item_quantity.quantity < item_details.item_quantity:
                            session.rollback()  # Rollback transaction
                            return PlaceOrder(
                                status="failed",
                                message=f"Item with ID {item_details.item_id} doesn't have sufficient quantity."
                            )
                        else:
                            item_quantity.quantity = item_quantity.quantity - item_details.item_quantity
                        

                        order_details.order_items.append(order_items_data)
                    if order_data.payment_mode == "wallet":
                        wallet_data = session.query(WalletModel).filter(WalletModel.user_id == order_data.customer_id).first()
                        # wallet_transaction = session.query(UserWalletTransactions).filter(UserWalletTransactions.user_id == order_data.customer_id).first()
                        if wallet_data.balance >= total_order_price and wallet_data.balance > 0:
                            wallet_data.balance = wallet_data.balance - total_order_price
                            # wallet_data.updated_at = datetime.now()
                            wallet_transaction = UserWalletTransactions(
                                user_id = order_data.customer_id,
                                updated_at = datetime.now(),
                                amount_change = f"-{total_order_price}",
                                wallet_id = wallet_data.wallet_id
                            )
                        else:
                            return PlaceOrder(
                                status = "failed",
                                status_code = 404,
                                message = f"failed to place order due to wallet balance is less than order total."
                            )

                    order_details.order_total = total_order_price
                    
                    session.add(wallet_transaction)
                    session.add(wallet_data)
                    session.add(item_quantity)
                    session.add(order_details)
                    session.commit()
                    session.refresh(order_details)

            return PlaceOrder(
                status="successful",
                order_output=order_details,
                status_code = 201,
                message = "your order has been placed."
            )
        except:
            session.rollback()
            return PlaceOrder(
                status = "failed",
                status_code = 404,
                message = "failed to place the order."
            )



# Mutation for updateing the order.
class UpdateOrder(Mutation):
    """
    Mutation to update the order by order_id
    """
    class Arguments:
        order_id = String(required = True)
        customer_id =  Int()
        customer_name = String()
        customer_mobile_number = String()
        payment_mode = String()
        payment_status = String()
        shipping_address = String()
        shipping_details = String()
        order_status = String()
        order_total = Float()
    
    status = String()
    status_code = Int()
    message = String()
    updated_order = Field(lambda:OrderData)
    
    @staticmethod
    def mutate(root,info,
               order_id,
               customer_id,
               customer_name,
               customer_mobile_number,
               payment_mode,
               payment_status,
               shipping_address,
               shipping_details,
               order_status,
               order_total):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return UpdateOrder(
                status = "faield",
                status_code = 404,
                message = "failed to update order."
            )
            
        try:
            with Session() as session:
                
                order_data_by_id = session.query(OrderDetails).filter(OrderDetails.order_id == order_id and OrderDetails.customer_id == user.user_id).first()
                
                if not order_data_by_id:
                    return UpdateOrder(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find order with {order_id}."
                    )

                if customer_id:
                    order_data_by_id.customer_id = customer_id
                
                if customer_name:
                    order_data_by_id.customer_name = customer_name
                
                if customer_mobile_number:
                    order_data_by_id.customer_mobile_number = customer_mobile_number
                
                if payment_mode:
                    order_data_by_id.payment_mode = payment_mode
                    
                if payment_status:
                    order_data_by_id.payment_status = payment_status
                
                if shipping_address:
                    order_data_by_id.shipping_address = shipping_address
                
                if shipping_details:
                    order_data_by_id.shipping_details = shipping_details
                
                if order_status:
                    order_data_by_id.order_status = order_status
                
                if order_total:
                    order_data_by_id.order_total = order_total
                    
                # now lets add updated data to the database.
                    
                session.add(order_data_by_id)
                session.commit()
                session.refresh(order_data_by_id)
            
            return UpdateOrder(
                status = "success",
                status_code = 201,
                message = f"order with id {order_id} has been updated succesfully.",
                updated_order = order_data_by_id
            ) 
        except:
            session.rollback()
            return UpdateOrder(
                status = "failed",
                status_code = 404,
                message = f"order with id {order_id} has been failed to update."
            )
                
                
                
# lets write the mutation to delete the order by its order_id.
class DeleteOrder(Mutation):
    """
    Mutation to delete the order by its order_id
    """
    class Arguments:
        order_id = String()
        
    status = String()
    status_code = Int()
    message = String()

    @staticmethod
    def mutate(root,info,
               order_id):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return DeleteOrder(
                status = "faield",
                status_code = 404,
                message = "failed to delete order."
            )
            
        try:
            with Session() as session:
                order_data = session.query(OrderDetails).filter(OrderDetails.order_id == order_id and OrderDetails.customer_id == user.user_id).first()
                
                if not order_data:
                    return DeleteOrder(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find the order with {order_id}."
                    )
                session.delete(order_data)
                session.commit()
            return DeleteOrder(
                status = "success",
                status_code = 200,
                message = f"order with id {order_id} has been deleted."
            )
        except:
            session.rollback()
            return DeleteOrder(
                status = "failed",
                status_code = 404,
                message = f"can not delete order with id {order_id}"
            )