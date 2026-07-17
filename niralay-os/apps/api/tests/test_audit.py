from app.services.audit import AuditService

def test_audit_log_append(db):
    svc = AuditService(db)
    svc.log(
        event="TEST_EVENT",
        outcome="success",
        detail="Testing audit log append"
    )
    
    from app.repositories.session import AuditLogRepository
    repo = AuditLogRepository(db)
    logs = repo.list_recent(limit=1)
    
    assert len(logs) == 1
    assert logs[0].event == "TEST_EVENT"
