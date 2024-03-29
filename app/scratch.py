# from app.utils import decode_tokens
# from datetime import datetime
# tokens = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX21vYmlsZV9udW1iZXIiOiJrZXNoYXYiLCJyb2xlIjoidXNlciIsInRva2VuX3R5cGUiOiJhY2Nlc3MiLCJleHBfdGltZSI6IjIwMjQtMDMtMjVUMTM6MzY6NTkuOTE4MzU3In0.t9jTn6AndcHx1DmrOWvlwogkfQp-xXtBqKKdgL1zmB8"
# token_data = decode_tokens(tokens)
# print(True if datetime.strptime(token_data["exp_time"],'%Y-%m-%dT%H:%M:%S.%f') > datetime.now() else False)
# # for access token to access resorces
# # for refresh token to genrate ne