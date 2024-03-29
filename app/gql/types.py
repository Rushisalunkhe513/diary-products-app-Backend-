from graphene import List,Field,Int,String,ObjectType,Float,DateTime

# lets create type for ItemModel
class ItemType(ObjectType):
    id = Int()
    name = String()
    description = String()
    image_url = String()
    title = String()
    item_details = List(lambda: ItemDetailType)
    
    @staticmethod
    def resolve_item_details(root,info):
        return root.item_details  # this is actually used to return item_dtails from item model.
    
# lets declare item_details type first
class ItemDetailType(ObjectType):
    id = Int()
    mrp = Float()
    discount = Float()
    price = Float()
    weight=  String()
    unit = String()
    quantity = Int()
    item_id = Int()
    
    
# output object type
class SubscribedItems(ObjectType):
    id = Int()
    subscription_id = Int()
    item_name = String()
    item_id = Int()
    item_price = Float()
    item_unit = String()
    item_weight = String()
    item_quantity = Int()
    frequency = String()
    subscription_from = DateTime()
    subscription_to = DateTime()
    
class SubscriptionOutput(ObjectType):
    id = Int()
    customer_id = Int()
    customer_name = String()
    customer_address = String()
    subscription_time = DateTime()
    # subscribed_items = List(SubscribedItems)
    
    # @staticmethod
    # def resolve_subscribed_items(root, info):
    #     # Assuming root is an instance of Subscription
    #     return root.subscribed_items
    
class ErrorResponse(ObjectType):
    status = String()
    status_code = Int()
    message = String()