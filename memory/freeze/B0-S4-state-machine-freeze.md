# B0-S4 — State Machine Freeze

**Status**: FROZEN  
**Freeze Date**: 2026-02-XX  
**Rule**: Every lifecycle has explicit states and allowed transitions. Invalid transitions are impossible. Android knows exactly which CTA to show per state.

---

## 1. Auth / User Account Lifecycle

```
ANONYMOUS ──[register]──> ONBOARDING_INCOMPLETE ──[complete steps]──> ONBOARDING_COMPLETE
                                                                           │
                                                                    [normal usage]
                                                                           │
                                                                      ACTIVE ◄───────────────────┐
                                                                        │                        │
                                                               [failed login x5]          [suspension expires]
                                                                        │                        │
                                                                   LOCKED_OUT ──[cooldown]──> ACTIVE
                                                                        │                        │
                                                               [admin action]             [appeal approved]
                                                                        │                        │
                                                                   SUSPENDED ──[wait/appeal]──> ACTIVE
                                                                        │
                                                               [admin action]
                                                                        │
                                                                     BANNED (terminal)
```

### Auth States
| State | Description | Can Login? | Can Post? |
|-------|------------|------------|-----------|
| ANONYMOUS | Not registered | No | No |
| ONBOARDING_INCOMPLETE | Registered but hasn't completed age/college/consent | Yes | No |
| ACTIVE | Fully onboarded, normal user | Yes | Yes |
| LOCKED_OUT | Too many failed login attempts | No (temp) | N/A |
| SUSPENDED | Admin/moderation suspended | Yes (sees suspension notice) | No |
| BANNED | Permanently banned | No | No |

### Onboarding Sub-States (sequential)
```
AGE ──> COLLEGE ──> CONSENT ──> DONE
```
Each step must be completed in order. `onboardingStep` field tracks current position.

---

## 2. Content Visibility Lifecycle

```
                    ┌──[auto-eval promotes]──> LIMITED (Stage 1, college visible)
                    │                              │
PUBLIC_CREATED ──> PROFILE_ONLY (Stage 0) ────────[auto-eval promotes]──> PUBLIC (Stage 2, public visible)
                    │
                    │──[moderation hold]──> HELD_FOR_REVIEW ──[approve]──> (previous stage)
                    │                           │
                    │                      [reject/remove]
                    │                           │
                    │                      REMOVED (soft delete)
                    │
                    │──[user delete]──> REMOVED
                    │
                    └──[admin shadow]──> SHADOW_LIMITED
```

### Content Visibility Values
| Value | Meaning | Visible In |
|-------|---------|-----------|
| `PUBLIC` | Stage 2 distribution | Public feed, college feed, profile |
| `LIMITED` | Stage 1 distribution | College feed, profile |
| `SHADOW_LIMITED` | Silently limited | Only author's own view |
| `HELD_FOR_REVIEW` | Pending moderation | Only admins |
| `REMOVED` | Soft deleted | Nobody |

### Distribution Stage Values
| Stage | Meaning | Feed Eligibility |
|-------|---------|-----------------|
| 0 | Profile only | User profile only |
| 1 | College | College feed + profile |
| 2 | Public | Public feed + college feed + profile |

### Allowed Transitions
| From | To | Trigger |
|------|----|---------|
| 0 | 1 | Auto-eval or admin override |
| 1 | 2 | Auto-eval or admin override |
| 0 | 2 | Admin override (skip stage 1) |
| any | 0 | Admin demotion |
| any | HELD_FOR_REVIEW | Moderation flag |
| any | REMOVED | User delete or admin remove |

---

## 3. Story Lifecycle

```
ACTIVE ──[24h expires]──> EXPIRED ──[30 days TTL]──> DELETED (from DB)
  │
  ├──[user delete]──> DELETED
  │
  └──[moderation]──> MODERATED
```

### Story States
| State | Description | Visible? | Interactions Allowed? |
|-------|------------|---------|----------------------|
| `ACTIVE` | Live, within 24h window | Yes (per privacy) | Yes |
| `EXPIRED` | Past 24h, archived | No (410 on view) | No |
| `DELETED` | User-deleted | No | No |
| `MODERATED` | Admin-hidden | No | No |

### Key Rules
- Stories auto-expire exactly 24 hours after `createdAt`
- Expired stories return HTTP **410 Gone**
- All interactions (view, react, reply, sticker respond) blocked on non-ACTIVE stories
- Expired stories remain in DB for 30 days (TTL cleanup), visible in archive

---

## 4. Reel Lifecycle

```
DRAFT ──[publish]──> PROCESSING ──[media ready]──> PUBLISHED
  │                      │                            │
  │                 [media fails]                [user archive]
  │                      │                            │
  │                   FAILED                     ARCHIVED ──[restore]──> PUBLISHED
  │                                                   │
  │                                              [user delete]
  │                                                   │
  └──[user delete]────────────────────────────── REMOVED
                                                      │
                                                [moderation]
                                                      │
                                             PUBLISHED ──[moderate]──> REMOVED
```

### Reel States
| State | Description | Visible In Feed? |
|-------|------------|-----------------|
| `DRAFT` | Unpublished draft | No |
| `PROCESSING` | Media being processed | No (show processing UI) |
| `PUBLISHED` | Live, visible | Yes |
| `ARCHIVED` | User archived | No (visible in archive) |
| `REMOVED` | Deleted or moderated | No |
| `FAILED` | Processing failed | No (show retry option) |

### Reel Media Status Sub-Machine
| State | Meaning |
|-------|---------|
| `PENDING` | Upload received, not processed |
| `PROCESSING` | Transcoding/thumbnailing |
| `READY` | Media ready for playback |
| `FAILED` | Processing failed |

### Reel Moderation Status Sub-Machine
| State | Meaning |
|-------|---------|
| `PENDING` | Not yet moderated |
| `CLEAN` | Passed moderation |
| `FLAGGED` | Needs review |
| `REMOVED` | Moderation removed |

---

## 5. Event Lifecycle

```
DRAFT ──[publish]──> PUBLIC ──[cancel]──> CANCELLED
                       │
                  [archive after end]
                       │
                   ARCHIVED
                       │
                  [moderation hold]
                       │
                     HELD
```

### Event States
| State | Description | RSVP Allowed? |
|-------|------------|--------------|
| `DRAFT` | Unpublished | No |
| `PUBLIC` | Live, visible | Yes |
| `CANCELLED` | Cancelled by organizer | No |
| `ARCHIVED` | Past event, archived | No |
| `HELD` | Moderation hold | No |

### Allowed Transitions
| From | To | Trigger |
|------|----|---------|
| DRAFT | PUBLIC | Owner publish |
| PUBLIC | CANCELLED | Owner cancel |
| PUBLIC | ARCHIVED | Owner archive (after end date) |
| PUBLIC | HELD | Moderation (3+ reports) |
| HELD | PUBLIC | Admin approve |

---

## 6. College Claim Lifecycle

```
PENDING ──[approve]──> APPROVED
    │
    ├──[reject]──> REJECTED ──[7-day cooldown]──> (can re-submit)
    │
    ├──[user withdraw]──> WITHDRAWN
    │
    └──[flag fraud]──> FRAUD_REVIEW ──[approve]──> APPROVED
                                      │
                                 [reject]──> REJECTED
```

### Claim States
| State | Description | User Can Re-submit? |
|-------|------------|-------------------|
| `PENDING` | Awaiting review | No (one active at a time) |
| `APPROVED` | College linked to user | N/A |
| `REJECTED` | Denied by reviewer | Yes (after 7-day cooldown) |
| `WITHDRAWN` | User cancelled | Yes |
| `FRAUD_REVIEW` | Escalated for fraud investigation | No |

### Key Rules
- Only ONE active claim (PENDING or FRAUD_REVIEW) at a time
- 7-day cooldown after REJECTED before re-submitting
- 3+ lifetime rejections → auto-fraud flag on next PENDING claim
- APPROVED → sets `user.collegeVerified = true` and links `user.collegeId`

---

## 7. Board Notice Lifecycle

```
PENDING_REVIEW ──[moderator approve]──> PUBLISHED
       │
  [moderator reject]
       │
   REJECTED
```

### Notice States
| State | Description | Visible to Students? |
|-------|------------|---------------------|
| `PENDING_REVIEW` | Submitted, awaiting moderation | No |
| `PUBLISHED` | Approved and visible | Yes |
| `REJECTED` | Denied by moderator | No |

### Key Rule
- Admin-created notices bypass PENDING_REVIEW and go straight to PUBLISHED
- Board member notices always start at PENDING_REVIEW

---

## 8. Moderation / Report Lifecycle

```
OPEN ──[reviewer picks up]──> REVIEWING ──[action taken]──> RESOLVED
                                              │
                                        [no action needed]
                                              │
                                          DISMISSED
```

### Report States
| State | Description |
|-------|------------|
| `OPEN` | New report, unreviewed |
| `REVIEWING` | Moderator investigating |
| `RESOLVED` | Action taken (strike, remove, etc.) |
| `DISMISSED` | Report rejected as invalid |

### Moderation Actions (on content)
| Action | Effect |
|--------|--------|
| `APPROVE` | Restore/keep visible |
| `HOLD` | Set to HELD_FOR_REVIEW |
| `REMOVE` | Set to REMOVED |
| `SHADOW_LIMIT` | Set to SHADOW_LIMITED |
| `STRIKE` | Issue strike to author |
| `SUSPEND` | Suspend author account |
| `BAN` | Permanently ban author |

---

## 9. Appeal Lifecycle

```
PENDING ──[reviewer picks up]──> REVIEWING ──[approve]──> APPROVED (content restored, strike reversed)
                                      │
                                 [request more info]──> MORE_INFO_REQUESTED ──[user responds]──> REVIEWING
                                      │
                                   [deny]──> DENIED
```

### Appeal States
| State | Description |
|-------|------------|
| `PENDING` | Submitted, awaiting review |
| `REVIEWING` | Moderator investigating |
| `APPROVED` | Appeal granted, action reversed |
| `DENIED` | Appeal rejected |
| `MORE_INFO_REQUESTED` | Moderator needs more info from user |

### Side Effects of APPROVED
- Content visibility restored to previous state
- Linked strike reversed (if any)
- If strike count drops, suspension may be lifted

---

## 10. Contest Lifecycle (Stage 12X)

```
DRAFT ──[publish]──> PUBLISHED ──[open entries]──> ENTRY_OPEN ──[close entries]──> ENTRY_CLOSED
                                                                                       │
                                                                              [start evaluation]
                                                                                       │
                                                                                  EVALUATING ──[lock]──> LOCKED ──[resolve]──> RESOLVED
                                                                                                                      │
                                                                                                              (TERMINAL: salutes distributed)
                                                                                                              (idempotent: re-resolve returns same result)

ANY STATE ──[cancel]──> CANCELLED
```

### Contest States
| State | Description | Entries? | Voting? | Scoring? |
|-------|------------|---------|---------|----------|
| `DRAFT` | Created, not visible | No | No | No |
| `PUBLISHED` | Visible, entries not open | No | No | No |
| `ENTRY_OPEN` | Accepting submissions | Yes | Yes (if enabled) | No |
| `ENTRY_CLOSED` | Submissions closed, entries validated | No | No (voting may still count) | No |
| `EVALUATING` | Scores being computed | No | No | Yes |
| `LOCKED` | Scores finalized, ready for resolution | No | No | Frozen |
| `RESOLVED` | Winner declared, salutes distributed | No | No | Frozen |
| `CANCELLED` | Contest cancelled at any stage | No | No | No |

### Allowed Transitions (strict)
| From | To | Trigger |
|------|----|---------|
| DRAFT | PUBLISHED | Admin publish |
| PUBLISHED | ENTRY_OPEN | Admin open entries |
| ENTRY_OPEN | ENTRY_CLOSED | Admin close entries |
| ENTRY_CLOSED | EVALUATING | Auto (via lock shortcut) |
| EVALUATING | LOCKED | Admin lock |
| LOCKED | RESOLVED | Admin resolve (IDEMPOTENT) |
| ANY | CANCELLED | Admin cancel |

### Entry Sub-States
| State | Meaning |
|-------|---------|
| `submitted` | User submitted, pending validation |
| `validated` | Entries validated after close |
| `locked` | Entry locked for scoring |
| `withdrawn` | User withdrew entry |
| `disqualified` | Admin disqualified |

### CRITICAL IDEMPOTENCY RULE
If contest is already RESOLVED, calling `/resolve` again returns the existing result with `idempotent: true`. No duplicate salutes are ever distributed.

---

## 11. Resource Status Lifecycle

```
PUBLIC ──[3+ reports]──> HELD ──[admin approve]──> PUBLIC
                              │
                         [admin remove]──> REMOVED
```

### Resource States
| State | Description | Searchable? |
|-------|------------|------------|
| `PUBLIC` | Normal, visible | Yes |
| `HELD` | Auto-held due to reports | No |
| `UNDER_REVIEW` | Manual review | No |
| `REMOVED` | Deleted/moderated | No |

---

## 12. Grievance Lifecycle

```
OPEN ──[staff picks up]──> IN_PROGRESS ──[resolved]──> RESOLVED
                                              │
                                         [closed without fix]──> CLOSED
```

---

## 13. RSVP Status Machine

```
(no RSVP) ──[rsvp GOING]──> GOING ──[change to INTERESTED]──> INTERESTED
                              │                                    │
                         [cancel RSVP]                       [cancel RSVP]
                              │                                    │
                          (no RSVP) ◄──────────────────────── (no RSVP)
```

### RSVP Waitlist
If event capacity is full and user RSVPs GOING:
```
GOING → WAITLISTED (automatically)
```
If a GOING user cancels and capacity opens:
```
WAITLISTED (earliest) → GOING (auto-promoted)
```

---

## PASS Gate Verification

- [x] Every entity has explicit state machine documented
- [x] Allowed transitions are strict — no undefined state jumps
- [x] Contest lifecycle is 100% clear with idempotency guarantee
- [x] Story 24h expiry → 410 behavior documented
- [x] Moderation cascade effects documented (appeal → strike reversal → suspension lift)
- [x] College claim cooldown and fraud escalation documented
- [x] Entry sub-states within contest lifecycle documented
- [x] Android can build state-aware UI with correct CTA per state
- [x] No state confusion between similar-looking states across entities

**B0-S4 STATUS: FROZEN**
