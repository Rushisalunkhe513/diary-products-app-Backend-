from argon2 import PasswordHasher
from datetime import datetime,timedelta
import random
from dotenv import load_dotenv
import os
import requests

from graphql import GraphQLError

from app.db.models import UserObject,AdminModel,UserSession,AdminSession

from app.db.blocklist import BlockList





import jwt

ph = PasswordHasher()

load_dotenv()

# function to store otp in cache
def store_otp(mobile_number,otp,r_client):
    # store
    try:
        store = r_client.set(mobile_number,otp,exp=60)
        return True
    except:
        return False
    
# verify otp by fetching otp from redis
def verify_otp(mobile_number,otp,r_client):
    # verify otp
    
    get_otp = r_client.get(mobile_number)
    if get_otp == otp:
        return True
    else:
        return False

def password_hash(password):
    secured_password =  ph.hash(password)
    return secured_password

def validate_password(hidden_password,password):
    return ph.verify(hidden_password,password)

# lets calculate exact price for the item.

def calculate_price(mrp,discount):
    price = mrp - mrp*(discount/100)
    return price

# now lets write function to genrate interesting order_id with year,date,month in it.
def genrate_order_id():
    order_time = datetime.now().strftime("%Y%m%d") # we are taking today date in year,month and date in string format by strftime.
    # lets get random 7 digit number.
    rand_7_digit_number = random.randint(1000000,9999999)
    
    order_id = f"{order_time}-{rand_7_digit_number}"
    
    return order_id


# create unique wallet id.
def genrate_wallet_id(name):
    rand_num = random.randint(1000,9999)
    wallet_id = f"{name}-{rand_num}"
    return wallet_id
    
    


# genrate access token and refresh token for user.
def gen_user_access_and_refresh_token(id, user_mobile_number,acc_exp_time,ref_exp_time,role):
    
    """
    payload = payload is what we need to store inside token, like user related data and more.
    secret_key = secret_key is a secret that stored inside the token to generate and decode token.
    algorothm = there is multiple type of algorithm used but most basically used algorithm is HS256. it is complexity type for token.
    
    Generate user access and refresh tokens.
    
    Parameters:
        id (int): User ID.
        user_name (str): User name.
        role = "user" or  "admin"    
    Returns:
        list: List containing access token and refresh token.
    """
    # Get secret key and algorithm from environment variables
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    
    # (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_ACCESS_TIME")))).isoformat()
    # Generate access token payload
    access_token_payload = {
        "user_id": id,
        "user_mobile_number": user_mobile_number,
        "token_type":"access",
        "role":role,
        "exp_time":   acc_exp_time # Convert to ISO 8601 format
    }
    
    # Encode access token
    access_token = jwt.encode(access_token_payload, secret_key, algorithm)
    
    # Generate refresh token payload
    refresh_token_payload = {
        "user_id": id,
        "user_mobile_number": user_mobile_number,
        "token_type":"refresh",
        "role":role,
        "exp_time": ref_exp_time  # Convert to ISO 8601 format
    }
    
    # Encode refresh token
    refresh_token = jwt.encode(refresh_token_payload, secret_key, algorithm)
    
    # Return both tokens
    return {
        "access_token":access_token,
        "refresh_token":refresh_token
    }

# tokens = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX21vYmlsZV9udW1iZXIiOiJrZXNoYXYiLCJyb2xlIjoidXNlciIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJleHBfdGltZSI6IjIwMjQtMDMtMjVUMTM6MzY6NTkuOTE4MzU3In0.t9jTn6AndcHx1DmrOWvlwogkfQp-xXtBqKKdgL1zmB8"
# lets write function to decode tokens.
def decode_tokens(token):
        secret_key = os.getenv("SECRET_KEY")
        algorithm = os.getenv("ALGORITHM")
        
        payload = jwt.decode(token,secret_key,algorithm)
        return payload

        
# token_data = decode_tokens(tokens)
# print(datetime.now()>datetime.strptime(token_data["exp_time"],'%Y-%m-%dT%H:%M:%S.%f'))
# for access token to access resorces
# for refresh token to genrate new tokens for user and admin

# get authenticated user or admin access only.
def get_authenticated_admin(context,Session):
    
    # get token in request form
    request_data = context.get("request")
    
    session = Session()
    # get token data from authoriation
    token_data = request_data.headers.get("Authorization")
    
    if token_data:
        token_values = token_data.split(" ")
        
        if token_values[0] == "Bearer" and len(token_values) == 2:
            token_details = decode_tokens(token_values[1])
            
            user = session.query(UserSession).filter(UserSession.user_id == token_details["user_id"] and UserSession.token_holder_mobile_number == token_details["user_mobile_number"]).first()
            admin = session.query(AdminSession).filter(AdminSession.admin_id == token_details["user_id"] and AdminSession.token_holder_mobile_number == token_details["user_mobile_number"]).first()
            if (user.access_token == token_values[1] or admin.access_token == token_values[1]) and token_details["token_type"] == "access":
                
                if datetime.now()>datetime.strptime(token_details["exp_time"],"%Y-%m-%dT%H:%M:%S.%f"):
                    print("*****************************************>>>>>",True if datetime.strptime(token_details["exp_time"],"%Y-%m-%dT%H:%M:%S.%f") < datetime.now() else False)
                    return GraphQLError("Token Has Expired")
                
                
                else:
                    
                        if token_details["role"] == "user":
                            user_details = session.query(UserObject).filter(UserObject.mobile_number == token_details["user_mobile_number"]).first()
                            
                            if not user_details:
                                return False
                            else:
                                return user_details        
                        else:
                            admin_details = session.query(AdminModel).filter(AdminModel.admin_mobile_number == token_details["user_mobile_number"]).first()
                            
                            if not admin_details:
                                return False
                            else:
                                return admin_details
            else:
                return False
                        
        else:
            return jwt.InvalidTokenError("Invalid Token Format")
        
            
def token_for_new_acc_ref_token(context,Session):
    # to genrate new tokens after current one is expired use refresh token to get new access token and refresh token.
    # rather than making user login again after expiry of his/her access token.
    
    request_data = context.get("request")
    
    # now get data from authorization key.
    token_data = request_data.headers.get('Authorization')
    
    if token_data:
        token_values = token_data.split(" ")
        
    if token_values[0] == "Bearer" and len(token_values) == 2:
        token_details = decode_tokens(token_values[1])
        
        with Session() as session:
            user_session = session.query(UserSession).filter(UserSession.refresh_token == token_values[1]).first()
            admin_session = session.query(AdminSession).filter(AdminSession.refresh_token == token_values[1]).first()
        
            if user_session or admin_session:
                if token_values[1] in BlockList:
                    return GraphQLError("token can not be used ")
                
                if datetime.strptime(token_details["exp_time"],"%Y-%m-%dT%H:%M:%S.%f") < datetime.now():
                    return GraphQLError("token has been expired")
                
                if token_details["token_type"] == "access":
                    return GraphQLError("wrong token is being used for getting new access and refresh token.")
                
                
                user = session.query(UserObject).filter(UserObject.id == token_details["user_id"] and UserObject.mobile_number == token_details["user_mobile_number"]).first()
                admin = session.query(AdminModel).filter(AdminModel.id == token_details["user_id"] and AdminModel.admin_mobile_number == token_details["user_mobile_number"]).first()
                if not user:
                    acc_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("ADMIN_EXP_ACCESS_TIME")))).isoformat()
                    ref_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("ADMIN_EXP_REF_TIME")))).isoformat()
                    new_tokens = gen_user_access_and_refresh_token(admin.id,admin.admin_mobile_number,acc_exp_time,ref_exp_time,role = "admin")
                    print(new_tokens["access_token"],"*************************************************************************")
                    add_tokens_to_admin_session(new_tokens["access_token"],new_tokens["refresh_token"],admin.admin_mobile_number,admin.id,admin.admin_name,Session)
                    return new_tokens
                if not admin:
                    acc_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_ACCESS_TIME")))).isoformat()
                    ref_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_REF_TIME")))).isoformat()
                    new_tokens = gen_user_access_and_refresh_token(user.id,user.mobile_number,acc_exp_time,ref_exp_time,role = "user")
                    print(new_tokens,"*************************************************************************")
                    add_tokens_to_user_session(new_tokens["access_token"],new_tokens["refresh_token"],user.mobile_number,user.id,user.first_name,Session)
                    return new_tokens
    else:
        return GraphQLError("wrong payload in header.")
    

    
# function to add tokeen to user session.
def add_tokens_to_user_session(access_token,refresh_token,mobile_number,token_holder_id,token_holder_name,Session):
    # lets seee token is already in session or not.
        with Session() as session:
            print("Inside session")
            check_existing_session_for_user = session.query(UserSession).filter(UserSession.user_id == token_holder_id).first()
            if check_existing_session_for_user:
                session.delete(check_existing_session_for_user)
                session.commit()
                session.add(
                    UserSession(
                        access_token = access_token,
                        refresh_token = refresh_token,
                        token_holder_mobile_number = mobile_number,
                        token_holder_name = token_holder_name,
                        user_id = token_holder_id
                    
                    )
                )
                print("deleted existing session")
                session.commit()
                session.close()
                
            else:
                session.add(
                    UserSession(
                        access_token = access_token,
                        refresh_token = refresh_token,
                        token_holder_mobile_number = mobile_number,
                        token_holder_name = token_holder_name,
                        user_id = token_holder_id
                )
                )
                print("session has been created")
                session.commit()
                session.close()
        return True
                
    
       
    

# add token to admin session.
def add_tokens_to_admin_session(access_token,refresh_token,mobile_number,token_holder_id,token_holder_name,Session):
    # lets seee token is already in session or not.
        with Session() as session:
            print("Inside session")
            check_existing_session_for_admin = session.query(AdminSession).filter(AdminSession.token_holder_mobile_number == mobile_number).first()
            if check_existing_session_for_admin:
                session.delete(check_existing_session_for_admin)
                session.commit()
                session.add(
                    AdminSession(
                        access_token = access_token,
                        refresh_token = refresh_token,
                        token_holder_mobile_number = mobile_number,
                        token_holder_name = token_holder_name,
                        admin_id = token_holder_id
                    
                    )
                )
                print("deleted existing session")
                session.commit()
                session.close()
                
            else:
                session.add(
                    AdminSession(
                        access_token = access_token,
                        refresh_token = refresh_token,
                        token_holder_mobile_number = mobile_number,
                        token_holder_name = token_holder_name,
                        admin_id = token_holder_id
                )
                )
                print("session has been created")
                session.commit()
                session.close()
        return True

# function to add token to block_list after user logout so, user never logs out again:-
def add_tokens_to_blocklist(access_token,refresh_tokens):
    # lets add token to blocklist so,they cant be used again.
    
    if len(BlockList) != 0:
        for token in BlockList:
            token_details = decode_tokens(token)
            if datetime.strptime(token_details["exp_time"],"%Y-%m-%dT%H:%M:%S.%f") < datetime.now():
                BlockList.remove(token)
    else:
        acc_token = decode_tokens(access_token)
        ref_token = decode_tokens(refresh_tokens)
        if acc_token["user_id"] == ref_token["user_id"]:
            BlockList.append(access_token)
            BlockList.append(refresh_tokens)
    
    return True


# lets give admin some privalages.
def admin_privaleges(context,Session):
    
     # get token in request form
    request_data = context.get("request")
    
    session = Session()
    # get token data from authoriation
    token_data = request_data.headers.get("Authorization")
    
    if token_data:
        token_values = token_data.split(" ")
        
        if token_values[0] == "Bearer" and len(token_values) == 2:
            token_details = decode_tokens(token_values[1])
            
            if token_details["role"] == "admin":
                admin = session.query(AdminSession).filter(AdminSession.admin_id == token_details["user_id"] and AdminSession.token_holder_mobile_number == token_details["user_mobile_number"]).first()
                if  admin.access_token == token_values[1] and token_details["token_type"] == "access":
                    
                    if datetime.now()>datetime.strptime(token_details["exp_time"],"%Y-%m-%dT%H:%M:%S.%f"):
                        return GraphQLError("Token Has Expired")
                    else:
                                
                        admin_details = session.query(AdminModel).filter(AdminModel.admin_mobile_number == token_details["user_mobile_number"]).first()
                                
                        if not admin_details:
                            return False
                        else:
                            return admin_details
            else:
                return False
                        
        else:
            return jwt.InvalidTokenError("Invalid Token Format")
            