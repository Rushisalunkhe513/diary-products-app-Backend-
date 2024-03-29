from graphene import String,Int,Float,Field,List,ObjectType,InputObjectType,DateTime


class OrderItems(ObjectType):
    id = Int()
    order_id = String()
    item_id = Int()
    item_name = String()
    item_quantity = Int()
    item_price = Float()
    item_mrp = Float()
    item_discount = Float()

class OrderData(ObjectType):
    order_id = String()
    customer_id = Int()
    customer_name = String()
    customer_mobile_number = String()
    order_total = Float()
    order_time = DateTime()
    order_status = String()
    payment_mode = String()
    payment_status = String()
    shipping_address = String()
    shipping_details = String()
    order_items = List(lambda:OrderItems)
    
    @staticmethod
    def resolve_order_items(root,info):
        return root.order_items
    
    
class OrderItemsInput(InputObjectType):
    item_id = Int()
    item_name = String()
    item_quantity = Int()
    item_price = Float()
    item_mrp = Float()
    item_discount = Float()
    
class OrderDataInput(InputObjectType):
    customer_id = Int()
    customer_name = String()
    customer_mobile_number = String()
    order_status = String()
    payment_mode = String()
    shipping_address = String()
    shipping_details = String()
    order_items = List(OrderItemsInput) # we can list as many iems in single order as we want.
    
    