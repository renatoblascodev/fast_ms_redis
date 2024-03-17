from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Middleware CORS para permitir solicitações de origens diferentes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com Redis
redis = get_redis_connection(
    host='redis-14317.c302.asia-northeast1-1.gce.cloud.redislabs.com',
    port='14317',
    password='9wSNCkb7ukgJNxosdTQjnQAY5U9ocab7',
    decode_responses=True
)

# Definição do modelo de dados do produto
class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

# Classe de modelo Pydantic para validação dos dados de entrada# Classe de modelo Pydantic para validação dos dados de entrada durante a criação de um novo produto
class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

# Classe de modelo Pydantic para representar a resposta da criação de produto
class ProductResponse(BaseModel):
    name: str
    price: float
    quantity: int

# Operação de criação de produto
@app.post('/products', response_model=ProductResponse)
def create_product(product: ProductCreate):
    new_product = Product(**product.dict())
    new_product.save()
    return new_product



@app.get('/products')
def read_all_products():
    products = Product.all_pks()
    return [format(pk) for pk in products]


def format(pk: str):
    product =  Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name, 
        'price': product.price, 
        'quantity': product.quantity
    }


@app.get('/products/{pk}')
def get(pk: str):
    try:
        product = Product.get(pk)
        if product:
            return product
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao buscar o produto")



# # Operação de leitura de um produto específico
# @app.get('/products/{product_id}', response_model=Product)
# def read_product(product_id: str):
#     product = Product.get(product_id)
#     if product:
#         return product
#     else:
#         raise HTTPException(status_code=404, detail="Produto não encontrado")

# # Operação de atualização de produto
# @app.put('/products/{product_id}', response_model=Product)
# def update_product(product_id: str, product: ProductCreate):
#     existing_product = Product.get(product_id)
#     if existing_product:
#         for key, value in product.dict().items():
#             setattr(existing_product, key, value)
#         existing_product.save()
#         return existing_product
#     else:
#         raise HTTPException(status_code=404, detail="Produto não encontrado")

# # Operação de exclusão de produto
# @app.delete('/products/{product_id}')
# def delete_product(product_id: str):
#     product = Product.get(product_id)
#     if product:
#         product.delete()
#         return {"message": "Produto excluído com sucesso"}
#     else:
#         raise HTTPException(status_code=404, detail="Produto não encontrado")
