from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy import extract

from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "API is running. Use /docs to explore endpoints."}

# Create a new contact
@app.post("/contacts/", response_model=schemas.ContactOut)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

# Get all contacts with optional search
@app.get("/contacts/", response_model=List[schemas.ContactOut])
def get_contacts(
    db: Session = Depends(get_db),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None)
):
    return crud.search_contacts(db, first_name, last_name, email)

# Get contact by ID
@app.get("/contacts/{contact_id}", response_model=schemas.ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

# Update contact
@app.put("/contacts/{contact_id}", response_model=schemas.ContactOut)
def update_contact(contact_id: int, updated_contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    contact = crud.update_contact(db, contact_id, updated_contact)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

# Delete contact
@app.delete("/contacts/{contact_id}", response_model=schemas.ContactOut)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.delete_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

# Get contacts with upcoming birthdays
@app.get("/contacts/upcoming_birthdays/", response_model=List[schemas.ContactOut])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    upcoming_date = today + timedelta(days=7)

    contacts = db.query(models.Contact).filter(
        models.Contact.birthday.isnot(None),
        extract('month', models.Contact.birthday) == today.month,
        extract('day', models.Contact.birthday) >= today.day,
        extract('day', models.Contact.birthday) <= upcoming_date.day
    ).all()
    return contacts
