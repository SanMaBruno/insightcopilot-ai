from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from src.application.use_cases.index_document_use_case import IndexDocumentUseCase
from src.domain.repositories.document_indexer import DocumentIndexer
from src.domain.repositories.file_storage import FileStorage
from src.presentation.api.dependencies import get_document_indexer, get_file_storage
from src.presentation.api.schemas.document import (
    DocumentIndexRequest,
    DocumentIndexResponse,
    DocumentUploadResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])

_ALLOWED_EXTENSIONS = {".txt", ".md"}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile,
    storage: FileStorage = Depends(get_file_storage),  # noqa: B008
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido.")

    ext = ""
    dot_idx = file.filename.rfind(".")
    if dot_idx >= 0:
        ext = file.filename[dot_idx:].lower()

    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Solo se permiten archivos {', '.join(sorted(_ALLOWED_EXTENSIONS))}.",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    file_path = storage.save(file.filename, content)
    return DocumentUploadResponse(source=file.filename, file_path=file_path)


@router.post("/index", response_model=DocumentIndexResponse)
def index_document(
    body: DocumentIndexRequest,
    indexer: DocumentIndexer = Depends(get_document_indexer),  # noqa: B008
) -> DocumentIndexResponse:
    import os

    if not os.path.isfile(body.file_path):
        raise HTTPException(
            status_code=404, detail=f"Archivo no encontrado: {body.file_path}"
        )

    with open(body.file_path, encoding="utf-8") as f:
        content = f.read()

    source = os.path.basename(body.file_path)

    count = IndexDocumentUseCase(indexer=indexer).execute(
        source=source,
        content=content,
        chunk_size=body.chunk_size,
        overlap=body.overlap,
    )

    return DocumentIndexResponse(source=source, chunks_indexed=count)
