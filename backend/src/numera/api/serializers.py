from numera.domain.schemas import JournalEntryRead, JournalLineRead


def enum_value(value):
    return value.value if hasattr(value, "value") else value


def journal_entry_to_read(entry):
    if entry is None:
        return None

    return JournalEntryRead(
        id=getattr(entry, "id", None),
        company_id=entry.company_id,
        event_type=enum_value(entry.event_type),
        source_event_id=entry.source_event_id,
        source_document_id=entry.source_document_id,
        entry_date=entry.entry_date,
        description=entry.description,
        status=enum_value(entry.status),
        lines=[
            JournalLineRead(
                id=getattr(line, "id", None),
                position=getattr(line, "position", None),
                account_code=line.account_code,
                account_name=line.account_name,
                description=line.description,
                debit=line.debit,
                credit=line.credit,
            )
            for line in entry.lines
        ],
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        is_balanced=entry.is_balanced,
    )
