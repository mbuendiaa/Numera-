from numera.engines.business_events import DocumentUploaded, EventBus, InvoiceCreated


def test_publish_notifies_typed_subscribers_and_records_history():
    bus = EventBus(history_limit=10)
    received = []
    bus.subscribe(DocumentUploaded, received.append)

    event = DocumentUploaded(
        company_id="company_1",
        document_id="document_1",
        filename="invoice.pdf",
        document_type="invoice",
    )
    bus.publish(event)

    assert received == [event]
    assert bus.recent() == [event]
    assert event.to_dict()["event_type"] == "DocumentUploaded"


def test_subscriptions_are_isolated_by_event_type_and_can_unsubscribe():
    bus = EventBus()
    received = []
    unsubscribe = bus.subscribe(DocumentUploaded, received.append)

    bus.publish(InvoiceCreated(company_id="company_1", invoice_id="invoice_1"))
    unsubscribe()
    bus.publish(DocumentUploaded(company_id="company_1", document_id="document_1"))

    assert received == []


def test_recent_filters_by_company_and_event_type():
    bus = EventBus()
    bus.publish(DocumentUploaded(company_id="company_1", document_id="document_1"))
    bus.publish(DocumentUploaded(company_id="company_2", document_id="document_2"))
    bus.publish(InvoiceCreated(company_id="company_1", invoice_id="invoice_1"))

    company_events = bus.recent(company_id="company_1")
    document_events = bus.recent(event_type="DocumentUploaded")

    assert [event.company_id for event in company_events] == ["company_1", "company_1"]
    assert [event.event_type for event in document_events] == ["DocumentUploaded", "DocumentUploaded"]


def test_history_is_bounded():
    bus = EventBus(history_limit=2)
    for index in range(3):
        bus.publish(DocumentUploaded(company_id="company_1", document_id=f"document_{index}"))

    assert [event.document_id for event in bus.recent()] == ["document_2", "document_1"]
