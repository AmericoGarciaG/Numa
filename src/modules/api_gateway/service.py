"""API Gateway Service - Business Flow Orchestration (Public Interface).

This module orchestrates business flows by coordinating between
FinanceCore and AIBrain modules.

PROTOCOLO NEXUS: This is the PUBLIC INTERFACE of the APIGateway module.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

# Import the new real AI modules
from src.modules.ai_brain import reasoning
from src.modules.ai_brain import service as ai_brain_service
from src.modules.ai_brain import transcriber
# We validly import finance_core
from src.modules.finance_core import service as finance_core
from src.modules.finance_core.models import Transaction, TransactionType


def _generate_narrative(transactions: List[Transaction]) -> str:
    if not transactions:
        return "No se registró ningún movimiento."

    if len(transactions) == 1:
        t = transactions[0]
        tx_type = getattr(t, "type", None)
        concept = (getattr(t, "concept", "") or "").strip() or "el movimiento"
        amount = getattr(t, "amount", 0.0) or 0.0
        merchant = (getattr(t, "merchant", "") or "").strip()

        if tx_type == TransactionType.INCOME:
            return f"¡Súper! Registré el ingreso de {concept} por ${amount:.2f}."
        if tx_type == TransactionType.DEBT:
            return f"Entendido. Registré la deuda de {concept} por ${amount:.2f}."

        base = f"Listo. Anoté {concept} por ${amount:.2f}"
        if merchant and merchant.lower() != concept.lower():
            base += f" en {merchant}."
        else:
            base += "."
        return base

    expenses: List[Transaction] = []
    incomes: List[Transaction] = []
    debts: List[Transaction] = []

    for t in transactions:
        tx_type = getattr(t, "type", None)
        if tx_type == TransactionType.EXPENSE:
            expenses.append(t)
        elif tx_type == TransactionType.INCOME:
            incomes.append(t)
        elif tx_type == TransactionType.DEBT:
            debts.append(t)

    parts = []

    if expenses:
        total = sum((getattr(t, "amount", 0.0) or 0.0) for t in expenses)
        parts.append(f"{len(expenses)} gastos (${total:,.2f})")

    if incomes:
        total = sum((getattr(t, "amount", 0.0) or 0.0) for t in incomes)
        parts.append(f"{len(incomes)} ingresos (${total:,.2f})")

    if debts:
        total = sum((getattr(t, "amount", 0.0) or 0.0) for t in debts)
        parts.append(f"{len(debts)} deudas (${total:,.2f})")

    if not parts:
        return "Procesé tus movimientos."

    return f"Procesado: {', '.join(parts)}."


# ============================================================================
# VOICE TRANSACTION ORCHESTRATION
# ============================================================================


async def orchestrate_voice_transaction(
    db: Session, audio_file: UploadFile, user_id: int
):
    """Orchestrate the voice-to-transaction flow.

    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz):
    1. Transcribe audio (AIBrain - Google Chirp)
    2. Extract transaction data (AIBrain - Google Gemini)
    3. Create provisional transaction (FinanceCore)

    Args:
        db: Database session
        audio_file: Uploaded audio file
        user_id: ID of the user creating the transaction

    Returns:
        dict: {"data": List[Transaction], "message": str}

    Raises:
        ValueError: If transcription or extraction fails
    """
    audio_bytes = await audio_file.read()
    print(f"DEBUG: Received audio bytes: {len(audio_bytes)}")

    try:
        transcribed_text = await transcriber.transcribe_audio(
            audio_bytes, language="es-MX"
        )
        print(f"DEBUG: STT Result: '{transcribed_text}'")
    except Exception as e:
        print(f"ERROR: STT Failed: {e}")
        transcribed_text = ""

    debug_transcription = transcribed_text or "ERROR"
    debug_analysis = None
    debug_final_action = None

    normalized_transcription = (transcribed_text or "").strip()
    if not normalized_transcription or normalized_transcription.upper() == "ERROR":
        print(
            "[WARN] No valid transcription detected. Aborting voice transaction flow."
        )
        raise ValueError(
            "No pude detectar voz clara en el audio. Por favor intenta de nuevo."
        )

    print(f"DEBUG: Transcribed text: {transcribed_text}")

    try:
        cascade = reasoning.analyze_input_stream(transcribed_text)
        debug_analysis = cascade
        cascade_intent = cascade.get("intent", "WRITE")
        print(f"DEBUG: Cascade analysis: {cascade}")
    except Exception as e:
        print(f"ERROR: Input stream analysis failed: {e}")
        cascade_intent = "WRITE"

    normalized = (transcribed_text or "").strip().lower()

    if cascade_intent == "NOISE":
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": "No te entendí, repítelo por favor.",
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }

    if cascade_intent in ("META", "SOCIAL"):
        chat_message = reasoning.generate_chat_response(
            transcribed_text, mode="CHAT"
        )
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": chat_message,
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }

    if cascade_intent == "READ":
        chat_data = await handle_chat_query(
            db=db, query=transcribed_text, user_id=user_id
        )
        message = chat_data.get(
            "response",
            "Procesé tu consulta financiera.",
        )
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": message,
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }

    if cascade_intent == "AMBIGUOUS":
        if "ingreso" in normalized:
            help_message = "¿De qué fue el ingreso y de cuánto fue?"
        elif "deuda" in normalized:
            help_message = "¿A quién le debes y cuánto es la deuda?"
        else:
            help_message = "¿De qué fue el gasto/ingreso? Necesito más detalles."
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": help_message,
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }

    try:
        extracted_list = reasoning.extract_transaction_data(transcribed_text)
        print(f"DEBUG: Extracted data list: {extracted_list}")
    except reasoning.IncompleteInfoError as e:
        error_reason = str(e) if str(e) else ""
        if "Monto obligatorio" in error_reason:
            message = (
                "Entendí el concepto, pero necesito el monto para registrarlo. "
                "¿Cuánto costó?"
            )
        else:
            message = (
                "Entendí que quieres registrar algo, pero me faltan detalles. "
                "¿Podrías decirme qué fue y cuánto costó?"
            )
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": message,
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }
    except ValueError as e:
        error_text = str(e)
        if (
            "Failed to extract info from text" in error_text
            or "Concepto demasiado genérico y sin monto." in error_text
        ):
            message = (
                "Entendí que quieres registrar algo, pero me faltan detalles. "
                "¿Podrías decirme qué fue y cuánto costó?"
            )
            debug_final_action = "CHAT"
            return {
                "type": "chat",
                "message": message,
                "debug_transcription": debug_transcription,
                "debug_ai_analysis": debug_analysis,
                "debug_final_action": debug_final_action,
            }
        raise
    except Exception as e:
        raise ValueError(f"Data extraction failed: {str(e)}")

    if not extracted_list:
        message = (
            "Entendí que quieres registrar algo, pero me faltan datos. "
            "¿Podrías decirlo de nuevo con el monto y el concepto?"
        )
        debug_final_action = "CHAT"
        return {
            "type": "chat",
            "message": message,
            "debug_transcription": debug_transcription,
            "debug_ai_analysis": debug_analysis,
            "debug_final_action": debug_final_action,
        }

    transactions: List[Transaction] = []
    for item in extracted_list:
        try:
            amount = float(item.get("amount", 0.0))
        except (ValueError, TypeError):
            amount = 0.0

        concept = item.get("concept", "Gasto sin concepto")
        merchant = item.get("merchant")
        if (
            merchant
            and concept
            and merchant.strip().lower() == concept.strip().lower()
        ):
            merchant = None

        transaction_date = None
        date_str = item.get("date")
        if date_str:
            try:
                transaction_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                transaction_date = None

        tx = finance_core.create_provisional_transaction(
            db=db,
            user_id=user_id,
            amount=amount,
            concept=concept,
            transaction_type=TransactionType[item.get("type", "EXPENSE").upper()],
            merchant=merchant,
            category=item.get("category"),
            transaction_date=transaction_date,
        )
        transactions.append(tx)

    narrative = _generate_narrative(transactions)
    debug_final_action = "WRITE"
    return {
        "type": "transaction",
        "data": transactions,
        "message": narrative,
        "debug_transcription": debug_transcription,
        "debug_ai_analysis": debug_analysis,
        "debug_final_action": debug_final_action,
    }


# ============================================================================
# DOCUMENT VERIFICATION ORCHESTRATION
# ============================================================================


async def orchestrate_document_verification(
    db: Session, transaction_id: int, document: UploadFile, user_id: int
):
    """Orchestrate the document verification flow.

    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).
    """
    # Use the placeholder service for now if image analysis not fully implemented in real modules,
    # OR we could implement image analysis in `reasoning.py` too.
    # For this specific task, "Action 1 & 2" only covered Transcriber and Reasoning (Text).
    # So we keep using the `ai_brain_service` placeholder for document logic
    # unless we want to upgrade it to real Gemini Vision now.
    # The prompt explicitly asked for 'transcriber.py' and 'reasoning.py' (text).
    # So we will wrap the legacy/placeholder calls for the document parts to avoid breaking.

    document_bytes = await document.read()
    document_data = ai_brain_service.analyze_document(document_bytes)

    transaction = (
        db.query(finance_core.Transaction)
        .filter(finance_core.Transaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to verify this transaction"
        )

    category = ai_brain_service.classify_category(
        concept=transaction.concept, merchant=document_data.get("vendor")
    )

    verified_transaction = finance_core.verify_transaction_with_document(
        db=db,
        transaction_id=transaction_id,
        amount=document_data.get("total_amount", 0.0),
        merchant=document_data.get("vendor", "Unknown"),
        transaction_date=document_data.get("date", datetime.now()),
        category=category,
    )

    return verified_transaction


# ============================================================================
# MANUAL VERIFICATION ORCHESTRATION
# ============================================================================


async def orchestrate_manual_verification(
    db: Session, transaction_id: int, user_id: int
):
    """Orchestrate the manual verification flow."""
    transaction = (
        db.query(finance_core.Transaction)
        .filter(finance_core.Transaction.id == transaction_id)
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to verify this transaction"
        )

    # Use placeholder or simple logic
    category = ai_brain_service.classify_category(
        concept=transaction.concept, merchant=None
    )

    verified_transaction = finance_core.verify_transaction_manually(
        db=db, transaction_id=transaction_id, category=category
    )

    return verified_transaction


# ============================================================================
# CHAT QUERY ORCHESTRATION
# ============================================================================


async def handle_chat_query(db: Session, query: str, user_id: int) -> dict:
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    analysis = reasoning.analyze_query_intent(query, today_str)
    intent = analysis.get("intent", "CHAT")
    filters = analysis.get("filters", {}) or {}

    if intent == "QUERY":
        summary = finance_core.calculate_summary(
            db=db, user_id=user_id, filters=filters
        )
        pending = finance_core.get_pending_balance(db=db, user_id=user_id)

        total_amount = summary.get("total", 0.0)
        transaction_count = summary.get("count", 0)
        pending_total = pending.get("total", 0.0)
        pending_count = pending.get("count", 0)
        category = filters.get("category")
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        tx_type = filters.get("type")

        parts = []
        if category:
            parts.append(f"en la categoría {category}")
        if tx_type:
            if tx_type == "EXPENSE":
                parts.append("de tipo gasto")
            elif tx_type == "INCOME":
                parts.append("de tipo ingreso")
            elif tx_type == "DEBT":
                parts.append("de tipo deuda")
        if start_date and end_date:
            if start_date == end_date:
                parts.append(f"el día {start_date}")
            else:
                parts.append(f"entre {start_date} y {end_date}")

        detail = ""
        if parts:
            detail = " " + ", ".join(parts)

        if transaction_count == 0 and pending_count == 0:
            response_text = "Según mis registros, no encontré transacciones que coincidan con tu consulta."
        elif transaction_count == 0 and pending_count > 0:
            response_text = (
                f"No tienes transacciones validadas{detail}, pero tienes "
                f"${pending_total:.2f} en {pending_count} transacciones pendientes de revisión."
            )
        elif transaction_count > 0 and pending_count > 0:
            response_text = (
                f"Tus gastos validados suman ${total_amount:.2f}{detail}, en {transaction_count} transacciones. "
                f"Además, tienes ${pending_total:.2f} en {pending_count} transacciones pendientes de revisión."
            )
        else:
            response_text = (
                f"Tus gastos validados suman ${total_amount:.2f}{detail}, "
                f"en {transaction_count} transacciones."
            )

        return {
            "response": response_text,
            "total_amount": float(total_amount),
            "period": None,
            "category": category,
            "transaction_count": transaction_count,
        }

    query_lower = query.lower()
    detected_period = None
    days_back = 30
    if "hoy" in query_lower:
        detected_period, days_back = "today", 0
    elif "ayer" in query_lower:
        detected_period, days_back = "yesterday", 1
    elif "semana" in query_lower:
        detected_period, days_back = "week", 7

    end_date = datetime.utcnow()
    start_date = (
        end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if days_back == 0
        else end_date - timedelta(days=days_back)
    )

    detected_category = None
    if "comida" in query_lower or "super" in query_lower:
        detected_category = "Alimentación"
    elif "gasolina" in query_lower or "uber" in query_lower:
        detected_category = "Transporte"

    total_amount = finance_core.calculate_user_spending(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=detected_category,
    )

    transactions = finance_core.get_user_transactions(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=detected_category,
    )

    context = {
        "total_amount": total_amount,
        "transaction_count": len(transactions),
        "period": detected_period,
        "category": detected_category,
    }

    response_text = ai_brain_service.answer_query(query, context)

    return {
        "response": response_text,
        "total_amount": total_amount,
        "period": detected_period,
        "category": detected_category,
        "transaction_count": len(transactions),
    }
