from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel


class Cake(BaseModel):
    id: int
    name: str
    comment: str
    imageUrl: str
    yumFactor: int = 0


class CakeCreate(BaseModel):
    name: str
    comment: str
    imageUrl: str
    yumFactor: int = 0


DATABASE_URL = ("sqlite:///cakes")


class Base(DeclarativeBase):
    pass

# model
class DBItem(Base):
    __tablename__ ="cakes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30))
    comment: Mapped[str] = mapped_column(String(200))
    imageUrl: Mapped[str] = mapped_column(String(200))
    yumFactor: Mapped[int] = mapped_column()


# create the database
engine = create_engine(DATABASE_URL)
# create the tables
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Cake API",
    description="A simple API that manages cakes",
    version="0.1",
    docs_url="/",
)
                    
# Dependency to get the database session
def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@app.get("/cakes/")
async def get_cakes(db: Session = Depends(get_db)):
    db_cake = db.query(DBItem).all()
    if db_cake is None:
        raise HTTPException(status_code=404, detail=f"Get no cakes found ")
    return Cake(**db_cake.__dict__)


@app.get("/startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.post("/cakes/")
async def create_item(item: CakeCreate, db: Session = Depends(get_db)) -> Cake:
    db_cake = DBItem(**item.model_dump())
    db.add(db_cake)
    db.commit()
    db.refresh(db_cake)
    return Cake(**db_cake.__dict__)


@app.get("/cakes/{cake_id}")
async def read_item(cake_id: int, db: Session = Depends(get_db)) -> Cake:
    db_cake = db.query(DBItem).filter(DBItem.id == cake_id).first()
    if db_cake is None:
        raise HTTPException(status_code=404, detail=f"Get Cake not found {cake_id}")
    return Cake(**db_cake.__dict__)

@app.delete("/cakes/{cake_id}")
async def delete_item(cake_id: int, db: Session = Depends(get_db)) -> Cake:
    db_cake = db.query(DBItem).filter(DBItem.id == cake_id).first()
    if db_cake is None:
        raise HTTPException(status_code=404, detail="Delete Cake not found")
    db.delete(db_cake)
    db.commit()
    return Cake(**db_cake.__dict__)
