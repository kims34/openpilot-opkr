from research_v1_m20_original_document_table_contract import scan_original_document_text


def test_empty_markup_stays_closed():
    assert scan_original_document_text('')['real_orders_authorized'] is False
