from graphene import Int, String,List,Field,ObjectType,InputObjectType,Float,DateTime



    
    
# input object type
class SubscribedItemsInput(InputObjectType):
    # subscription_id = Int()
    item_name = String()
    item_id = Int()
    item_price = Float()
    item_unit = String()
    item_weight = String()
    item_quantity = Int()
    frequency = String()
    subscription_from = String()
    subscription_to = String()
    
class SubscriptionInput(InputObjectType):
    customer_name = String()
    customer_id = Int()
    customer_address = String()
    subscribed_items_input = List(SubscribedItemsInput)
    