from graphene import Int,String,List,Field,ObjectType,Mutation



class BannerOutpt(ObjectType):
    id = Int()
    name = String()
    image_url = String()

    
