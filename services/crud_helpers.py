from collections.abc import Callable
from typing import Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

TSchema = TypeVar("TSchema", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)


def register_uuid_crud(
    *,
    prefix: str,
    tag: str,
    orm_model: type,
    create_schema: type[BaseModel],
    response_schema: type[BaseModel],
    to_orm: Callable[[BaseModel], dict[str, Any]],
    to_response: Callable[[Any], BaseModel],
    get_db: Callable,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=list[response_schema])
    def list_items(db: Session = Depends(get_db)):
        rows = db.query(orm_model).all()
        return [to_response(row) for row in rows]

    @router.get("/{item_id}", response_model=response_schema)
    def get_item(item_id: UUID, db: Session = Depends(get_db)):
        row = db.query(orm_model).filter(orm_model.id == item_id).first()
        if not row:
            raise HTTPException(status_code=404, detail=f"{tag} not found")
        return to_response(row)

    @router.post("", response_model=response_schema, status_code=201)
    def create_item(data: create_schema, db: Session = Depends(get_db)):
        row = orm_model(**to_orm(data))
        db.add(row)
        db.commit()
        db.refresh(row)
        return to_response(row)

    @router.put("/{item_id}", response_model=response_schema)
    def update_item(item_id: UUID, data: create_schema, db: Session = Depends(get_db)):
        row = db.query(orm_model).filter(orm_model.id == item_id).first()
        if not row:
            raise HTTPException(status_code=404, detail=f"{tag} not found")
        for key, value in to_orm(data).items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return to_response(row)

    @router.delete("/{item_id}")
    def delete_item(item_id: UUID, db: Session = Depends(get_db)):
        row = db.query(orm_model).filter(orm_model.id == item_id).first()
        if not row:
            raise HTTPException(status_code=404, detail=f"{tag} not found")
        db.delete(row)
        db.commit()
        return {"deleted": item_id}

    return router
