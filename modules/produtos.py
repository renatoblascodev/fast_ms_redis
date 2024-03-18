from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from typing import List
from connection import redis
from redis_om import HashModel
from pydantic import BaseModel

router = APIRouter()

# Definição do modelo de dados do produto
class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

# Classe de modelo Pydantic para validação dos dados de entrada durante a criação de um novo produto
class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

# Classe de modelo Pydantic para representar a resposta da criação de produto
class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    quantity: int

# Operação de criação de produto
@router.post('/products', response_model=ProductResponse)
def create_product(product: ProductCreate):
    new_product = Product(**product.dict())
    new_product.save()
    return new_product

# Operação de leitura de todos os produtos
@router.get('/products', response_model=List[ProductResponse])
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

# Operação de leitura de um produto específico
@router.get('/products/{id}', response_model=ProductResponse)
def get(id: str):
    try:
        product = Product.get(id)
        if product:
            # Modificação aqui para incluir o campo 'id' na resposta
            return ProductResponse(id=product.pk, name=product.name, price=product.price, quantity=product.quantity)
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao buscar o produto")
# Operação de exclusão de produto
@router.delete('/products/{pk}')
def delete_product(pk: str):
    try:
        product = Product.get(pk)
        if product:
            product.delete(pk)
            return JSONResponse(content={"message": "Produto excluído com sucesso"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao excluir o produto")
