from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models, database, auth
from typing import List
import datetime

# Inicializa Banco de Dados
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Almox 360 Pro")

# CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- DEPENDÊNCIAS ---
def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- ROTAS DE AUTENTICAÇÃO ---
@app.post("/token")
async def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.post("/register-initial-admin")
def register_initial_admin(db: Session = Depends(database.get_db)):
    if db.query(models.User).count() == 0:
        admin = models.User(
            username="admin",
            hashed_password=auth.get_password_hash("123456"),
            role="ADMIN"
        )
        db.add(admin)
        db.commit()
        return {"msg": "Admin inicial criado: admin / 123456"}
    return {"msg": "Já existem usuários cadastrados"}

# --- ROTAS DE PRODUTOS ---
@app.get("/products")
def list_products(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Product).all()

@app.post("/products")
def create_product(
    name: str, category: str, location: str, stock: float, min_stock: float, obs: str = "",
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Lógica de geração de código automática
    prefix = category[:3].upper()
    count = db.query(models.Product).filter(models.Product.category == category).count()
    code = f"{prefix}-{(count + 1):04d}"
    
    new_prod = models.Product(
        code=code, name=name, category=category, location=location, 
        stock=stock, min_stock=min_stock, observation=obs
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod

# --- ROTAS DE MOVIMENTAÇÃO (SINCRONIZAÇÃO) ---
@app.post("/sync/movements")
def sync_movements(
    movements: List[dict], 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Recebe uma lista de movimentações (pode ser uma ou várias vindas do offline)
    """
    results = []
    for mov in movements:
        prod = db.query(models.Product).filter(models.Product.code == mov['product_code']).first()
        if not prod:
            results.append({"code": mov.get('local_id'), "status": "error", "msg": "Produto não encontrado"})
            continue
        
        prev_stock = prod.stock
        if mov['type'] == 'SAIDA':
            if prod.stock < mov['quantity']:
                results.append({"code": mov.get('local_id'), "status": "error", "msg": "Estoque insuficiente"})
                continue
            prod.stock -= mov['quantity']
            if "FERRAMENT" in prod.category.upper():
                prod.in_use += mov['quantity']
        else:
            prod.stock += mov['quantity']
            
        new_history = models.History(
            product_id=prod.id,
            type=mov['type'],
            quantity=mov['quantity'],
            responsible=mov['responsible'],
            previous_stock=prev_stock,
            current_stock=prod.stock,
            location=prod.location,
            date=datetime.datetime.fromisoformat(mov['date']) if 'date' in mov else datetime.datetime.utcnow()
        )
        db.add(new_history)
        results.append({"code": mov.get('local_id'), "status": "success"})
    
    db.commit()
    return results

@app.get("/stats")
def get_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    total_items = db.query(models.Product).count()
    items_alert = db.query(models.Product).filter(models.Product.stock <= models.Product.min_stock).count()
    in_use = db.query(models.Product).filter(models.Product.category.like("%FERRAMENT%")).sum(models.Product.in_use) # Simplificado
    mov_today = db.query(models.History).filter(models.History.date >= datetime.date.today()).count()
    
    return {
        "total": total_items,
        "alert": items_alert,
        "in_use": in_use or 0,
        "today": mov_today
    }

# Montar arquivos estáticos para o frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
