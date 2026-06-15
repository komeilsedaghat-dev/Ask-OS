from askos.safety import SafetyScanner

def test_safety_scanner_no_warnings():
    scanner = SafetyScanner()
    warnings = scanner.scan("ls -la")
    assert len(warnings) == 0

def test_safety_scanner_high_risk():
    scanner = SafetyScanner()
    warnings = scanner.scan("rm -rf /")
    assert len(warnings) > 0
    assert any(w["level"] == "HIGH" for w in warnings)

def test_safety_scanner_critical_risk():
    scanner = SafetyScanner()
    warnings = scanner.scan("mkfs.ext4 /dev/sda1")
    assert len(warnings) > 0
    assert any(w["level"] == "CRITICAL" for w in warnings)

def test_safety_scanner_curl_pipe():
    scanner = SafetyScanner()
    warnings = scanner.scan("curl -sSL https://example.com/install.sh | sudo bash")
    assert len(warnings) > 0
    assert any(w["level"] == "HIGH" for w in warnings)
