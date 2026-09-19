import React, { useState } from 'react';

const ALGORITHM_SPECS = {
  'ML-DSA-44': {
    name: 'ML-DSA-44 (Dilithium-2)',
    category: 'Lattice-Based (NIST FIPS 204)',
    pkSize: 1312,
    sigSize: 2420,
    verifyTimeMs: 0.45,
    verifyCycles: '1,350,000',
    ramPeakKb: 8.2,
    securityLevel: 'Category 2 (128-bit quantum)',
    description: 'NIST FIPS 204 Module-Lattice digital signature standard optimized for balanced performance and signature size.',
  },
  'ML-DSA-87': {
    name: 'ML-DSA-87 (Dilithium-5)',
    category: 'Lattice-Based (NIST FIPS 204)',
    pkSize: 2592,
    sigSize: 4627,
    verifyTimeMs: 0.92,
    verifyCycles: '2,760,000',
    ramPeakKb: 14.8,
    securityLevel: 'Category 5 (256-bit quantum)',
    description: 'High-security NIST FIPS 204 parameter set providing maximum quantum resistance for critical national security infrastructure.',
  },
  'SLH-DSA': {
    name: 'SLH-DSA-SHA2-128f',
    category: 'Stateless Hash-Based (NIST FIPS 205)',
    pkSize: 32,
    sigSize: 17088,
    verifyTimeMs: 12.40,
    verifyCycles: '37,200,000',
    ramPeakKb: 4.1,
    securityLevel: 'Category 1 (128-bit quantum)',
    description: 'Stateless hash-based signature (SPHINCS+) offering minimal public key footprint with conservative security assumptions.',
  },
  'LMS': {
    name: 'LMS_SHA256_M32_H10',
    category: 'Stateful Hash-Based (NIST SP 800-208 / RFC 8554)',
    pkSize: 60,
    sigSize: 1180,
    verifyTimeMs: 0.18,
    verifyCycles: '540,000',
    ramPeakKb: 2.4,
    securityLevel: '128-bit quantum',
    description: 'Leighton-Micali Signature scheme providing ultra-fast verification and lightweight memory requirements ideal for Stage-0 Boot ROM.',
  },
};

export default function PqcBootPlayground() {
  const [selectedAlgo, setSelectedAlgo] = useState('ML-DSA-44');
  const [keyStatus, setKeyStatus] = useState('valid'); // 'valid' | 'corrupted'
  const [firmwareStatus, setFirmwareStatus] = useState('untampered'); // 'untampered' | 'tampered'
  const [isSimulating, setIsSimulating] = useState(false);
  
  const [pipelineState, setPipelineState] = useState([
    { id: 1, name: '1. Root of Trust Key Hash Check', status: 'idle', details: 'Matches public key SHA-256 against OTP eFuse hash' },
    { id: 2, name: '2. Firmware Manifest Header Parsing', status: 'idle', details: 'Validates magic 0x50514342, entry point 0x20000000, version counter' },
    { id: 3, name: '3. PQC Signature Validation', status: 'idle', details: 'Verifies post-quantum signature over image header and digest' },
    { id: 4, name: '4. Payload SHA-256 Hash Verification', status: 'idle', details: 'Computes flash payload digest and matches manifest payload hash' },
  ]);
  
  const [bootResult, setBootResult] = useState(null);

  const spec = ALGORITHM_SPECS[selectedAlgo];

  const handleSimulate = () => {
    setIsSimulating(true);
    setBootResult(null);

    // Reset pipeline steps
    const initialSteps = pipelineState.map((step) => ({ ...step, status: 'idle' }));
    setPipelineState(initialSteps);

    // Step 1: RoT Key Hash Check
    setTimeout(() => {
      if (keyStatus === 'corrupted') {
        setPipelineState((prev) =>
          prev.map((s) => (s.id === 1 ? { ...s, status: 'failed', failureReason: 'Public Key Hash mismatch with OTP eFuse!' } : s))
        );
        setBootResult({ success: false, step: 'RoT Key Hash', message: 'BOOT HALTED: Hardware Root of Trust Key verification failed (OTP digest mismatch).' });
        setIsSimulating(false);
        return;
      }

      setPipelineState((prev) =>
        prev.map((s) => (s.id === 1 ? { ...s, status: 'passed' } : s))
      );

      // Step 2: Header Parsing
      setTimeout(() => {
        setPipelineState((prev) =>
          prev.map((s) => (s.id === 2 ? { ...s, status: 'passed' } : s))
        );

        // Step 3: Signature Validation
        setTimeout(() => {
          if (firmwareStatus === 'tampered') {
            setPipelineState((prev) =>
              prev.map((s) => (s.id === 3 ? { ...s, status: 'failed', failureReason: 'PQC Signature verification error: invalid algebraic relation / state match' } : s))
            );
            setBootResult({ success: false, step: 'Signature Validation', message: `BOOT HALTED: PQC Signature validation failed for ${selectedAlgo} due to header/payload modification.` });
            setIsSimulating(false);
            return;
          }

          setPipelineState((prev) =>
            prev.map((s) => (s.id === 3 ? { ...s, status: 'passed' } : s))
          );

          // Step 4: Payload Hash Match
          setTimeout(() => {
            setPipelineState((prev) =>
              prev.map((s) => (s.id === 4 ? { ...s, status: 'passed' } : s))
            );

            setBootResult({
              success: true,
              message: `BOOT SUCCESS: ${selectedAlgo} signature verified in ${spec.verifyTimeMs} ms (${spec.verifyCycles} cycles). Handing over control to Kernel at 0x20000000.`,
            });
            setIsSimulating(false);
          }, 350);
        }, 400);
      }, 300);
    }, 300);
  };

  return (
    <div className="pqc-playground-container">
      <div className="pqc-playground-header">
        <h2 style={{ margin: 0 }}>Interactive PQC Secure Bootloader Simulator</h2>
        <p style={{ margin: '6px 0 0 0', opacity: 0.85 }}>
          Simulate the multi-stage post-quantum cryptographic verification pipeline for embedded hardware bootloaders.
        </p>
      </div>

      {/* Control Panel */}
      <div className="pqc-control-panel">
        <div className="pqc-control-group">
          <label htmlFor="algo-select">PQC Signature Algorithm:</label>
          <select
            id="algo-select"
            className="pqc-select"
            value={selectedAlgo}
            onChange={(e) => setSelectedAlgo(e.target.value)}
            disabled={isSimulating}
          >
            <option value="ML-DSA-44">ML-DSA-44 (Lattice-Based, FIPS 204)</option>
            <option value="ML-DSA-87">ML-DSA-87 (High Security Lattice, FIPS 204)</option>
            <option value="SLH-DSA">SLH-DSA-SHA2-128f (Stateless Hash, FIPS 205)</option>
            <option value="LMS">LMS_SHA256_M32_H10 (Stateful Hash, RFC 8554)</option>
          </select>
        </div>

        <div className="pqc-control-group">
          <label htmlFor="key-select">Root of Trust Key State:</label>
          <select
            id="key-select"
            className="pqc-select"
            value={keyStatus}
            onChange={(e) => setKeyStatus(e.target.value)}
            disabled={isSimulating}
          >
            <option value="valid">Authentic Key (OTP eFuse Match)</option>
            <option value="corrupted">Corrupted Key (eFuse Mismatch)</option>
          </select>
        </div>

        <div className="pqc-control-group">
          <label htmlFor="fw-select">Firmware Payload Integrity:</label>
          <select
            id="fw-select"
            className="pqc-select"
            value={firmwareStatus}
            onChange={(e) => setFirmwareStatus(e.target.value)}
            disabled={isSimulating}
          >
            <option value="untampered">Authentic Firmware (Signed & Untampered)</option>
            <option value="tampered">Tampered Firmware (Modified Payload / Header)</option>
          </select>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <button
          className="pqc-btn-simulate"
          onClick={handleSimulate}
          disabled={isSimulating}
        >
          {isSimulating ? 'Executing Boot Pipeline...' : '⚡ Simulate Secure Boot'}
        </button>
      </div>

      {/* Verification Pipeline Steps */}
      <h3 style={{ marginBottom: '12px' }}>Verification Pipeline Status</h3>
      <div className="pqc-pipeline">
        {pipelineState.map((step) => {
          let statusBadgeClass = 'pending';
          let statusLabel = 'PENDING';
          if (step.status === 'passed') {
            statusBadgeClass = 'passed';
            statusLabel = 'PASSED';
          } else if (step.status === 'failed') {
            statusBadgeClass = 'failed';
            statusLabel = 'FAILED';
          }

          return (
            <div key={step.id} className={`pqc-step ${statusBadgeClass}`}>
              <div>
                <strong>{step.name}</strong>
                <div style={{ fontSize: '0.85rem', marginTop: '2px', opacity: 0.8 }}>
                  {step.details}
                </div>
                {step.failureReason && (
                  <div style={{ color: '#ef4444', fontSize: '0.85rem', marginTop: '4px', fontWeight: 600 }}>
                    ❌ {step.failureReason}
                  </div>
                )}
              </div>
              <span
                style={{
                  fontWeight: 700,
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '0.8rem',
                  backgroundColor:
                    step.status === 'passed'
                      ? '#10b98122'
                      : step.status === 'failed'
                      ? '#ef444422'
                      : 'var(--ifm-color-emphasis-200)',
                  color:
                    step.status === 'passed'
                      ? '#10b981'
                      : step.status === 'failed'
                      ? '#ef4444'
                      : 'var(--ifm-color-emphasis-700)',
                }}
              >
                {statusLabel}
              </span>
            </div>
          );
        })}
      </div>

      {/* Boot Outcome Banner */}
      {bootResult && (
        <div
          style={{
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '24px',
            backgroundColor: bootResult.success ? '#10b98115' : '#ef444415',
            border: `2px solid ${bootResult.success ? '#10b981' : '#ef4444'}`,
            color: bootResult.success ? '#065f46' : '#991b1b',
            fontWeight: 600,
          }}
        >
          {bootResult.success ? '✅ ' : '🛑 '}
          {bootResult.message}
        </div>
      )}

      {/* Real-time Metrics Dashboard */}
      <h3 style={{ marginBottom: '12px' }}>Selected Algorithm Metrics ({spec.name})</h3>
      <p style={{ fontSize: '0.9rem', opacity: 0.85 }}>{spec.description}</p>
      
      <div className="pqc-metrics-grid">
        <div className="pqc-metric-card">
          <div className="pqc-metric-label">Public Key Size</div>
          <div className="pqc-metric-value">{spec.pkSize} B</div>
        </div>

        <div className="pqc-metric-card">
          <div className="pqc-metric-label">Signature Size</div>
          <div className="pqc-metric-value">{spec.sigSize} B</div>
        </div>

        <div className="pqc-metric-card">
          <div className="pqc-metric-label">Verify Latency</div>
          <div className="pqc-metric-value">{spec.verifyTimeMs} ms</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>~{spec.verifyCycles} cycles</div>
        </div>

        <div className="pqc-metric-card">
          <div className="pqc-metric-label">Peak Stack RAM</div>
          <div className="pqc-metric-value">{spec.ramPeakKb} KB</div>
        </div>

        <div className="pqc-metric-card">
          <div className="pqc-metric-label">Security Level</div>
          <div className="pqc-metric-value" style={{ fontSize: '1rem' }}>{spec.securityLevel}</div>
        </div>
      </div>
    </div>
  );
}
