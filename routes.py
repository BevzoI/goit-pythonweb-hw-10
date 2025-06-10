from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/contacts", response_model=schemas.ContactOut)
def create(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@router.get("/contacts", response_model=list[schemas.ContactOut])
def list_contacts(query: str = None, db: Session = Depends(get_db)):
    if query:
        return crud.search_contacts(db, query)
    return crud.get_all_contacts(db)

@router.get("/contacts/{contact_id}", response_model=schemas.ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    return crud.update_contact(db, contact_id, contact)

@router.delete("/contacts/{contact_id}")
def delete(contact_id: int, db: Session = Depends(get_db)):
    crud.delete_contact(db, contact_id)
    return {"message": "Contact deleted"}

@router.get("/contacts/upcoming-birthdays", response_model=list[schemas.ContactOut])
def birthdays(db: Session = Depends(get_db)):
    return crud.upcoming_birthdays(db)
