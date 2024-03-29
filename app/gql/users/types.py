from graphene import ObjectType,Mutation,Int,String,List,Field,DateTime,InputObjectType



# lets define type for user table.

# type for queries.

class UserInfo(ObjectType):
    """
    This type will only be used in query or in output of any mutation.
    """
    
    id = Int()
    first_name = String()
    last_name = String()
    mobile_number = String()
    land_mark = String()
    city = String()
    pincode = String()
    address = String()
    

    
# for delete

class MessageStatus(ObjectType):
    status = String()
    status_code = Int()
    message = String()
    
    
# types to Mutation

class UserInput(ObjectType):
    "This type will be used for mutation"
    
    first_name = String()
    last_name = String()
    mobile_number = String()
    pin = String() # pin should be hidden.
    land_mark = String()
    city = String()
    pincode = Int()
    address = String()
    
    
class AdminType(ObjectType):
    id = Int()
    admin_name = String()
    admin_mobile_number = String()
    created_at = DateTime()


    