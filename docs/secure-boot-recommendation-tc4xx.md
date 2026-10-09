# Secure Boot Recommendation: CMAC vs Signature on TC4xx

As of 2026-10-09

## 1. Recommendation

**For TC4xx ECUs, use signature verification at boot (ECDSA now, ML-DSA as target) instead of on-device CMAC.**

- One signature over the image is verified at flashing and again at every boot.
- The private key stays in the OEM backend HSM. The ECU holds only the public key anchor.
- Keep the hybrid model (signature at flashing, CMAC at boot) only for ECUs where the measured boot time delta does not fit the startup budget, and for SHE-class ECUs without ECC/SHA acceleration (for example TC3xx).

## 2. Benchmark basis (TC4xx, 2 MB image)

| Mechanism | Time (hash + verify) | Status |
| --- | --- | --- |
| ECDSA | ~5 ms | Measured |
| ML-DSA | ~13 ms | Measured |
| AES-CMAC | Not yet measured | Open |

Interpretation:

- On a 2 MB image the hash pass dominates. A CMAC must also process all 2 MB, so it is expected in the same order as the hash share (estimate: a few ms, to be confirmed).
- Expected gap versus CMAC: roughly 0 to 3 ms for ECDSA, about 10 ms for ML-DSA.
- On TC4xx the boot time argument for CMAC is therefore weak.

## 3. Why signature over CMAC on TC4xx

| Criterion | On-device CMAC (hybrid) | Signature at boot |
| --- | --- | --- |
| What is proven at boot | Image unchanged since MAC was computed | Image released by the OEM key holder |
| Secret stored on ECU | Device-unique MAC key | None (public key only) |
| Recompute gate needed after update | Yes (main residual risk) | No |
| Risk of autonomous MAC learning / bypass via debug or UDS 0x27 | Must be controlled | Not applicable |
| Mechanisms to argue in TARA / R156 | Two (signature + CMAC) | One |
| Boot time on TC4xx | Fastest | +0 to 3 ms (ECDSA), +~10 ms (ML-DSA) |
| PQC at boot | Not needed (AES) | Feasible, ML-DSA measured at 13 ms |

Key point: the CMAC is only as trustworthy as the moment it was computed. Removing the recompute step removes the largest residual risk of the hybrid model.

## 4. Decision rule per ECU class

1. Measure AES-CMAC over 2 MB on the target.
2. Compute `delta = signature time - CMAC time`.
3. Compare delta with the startup budget headroom (CAN wake-up or first-message deadline).
   - Delta fits: **signature at boot**.
   - Delta does not fit: try staged verification first (verify the boot-critical part synchronously, the rest in the background before it executes).
   - Still does not fit: keep the hybrid model for that ECU class only.
4. Algorithm choice:
   - Budget allows ~13 ms: ML-DSA now, or ECDSA + ML-DSA dual signature during transition.
   - Budget is tight: ECDSA now, with a crypto-agile verifier and PQC anchors provisioned from day one.

## 5. Key management

### Where keys live

- **Private key**: OEM backend only, inside an HSM-based signing service. Access control, dual control for production signing, audit logging. Never on the ECU, flash tool or workshop equipment.
- **Public key**: on the ECU in OTP or an HSM-protected key slot. Must be immutable (integrity matters, not secrecy). Write-protect after EOL.

### Same key for flashing and boot

Yes. It is one signature over one image, checked twice:

1. Backend signs a manifest (image hash, version, target ECU ID, signature).
2. Bootloader verifies it at flashing, before erasing or committing.
3. HSM verifies the same signature at every boot.

Keep the flash-time check even though boot verifies again:

- Rejects a bad image before the working image is erased (no bricking, A/B or fallback stays intact).
- Checks what boot does not need: anti-rollback version counter, target ECU ID / variant match, manifest dependencies.

### Key hierarchy

- **Root key**: offline, rarely used, hash anchored in OTP. Signs only intermediate keys.
- **Code-signing keys**: per ECU family or supplier, signed by the root. A compromise affects one family and can be revoked without touching the root.
- **Development vs production keys**: strictly separate. Dev keys revoked or disabled in OTP at EOL.
- **Revocation**: reserve several key slots or a key revocation counter in OTP from day one. Expect at least one rotation in a 15+ year vehicle lifetime, plus the ECDSA to ML-DSA switch.
- **Separate from code signing**: UDS 0x29 diagnostic authentication certificates, SecOC keys, TLS keys. Different purpose, lifecycle and owners.

### PQC readiness

- Provision anchors for both ECDSA and ML-DSA (or a hybrid dual signature) now.
- Moving to ML-DSA later then becomes a policy switch, not an OTP change in the field.

## 6. Checklist before rollout

- [ ] AES-CMAC benchmark on TC4xx (2 MB) completed and delta computed
- [ ] Startup budget headroom confirmed per ECU class
- [ ] Algorithm decided per ECU class (ECDSA, ML-DSA, or dual)
- [ ] Public key anchor location and write protection defined
- [ ] Root and code-signing key hierarchy defined, including per-family scope
- [ ] Revocation mechanism (key slots or counter) defined in OTP layout
- [ ] Dev key disablement at EOL defined
- [ ] Anti-rollback counter checked at flashing
- [ ] Backend signing HSM, access control and audit logging in place
- [ ] TARA updated for the new boot chain

## 7. Open questions

- AES-CMAC throughput on TC4xx for 2 MB?
- Startup time budget per ECU class?
- Does any TC4xx ECU class have images significantly larger than 2 MB?
- Which ECUs remain on TC3xx or SHE-class HSMs and stay on the hybrid model?
