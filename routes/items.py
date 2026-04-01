from fastapi import APIRouter, Depends,Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from typing import List
from schema.items import ItemInsert, ItemResponse,LabelSearch,LabelResponse,StatusUpdateRequest
from services.database import get_connection
from services.s3_services import s3Service
from utils.auth import get_current_user
from typing import List
import json

s3_service = s3Service()
router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/fetch-labels",response_model= LabelResponse,status_code=200)
async def fetch_labels(data: LabelSearch,current_user: dict= Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        """
        Function to get the list of labels on search by user
        """
        search_query = f"%{data.input}%"
        company = data.company
        cursor.execute(
            "SELECT label_name FROM label_list WHERE label_name ILIKE %s AND company = %s ORDER BY label_name",
            (search_query, company)
        )
        results = cursor.fetchall()
        labels = [row['label_name'] for row in results]
        return {"labels": labels}
    finally:
        cursor.close()
        conn.close()


@router.post("/place-order")
async def place_order(
    orders: str = Form(...),  # JSON string of orders
    file: UploadFile = None,
    current_user: dict = Depends(get_current_user)
):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        orders_data = json.loads(orders)
        file_url = None
        
        # Handle file upload if present
        if file and file.filename and len(orders_data) > 0:
            po_number = orders_data[0]['po_number']
            username = current_user['username']
            user_id = current_user['user_id']
            s3_filename = f"{po_number}_{username}"
            
            file_content = await file.read()
            upload_success = await s3_service.file_upload(s3_filename, file_content)
            
            if upload_success:
                file_url = await s3_service.downlaod_file(s3_filename)
            
        print(file_url)

        
        # Process each order item
        for order in orders_data:
            cursor.execute("""
                INSERT INTO orders (order_by, label_name, quantity, size, size_unit, po_number, file_url,status,id,company)
                VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
            """, (
                username,
                order['label_name'],
                order['quantity'],
                order['size'],
                order['size_unit'],
                order['po_number'],
                file_url,
                "NEW",
                user_id,
                current_user['company']
            ))
            
        conn.commit()
        return {"status": "success", "message": "Orders placed successfully"}
    
    except json.JSONDecodeError as e:
        conn.rollback()
        return {"status": "error", "message": f"Invalid JSON in orders: {str(e)}"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()
    
@router.get("/fetch-orders")
async def fetch_order( 
        current_user: dict = Depends(get_current_user)
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        role = current_user['role']
        username = current_user['username']
        company = current_user['company']
        if (role == "admin"):
            cursor.execute("Select * from orders")
            results = cursor.fetchall()
            formatted_orders = []
            for row in results:
                formatted_orders.append({
                    "id": str(row['order_id']), 
                    "label_name": row['label_name'], 
                    "label_image_url": row['file_url'], 
                    "download_url": row['file_url'],
                    "quantity": row['quantity'],
                    "po_number": row['po_number'],
                    "size": row['size'],
                    "status": row['status'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "customer_name": row['order_by'],
                    "company": row['company']
                })
            return jsonable_encoder(formatted_orders)
        
        else:

            cursor.execute("Select * from orders where order_by = %s",
                        (username,)
            )
            results = cursor.fetchall()
            formatted_orders = []
            for row in results:
                formatted_orders.append({
                    "id": str(row['order_id']), 
                    "label_name": row['label_name'],
                    "label_image_url": row['file_url'], 
                    "download_url": row['file_url'],
                    "quantity": row['quantity'],
                    "order_by": row['order_by'],
                    "po_number": row['po_number'],
                    "size": row['size'],
                    "status": row['status'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                })

            return jsonable_encoder(formatted_orders)


    except Exception as e:
        print(f"Error has occured {e}")



@router.post("/update-order-status")
def update_order_status(   
    data: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user)
    ):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        order_id = data.order_id
        status = data.status
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        conn.commit()
        return {"status": "success", "message": f"Order {order_id} status updated to {status}"}
    finally:
        cursor.close()
        conn.close()