from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.api.schemas import ProgramRunRequest
from language.parser.parser_errors import ParserError
from language.runtime.runtime_errors import RuntimeLanguageError
from language.semantic.semantic_errors import SemanticError

try:
    from language.lexer.lex_err import LexerError
except ImportError:
    from language.lexer.lex_err import LexerError


router = APIRouter(prefix="/api/interpreter", tags=["interpreter"])

#HTTP endpoint запуска програмыы
@router.post("/run")
async def run_program(payload: ProgramRunRequest, request: Request):
    try:
        return await request.app.state.interpreter_service.run(payload.source)
    except (LexerError, ParserError, SemanticError, RuntimeLanguageError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
