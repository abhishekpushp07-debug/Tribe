# Frontend Proof Status — Tribe App
## Updated: 2026-03-11

---

## 1. Proof Labels
| Label | Meaning |
|---|---|
| LIVE-PROVEN | Verified with real backend data in app flow |
| FIXTURE-PROVEN | Verified with controlled/mock data, renderer confirmed |
| DEVICE-PROOF PENDING | Correct in web/dev testing, needs real mobile device validation |

---

## 2. Current Status

### Feed Variants
| Variant | Status | Notes |
|---|---|---|
| USER text posts | LIVE-PROVEN | Core path works |
| PAGE text posts | LIVE-PROVEN | Seed data created, verified badge + page author rendering |
| PAGE media posts | LIVE-PROVEN | Seed data created, media + verified badge |
| Media posts (single) | LIVE-PROVEN | Seed data created, 1 image |
| Media posts (carousel) | LIVE-PROVEN | Seed data created, 2 images |
| Repost (of user post) | LIVE-PROVEN | Seed data created, original content embedded |
| Repost (of page post) | LIVE-PROVEN | Seed data created, page-authored original |
| Edited post | LIVE-PROVEN | Seed data created, editedAt timestamp real |

### Modal Flows
| Flow | Status | Notes |
|---|---|---|
| Comment modal | DEVICE-PROOF PENDING | Web automation limited by RN Web events |
| Create modal | DEVICE-PROOF PENDING | Same |
| Edit modal | DEVICE-PROOF PENDING | Same |
| Share modal | DEVICE-PROOF PENDING | Same |

---

## 3. Seed Data Records
| Type | ID | Author | Feed Visible |
|---|---|---|---|
| PAGE_POST | 22944ea1-1323-474f-9fe7-ec6105640cd0 | Tribe Campus Memes (VERIFIED) | ✅ Public + Following |
| PAGE_MEDIA_POST | a40f2925-8a22-4c80-b615-07f2bb92afa5 | Tribe Campus Memes (VERIFIED) | ✅ Public + Following |
| MEDIA_SINGLE | c7449353-e6a1-441d-b0ca-c3e948911893 | Seed Creator Alpha | ✅ Public + Following |
| MEDIA_CAROUSEL | 536e8a9b-91bd-4474-9f5a-ba8518638033 | Seed Creator Alpha | ✅ Public + Following |
| REPOST (text) | 797a8b4e-8dae-4347-afb6-d7823018942a | Seed Creator Beta → Alpha's post | ✅ Public + Following |
| REPOST (page) | e3369335-dc07-4639-b8fd-2f9f06f21754 | Seed Creator Beta → Page post | ✅ Public + Following |
| EDITED_POST | ac230b4e-dca4-4b6b-b9a7-162f1c0ee078 | Seed Creator Alpha | ✅ Public + Following |

### Test Credentials
| User | Phone | Pin |
|---|---|---|
| Seed Creator Alpha | 9999960001 | 1234 |
| Seed Creator Beta | 9999960002 | 1234 |

---

## 4. Contract Field Map (for Frontend)
| Field | Location | Type |
|---|---|---|
| `authorType` | post | `"USER"` or `"PAGE"` |
| `author.name` | PAGE post | string (page name) |
| `author.verificationStatus` | PAGE post | `"VERIFIED"` / `"NONE"` |
| `author.isOfficial` | PAGE post | boolean |
| `author.displayName` | USER post | string (user name) |
| `isRepost` | repost | boolean |
| `originalContent` | repost | full post object (nested) |
| `originalContent.author` | repost | author snippet |
| `editedAt` | edited post | ISO datetime string |
| `media` | media post | array of `{id, type, url, width, height}` |
| `media.length` | carousel detection | >1 = carousel |

---

## 5. Rules for Frontend
1. Do NOT claim modal flows are gold-verified until tested on real mobile devices
2. Keep rendering paths production-ready for all variants
3. Distinguish clearly between LIVE-PROVEN, FIXTURE-PROVEN, and DEVICE-PROOF PENDING
4. Frontend should NOT hardcode around missing live variants
5. As backend data diversity increases, UI should render automatically
