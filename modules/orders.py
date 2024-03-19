import pdb
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from typing import List
from connection import redis
from redis_om import HashModel
from pydantic import BaseModel
from starlette.requests import Request
import requests, time
import httpx

router = APIRouter()

# Definição do modelo de dados da ordem
class Order(HashModel):
    product_id: str
    price: float 
    fee:  float 
    total: float 
    quantity: int
    status: str
    class Meta:
        database = redis

# Classe de modelo Pydantic para validação dos dados de entrada durante a criação de uma nova ordem
class OrderCreate(BaseModel):
    product_id: str
    quantity: int


# Classe de modelo Pydantic para representar a resposta da criação da ordem
class OrderResponse(BaseModel):
    product_id: str
    price: float 
    fee:  float 
    total: float 
    quantity: int
    status: str 

# Operação de criação de ordem   
@router.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks): 
    data = await request.json()
    prod =  data['id']
    endpoint_produto = f"http://localhost:8000/products/{prod}"
    async with httpx.AsyncClient() as client:
        req = await client.get(endpoint_produto)
        product = req.json()
        order = Order(
            product_id=data['id'],  
            price=product['price'],
            fee=0.2 * product['price'],
            total=1.2 * product['price'],
            quantity=data['quantity'],  
            status='pending'
        )
        order.save()

        # order_completed(order) 
        # Coloca na fila de execucao
        background_tasks.add_task(order_completed, order)

        return order

def order_completed(order: Order):
    time.sleep(5) # Aguardar 5 segundos para retornar.
    order.status = 'completed'
    order.save() 
    redis.xadd('order_completed', order.dict(), '*')

# Operação de leitura de todos os produtos
@router.get('/orders', response_model=List[OrderResponse])
def read_all_orders():
    orders = Order.all_pks()
    return [format(pk) for pk in orders]

def format(pk: str):
    order =  Order.get(pk)
    return {
        'id': order.pk,
        'product_id': order.product_id,
        'price': order.price, 
        'fee': order.fee,
        'total': order.total, 
        'quantity': order.quantity,
        'status': order.status
    }

# Operação de leitura de um produto específico
@router.get('/orders/{pk}')
def get(pk: str):
    try:
        order = Order.get(pk)
        if order:
            return order
        else:
            raise HTTPException(status_code=404, detail="Ordem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao buscar a ordem")

# Operação de exclusão de produto
@router.delete('/orders/{pk}')
def delete_order(pk: str):
    try:
        order = Order.get(pk)
        if order:
            Order.delete(pk)
            return JSONResponse(content={"message": "Ordem excluída com sucesso"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Ordem não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao excluir a ordem")
