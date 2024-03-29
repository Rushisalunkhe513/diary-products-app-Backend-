from datetime import datetime
from app.utils import password_hash

default_admin = [{
    "id": 1,
    "admin_name":"SuperAdmin",
    "admin_mobile_number":"9876543210",
    "admin_pin_hash":password_hash("admin@2024"),
    "created_at":datetime.now()
}]