/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║  TRIBE API CLIENT v2.0 — World-Class TypeScript SDK            ║
 * ║  Auto-generated from B0 Contract (route_manifest.json)         ║
 * ║  265 live endpoints | 21 domains | Full type safety            ║
 * ║  Features: SSE, AbortController, auto-pagination, rate-limit   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 *
 * @example
 * ```ts
 * import { createTribeClient } from './tribe-api-client'
 *
 * const api = createTribeClient({
 *   baseUrl: 'https://api.tribe.app/api',
 *   getToken: () => localStorage.getItem('accessToken'),
 *   onTokenExpired: async () => {
 *     const rt = localStorage.getItem('refreshToken')
 *     if (!rt) return null
 *     const { data } = await api.auth.refresh({ refreshToken: rt })
 *     localStorage.setItem('accessToken', data.accessToken)
 *     localStorage.setItem('refreshToken', data.refreshToken)
 *     return data.accessToken
 *   },
 * })
 *
 * // Typed, auto-completed
 * const { data } = await api.auth.login({ phone: '1234567890', pin: '1234' })
 * console.log(data.user.displayName)
 *
 * // Auto-paginate all items
 * for await (const item of api.paginate(p => api.feed.public(p))) {
 *   console.log(item.caption)
 * }
 * ```
 */

// ════════════════════════════════════════════════════════════════════
// §1  PRIMITIVE ALIASES
// ════════════════════════════════════════════════════════════════════

/** Opaque media ID — resolve to URL via `api.mediaUrl(id)` */
type MediaId = string
/** ISO 8601 date-time string (e.g. `2026-03-10T12:00:00.000Z`) */
type ISODate = string
/** UUID v4 string */
type UUID = string

// ════════════════════════════════════════════════════════════════════
// §2  CANONICAL SHARED OBJECTS
// ════════════════════════════════════════════════════════════════════

/** Lightweight user identity embedded in content, comments, notifications */
export interface UserSnippet {
  id: UUID
  displayName: string | null
  username: string | null
  /** ⚠️ Raw media ID, NOT a URL. Use `api.mediaUrl(avatar)` to resolve. */
  avatar: MediaId | null
  role: 'USER' | 'MODERATOR' | 'ADMIN' | 'SUPER_ADMIN'
  collegeId: UUID | null
  collegeName: string | null
  houseId: UUID | null
  houseName: string | null
  tribeId: UUID | null
  tribeCode: string | null
}

/** Full user profile returned by /auth/me, /users/:id */
export interface UserProfile extends UserSnippet {
  phone: string
  bio: string | null
  avatarMediaId: MediaId | null
  ageStatus: 'UNKNOWN' | 'ADULT' | 'CHILD'
  ageVerified: boolean
  birthYear: number | null
  collegeVerified: boolean
  tribeName: string | null
  onboardingStep: 'FRESH' | 'PROFILE' | 'AGE' | 'COLLEGE' | 'DONE'
  followersCount: number
  followingCount: number
  postsCount: number
  strikes: number
  isBanned: boolean
  suspendedUntil: ISODate | null
  /** Present only when viewer is authenticated and viewing another user */
  isFollowing?: boolean
  createdAt: ISODate
  updatedAt: ISODate
}

/** Resolved media asset */
export interface MediaObject {
  id: UUID
  /** May be null for DB-stored media; use `api.mediaUrl(id)` as fallback */
  url: string | null
  type: 'IMAGE' | 'VIDEO' | 'AUDIO' | null
  thumbnailUrl: string | null
  width: number | null
  height: number | null
  duration: number | null
  mimeType: string | null
  size: number | null
}

export type ContentVisibility = 'PUBLIC' | 'LIMITED' | 'SHADOW_LIMITED' | 'HELD' | 'HELD_FOR_REVIEW' | 'REMOVED'
export type ContentKind = 'POST' | 'REEL' | 'STORY'

/** Content item (post, reel, or story from content_items collection) */
export interface ContentItem {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  kind: ContentKind
  caption: string
  media?: MediaObject[]
  mediaIds?: string[]
  visibility: ContentVisibility
  distributionStage: number
  likeCount: number
  dislikeCount: number
  commentCount: number
  viewCount: number
  saveCount: number
  collegeId: UUID | null
  houseId: UUID | null
  syntheticDeclaration: boolean
  moderationResult?: Record<string, unknown> | null
  viewerHasLiked?: boolean
  viewerHasDisliked?: boolean
  viewerHasSaved?: boolean
  createdAt: ISODate
  updatedAt: ISODate
}

/** Comment on content or reel */
export interface Comment {
  id: UUID
  contentId: UUID
  authorId: UUID
  author?: UserSnippet
  body: string
  parentId: UUID | null
  likeCount: number
  createdAt: ISODate
}

export type StickerType = 'POLL' | 'QUIZ' | 'SLIDER' | 'QUESTION' | 'MENTION' | 'HASHTAG' | 'LINK' | 'COUNTDOWN' | 'EMOJI'

export interface Sticker {
  id: string
  type: StickerType
  position?: { x: number; y: number }
  data?: Record<string, unknown>
}

/** Story from the dedicated stories collection (24h TTL) */
export interface Story {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  type: 'TEXT' | 'IMAGE' | 'VIDEO'
  text?: string
  mediaId?: MediaId
  caption?: string
  stickers?: Sticker[]
  privacy: 'EVERYONE' | 'CLOSE_FRIENDS' | 'CUSTOM'
  viewCount: number
  reactionCount: number
  replyCount: number
  expiresAt: ISODate
  createdAt: ISODate
}

export type ReelStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'REMOVED'

/** Reel from the dedicated reels collection */
export interface Reel {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  mediaId: MediaId
  caption: string
  audioId?: string
  isRemixOf?: UUID
  tags: string[]
  status: ReelStatus
  likeCount: number
  commentCount: number
  shareCount: number
  viewCount: number
  watchTimeMs: number
  pinned: boolean
  createdAt: ISODate
}

export interface Tribe {
  id: UUID
  name: string
  code: string
  color: string
  mascot: string
  motto: string
  membersCount: number
  totalPoints: number
}

export type ContestStatus = 'DRAFT' | 'PUBLISHED' | 'ENTRIES_OPEN' | 'ENTRIES_CLOSED' | 'JUDGING' | 'RESOLVED' | 'CANCELLED'

export interface TribeContest {
  id: UUID
  title: string
  description: string
  type: string
  status: ContestStatus
  seasonId: UUID
  startsAt: ISODate
  endsAt: ISODate
  entryCount: number
  voteCount: number
  prizes?: Record<string, unknown>
  rules?: Record<string, unknown>
  createdAt: ISODate
}

export type EventStatus = 'DRAFT' | 'PUBLISHED' | 'CANCELLED' | 'ARCHIVED'

export interface Event {
  id: UUID
  organizerId: UUID
  organizer?: UserSnippet
  title: string
  description: string
  eventType: string
  startDate: ISODate
  endDate?: ISODate
  location?: string
  collegeId?: UUID
  maxAttendees?: number
  attendeeCount: number
  status: EventStatus
  rsvpStatus?: string
  createdAt: ISODate
}

export interface BoardNotice {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  title: string
  body: string
  priority: 'NORMAL' | 'IMPORTANT' | 'URGENT'
  collegeId: UUID
  pinned: boolean
  acknowledgmentCount: number
  createdAt: ISODate
}

export interface Resource {
  id: UUID
  uploaderId: UUID
  uploader?: UserSnippet
  kind: 'NOTES' | 'PYQ' | 'LAB_MANUAL' | 'QUESTION_BANK' | 'SYLLABUS' | 'OTHER'
  collegeId: UUID
  title: string
  subject?: string
  branch?: string
  semester?: number
  year?: number
  description?: string
  fileAssetId: MediaId
  voteScore: number
  upvotes: number
  downvotes: number
  downloadCount: number
  viewerVote?: 'UP' | 'DOWN' | null
  status: string
  createdAt: ISODate
}

export interface Notification {
  id: UUID
  type: string
  actorId: UUID
  actor?: UserSnippet
  targetType: string
  targetId: UUID
  message: string
  read: boolean
  createdAt: ISODate
}

export interface Session {
  id: UUID
  ipAddress: string
  deviceInfo: string
  lastAccessedAt: ISODate
  createdAt: ISODate
  isCurrent: boolean
}

export interface College {
  id: UUID
  officialName: string
  shortName?: string
  city?: string
  state?: string
  type?: string
  membersCount: number
}

export interface House {
  id: UUID
  name: string
  slug: string
  color: string
  totalPoints: number
  membersCount: number
  rank?: number
}

// ════════════════════════════════════════════════════════════════════
// §3  PAGINATION & ENVELOPE TYPES
// ════════════════════════════════════════════════════════════════════

/** Cursor-based page (feeds, comments, notifications) */
export interface CursorPage<T> {
  items: T[]
  nextCursor: string | null
  hasMore: boolean
}

/** Offset-based page (followers, members) */
export interface OffsetPage<T> {
  users: T[]
  total: number
  offset: number
  limit: number
}

export interface CursorParams {
  cursor?: string
  limit?: number
  [key: string]: unknown
}

export interface OffsetParams {
  offset?: number
  limit?: number
  [key: string]: unknown
}

/** Standard API data envelope */
export interface Envelope<T> {
  data: T
}

// ════════════════════════════════════════════════════════════════════
// §4  ERROR HANDLING
// ════════════════════════════════════════════════════════════════════

export interface ApiErrorPayload {
  error: string
  code: string
  status?: number
  retryAfterSec?: number
  details?: string
}

export class TribeApiError extends Error {
  readonly code: string
  readonly status: number
  readonly retryAfterSec?: number
  readonly details?: string

  constructor(payload: ApiErrorPayload, status: number) {
    super(payload.error)
    this.name = 'TribeApiError'
    this.code = payload.code
    this.status = status
    this.retryAfterSec = payload.retryAfterSec
    this.details = payload.details
  }

  /** True if this is a rate-limit error (429) */
  get isRateLimited(): boolean { return this.status === 429 }
  /** True if auth token is expired/invalid (401) */
  get isUnauthorized(): boolean { return this.status === 401 }
  /** True if request was forbidden by role guard (403) */
  get isForbidden(): boolean { return this.status === 403 }
}

// ════════════════════════════════════════════════════════════════════
// §5  AUTH TOKEN TYPES
// ════════════════════════════════════════════════════════════════════

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresIn: number
  user: UserProfile
}

// ════════════════════════════════════════════════════════════════════
// §6  HTTP CLIENT CORE
// ════════════════════════════════════════════════════════════════════

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT'

interface RequestConfig {
  method: HttpMethod
  path: string
  body?: Record<string, unknown>
  query?: Record<string, unknown>
  /** Set to false for public endpoints; defaults to true */
  auth?: boolean
  /** Optional AbortSignal for cancellation */
  signal?: AbortSignal
}

export interface TribeClientConfig {
  /** Base URL including /api prefix, e.g. `https://app.tribe.com/api` */
  baseUrl: string
  /** Return current access token or null */
  getToken?: () => string | null
  /** Called on 401 — return new token or null to give up */
  onTokenExpired?: () => Promise<string | null>
  /** Global error hook */
  onError?: (error: TribeApiError) => void
  /** Global request hook (logging, analytics) */
  onRequest?: (method: string, path: string) => void
}

function buildUrl(baseUrl: string, path: string, query?: Record<string, unknown>): string {
  const url = new URL(path, baseUrl)
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    }
  }
  return url.toString()
}

async function request<T>(config: TribeClientConfig, req: RequestConfig): Promise<T> {
  const url = buildUrl(config.baseUrl, req.path, req.query)
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }

  if (req.auth !== false && config.getToken) {
    const token = config.getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  config.onRequest?.(req.method, req.path)

  const fetchOpts: RequestInit = {
    method: req.method,
    headers,
    body: req.body ? JSON.stringify(req.body) : undefined,
    signal: req.signal,
  }

  let res = await fetch(url, fetchOpts)

  // Auto-retry on 401 if token refresh is available
  if (res.status === 401 && config.onTokenExpired) {
    const newToken = await config.onTokenExpired()
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`
      res = await fetch(url, { ...fetchOpts, headers })
    }
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ error: res.statusText, code: 'UNKNOWN' }))
    const apiErr = new TribeApiError(errData, res.status)
    config.onError?.(apiErr)
    throw apiErr
  }

  if (res.status === 204) return {} as T
  return res.json() as Promise<T>
}

// ════════════════════════════════════════════════════════════════════
// §7  SSE (SERVER-SENT EVENTS) SUPPORT
// ════════════════════════════════════════════════════════════════════

export interface SSEConnection {
  /** Close the SSE connection */
  close(): void
}

function connectSSE(
  config: TribeClientConfig,
  path: string,
  onMessage: (event: { type: string; data: unknown }) => void,
  onError?: (err: globalThis.Event) => void,
): SSEConnection {
  const url = buildUrl(config.baseUrl, path)
  const token = config.getToken?.()
  const fullUrl = token ? `${url}${url.includes('?') ? '&' : '?'}token=${encodeURIComponent(token)}` : url
  const es = new EventSource(fullUrl)

  es.onmessage = (evt) => {
    try {
      onMessage({ type: 'message', data: JSON.parse(evt.data) })
    } catch {
      onMessage({ type: 'message', data: evt.data })
    }
  }
  es.onerror = (evt) => onError?.(evt)

  return { close: () => es.close() }
}

// ════════════════════════════════════════════════════════════════════
// §8  CLIENT FACTORY — 265 endpoints across 27 domains
// ════════════════════════════════════════════════════════════════════

export function createTribeClient(config: TribeClientConfig) {
  const r = <T>(req: RequestConfig) => request<T>(config, req)

  return {
    // ──────────────────────────────────────────────────────────────
    // UTILITIES
    // ──────────────────────────────────────────────────────────────

    /** Resolve a media ID to a full URL */
    mediaUrl(id: string): string {
      return `${config.baseUrl}/media/${id}`
    },

    /** Resolve avatar media ID to URL, or null if no avatar */
    avatarUrl(avatar: string | null): string | null {
      return avatar ? `${config.baseUrl}/media/${avatar}` : null
    },

    /**
     * Auto-paginate through all pages of a cursor-based endpoint.
     * Yields items one-by-one across all pages.
     * @example
     * ```ts
     * for await (const post of api.paginate(p => api.feed.public(p))) {
     *   console.log(post.caption)
     * }
     * ```
     */
    async *paginate<T>(
      fetcher: (params: CursorParams) => Promise<{ data: CursorPage<T> }>,
      pageSize = 20,
    ): AsyncGenerator<T> {
      let cursor: string | undefined
      let hasMore = true
      while (hasMore) {
        const { data } = await fetcher({ cursor, limit: pageSize })
        for (const item of data.items) yield item
        hasMore = data.hasMore
        cursor = data.nextCursor ?? undefined
      }
    },

    // ══════════════════════════════════════════════════════════════
    // SYSTEM (10 routes)
    // ══════════════════════════════════════════════════════════════

    system: {
      /** Liveness probe — always returns 200 if server is up */
      healthz() {
        return r<{ status: string }>({ method: 'GET', path: '/healthz', auth: false })
      },
      /** Readiness probe — checks DB connectivity */
      readyz() {
        return r<{ status: string }>({ method: 'GET', path: '/readyz', auth: false })
      },
      /** API root info */
      info() {
        return r<Record<string, unknown>>({ method: 'GET', path: '/', auth: false })
      },
      /** Cache stats (admin only) */
      cacheStats() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/cache/stats' })
      },
      /** Deep health check (admin only) */
      opsHealth() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/ops/health' })
      },
      /** Observability metrics (admin only) */
      opsMetrics() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/ops/metrics' })
      },
      /** SLI data (admin only) */
      opsSlis() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/ops/slis' })
      },
      /** Backup check (admin only) */
      opsBackupCheck() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/ops/backup-check' })
      },
      /** AI moderation config (mod only) */
      moderationConfig() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/moderation/config' })
      },
      /** Manual moderation check (mod only) */
      moderationCheck(body: { text: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/moderation/check', body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // AUTH (9 routes)
    // ══════════════════════════════════════════════════════════════

    auth: {
      /** Register a new account. Returns tokens + user profile. */
      register(body: { phone: string; pin: string; displayName: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/register', body, auth: false })
      },
      /** Login with phone + PIN. Brute-force protected (5 attempts → 15min lockout). */
      login(body: { phone: string; pin: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/login', body, auth: false })
      },
      /** Rotate refresh token. Reuse detection kills all sessions. */
      refresh(body: { refreshToken: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/refresh', body, auth: false })
      },
      /** Logout current session. Always returns 200. */
      logout() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/auth/logout' })
      },
      /** Get current authenticated user's full profile */
      me() {
        return r<{ data: { user: UserProfile } }>({ method: 'GET', path: '/auth/me' })
      },
      /** List all active sessions for current user */
      sessions() {
        return r<{ data: { sessions: Session[] } }>({ method: 'GET', path: '/auth/sessions' })
      },
      /** Revoke all sessions (force re-login everywhere) */
      revokeAllSessions() {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: '/auth/sessions' })
      },
      /** Revoke a single session by ID */
      revokeSession(sessionId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/auth/sessions/${sessionId}` })
      },
      /** Change PIN (requires current PIN) */
      changePin(body: { currentPin: string; newPin: string }) {
        return r<{ data: { message: string } }>({ method: 'PATCH', path: '/auth/pin', body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // ME / PROFILE (4 routes)
    // ══════════════════════════════════════════════════════════════

    me: {
      /** Update profile fields (all optional, only provided fields updated) */
      updateProfile(body: { displayName?: string; username?: string; bio?: string; avatarMediaId?: string }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/profile', body })
      },
      /** Set birth year. Child→Adult upgrade blocked once set. */
      setAge(body: { birthYear: number }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/age', body })
      },
      /** Link/unlink college (null to unlink) */
      setCollege(body: { collegeId: string | null }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/college', body })
      },
      /** Mark onboarding as complete */
      completeOnboarding() {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/onboarding', body: {} })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // CONTENT (3 routes)
    // ══════════════════════════════════════════════════════════════

    content: {
      /** Create a post, reel, or story in content_items. AI-moderated caption. Age gate enforced. */
      create(body: { caption?: string; mediaIds?: string[]; kind?: ContentKind; syntheticDeclaration?: boolean; collegeId?: string; houseId?: string }) {
        return r<{ data: ContentItem }>({ method: 'POST', path: '/content/posts', body })
      },
      /** Get a single content item by ID (with author snippet + viewer state if authed) */
      get(id: string) {
        return r<{ data: ContentItem }>({ method: 'GET', path: `/content/${id}`, auth: false })
      },
      /** Soft-delete a content item (owner or admin) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${id}` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // FEED (6 routes)
    // ══════════════════════════════════════════════════════════════

    feed: {
      /** Public discovery feed (stage-2 only content). Cursor paginated. */
      public(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/public', query: params, auth: false })
      },
      /** Feed from users you follow. Cursor paginated. */
      following(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/following', query: params })
      },
      /** College-scoped feed. Cached. Cursor paginated. */
      college(collegeId: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/feed/college/${collegeId}`, query: params, auth: false })
      },
      /** House-scoped feed. Cached. Cursor paginated. */
      house(houseId: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/feed/house/${houseId}`, query: params, auth: false })
      },
      /** Story rail grouped by user (content_items with kind=STORY) */
      stories() {
        return r<{ data: { storyGroups: Array<{ user: UserSnippet; stories: ContentItem[]; hasUnviewed: boolean }> } }>({ method: 'GET', path: '/feed/stories' })
      },
      /** Reels discovery feed. Cached. Cursor paginated. */
      reels(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/reels', query: params, auth: false })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // SOCIAL (7 routes)
    // ══════════════════════════════════════════════════════════════

    social: {
      /** Follow a user (idempotent) */
      follow(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/follow/${userId}` })
      },
      /** Unfollow a user (idempotent) */
      unfollow(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/follow/${userId}` })
      },
      /** Like content (triggers distribution evaluation) */
      like(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/like` })
      },
      /** Dislike content (internal signal, no UI count) */
      dislike(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/dislike` })
      },
      /** Remove like/dislike reaction */
      removeReaction(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${contentId}/reaction` })
      },
      /** Bookmark content (idempotent) */
      save(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/save` })
      },
      /** Remove bookmark */
      unsave(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${contentId}/save` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // COMMENTS (2 routes)
    // ══════════════════════════════════════════════════════════════

    comments: {
      /**
       * Post a comment on content. AI-moderated.
       * ⚠️ Quirk: both `body` and `text` field names are accepted.
       */
      create(contentId: string, body: { body: string; parentId?: string }) {
        return r<{ data: Comment }>({ method: 'POST', path: `/content/${contentId}/comments`, body })
      },
      /** List comments on content. Cursor paginated. */
      list(contentId: string, params?: CursorParams) {
        return r<{ data: { comments: Comment[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/content/${contentId}/comments`, query: params, auth: false })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // USERS (5 routes)
    // ══════════════════════════════════════════════════════════════

    users: {
      /** Get user profile (includes isFollowing if viewer is authed) */
      get(id: string) {
        return r<{ data: { user: UserProfile } }>({ method: 'GET', path: `/users/${id}`, auth: false })
      },
      /** Get user's posts/reels/stories. Filter with ?kind= */
      posts(id: string, params?: CursorParams & { kind?: ContentKind }) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/users/${id}/posts`, query: params, auth: false })
      },
      /** Get user's followers. Offset paginated. */
      followers(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/users/${id}/followers`, query: params, auth: false })
      },
      /** Get user's following. Offset paginated. */
      following(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/users/${id}/following`, query: params, auth: false })
      },
      /** Get user's saved posts (SELF-ONLY — returns 403 for others) */
      saved(id: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/users/${id}/saved`, query: params })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // DISCOVERY + SEARCH (11 routes)
    // ══════════════════════════════════════════════════════════════

    discovery: {
      /** Search colleges by name/state/type */
      searchColleges(params: { q?: string; state?: string; type?: string } & OffsetParams) {
        return r<{ data: { colleges: College[]; total: number } }>({ method: 'GET', path: '/colleges/search', query: params, auth: false })
      },
      /** List all college states (cached) */
      collegeStates() {
        return r<{ data: { states: string[] } }>({ method: 'GET', path: '/colleges/states', auth: false })
      },
      /** List all college types (cached) */
      collegeTypes() {
        return r<{ data: { types: string[] } }>({ method: 'GET', path: '/colleges/types', auth: false })
      },
      /** Get college detail */
      getCollege(id: string) {
        return r<{ data: College }>({ method: 'GET', path: `/colleges/${id}`, auth: false })
      },
      /** List members of a college. Offset paginated. */
      collegeMembers(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/colleges/${id}/members`, query: params, auth: false })
      },
      /** List all houses (cached) */
      houses() {
        return r<{ data: { houses: House[] } }>({ method: 'GET', path: '/houses', auth: false })
      },
      /** House leaderboard (cached) */
      houseLeaderboard() {
        return r<{ data: { houses: House[] } }>({ method: 'GET', path: '/houses/leaderboard', auth: false })
      },
      /** Get house by ID or slug */
      getHouse(idOrSlug: string) {
        return r<{ data: House }>({ method: 'GET', path: `/houses/${idOrSlug}`, auth: false })
      },
      /** List members of a house. Offset paginated. */
      houseMembers(idOrSlug: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/houses/${idOrSlug}/members`, query: params, auth: false })
      },
      /**
       * Universal search across users, colleges, houses.
       * ⚠️ Quirk: Post search NOT indexed (returns empty for type=posts)
       */
      search(params: { q: string; type?: 'all' | 'users' | 'colleges' | 'houses' } & OffsetParams) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/search', query: params, auth: false })
      },
      /** Follow suggestions based on college/house */
      suggestions() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/suggestions/users' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // MEDIA (2 routes)
    // ══════════════════════════════════════════════════════════════

    media: {
      /**
       * Upload media as base64 JSON. Tries object storage first, falls back to MongoDB.
       * Max image: 5MB, max video: 30MB.
       */
      upload(body: { data: string; mimeType: string; type?: 'IMAGE' | 'VIDEO' | 'AUDIO'; width?: number; height?: number; duration?: number }) {
        return r<{ data: MediaObject }>({ method: 'POST', path: '/media/upload', body })
      },
      /**
       * Get media binary by ID. Returns binary content with Cache-Control: immutable.
       * Typically use `api.mediaUrl(id)` in <img src> instead of calling this.
       */
      get(id: string) {
        return fetch(buildUrl(config.baseUrl, `/media/${id}`))
      },
    },

    // ══════════════════════════════════════════════════════════════
    // STORIES (25 routes + 1 SSE)
    // ══════════════════════════════════════════════════════════════

    stories: {
      /**
       * SSE stream for real-time story events (new stories, reactions, replies).
       * Returns a connection handle with .close() method.
       */
      eventStream(
        onMessage: (event: { type: string; data: unknown }) => void,
        onError?: (err: globalThis.Event) => void,
      ): SSEConnection {
        return connectSSE(config, '/stories/events/stream', onMessage, onError)
      },
      /** Create a new story (24h TTL). Rate limited: 30/hr. AI-moderated. */
      create(body: { type: 'TEXT' | 'IMAGE' | 'VIDEO'; text?: string; mediaId?: string; caption?: string; stickers?: Sticker[]; privacy?: 'EVERYONE' | 'CLOSE_FRIENDS' | 'CUSTOM'; background?: Record<string, unknown>; music?: Record<string, unknown> }) {
        return r<{ data: Story }>({ method: 'POST', path: '/stories', body })
      },
      /** Story feed from stories collection (distinct from feed/stories which uses content_items) */
      feed() {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: '/stories/feed' })
      },
      /** Get a single story by ID */
      get(id: string) {
        return r<{ data: Story }>({ method: 'GET', path: `/stories/${id}`, auth: false })
      },
      /** Delete a story (owner only) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/stories/${id}` })
      },
      /** Get story viewers (OWNER-ONLY) */
      views(id: string) {
        return r<{ data: { views: UserSnippet[] } }>({ method: 'GET', path: `/stories/${id}/views` })
      },
      /** React to a story with an emoji */
      react(id: string, body: { emoji: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/react`, body })
      },
      /** Remove reaction from a story */
      removeReaction(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/stories/${id}/react` })
      },
      /** Reply to a story (max 1000 chars) */
      reply(id: string, body: { text: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/reply`, body })
      },
      /** Get story replies (OWNER-ONLY) */
      replies(id: string) {
        return r<{ data: { replies: Array<{ id: string; text: string; author: UserSnippet; createdAt: ISODate }> } }>({ method: 'GET', path: `/stories/${id}/replies` })
      },
      /** Respond to a sticker (poll vote, quiz answer, slider value, etc.) */
      respondToSticker(storyId: string, stickerId: string, body: { response: string | number }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${storyId}/sticker/${stickerId}/respond`, body })
      },
      /** Get sticker results (aggregated — poll percentages, quiz stats) */
      stickerResults(storyId: string, stickerId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/stories/${storyId}/sticker/${stickerId}/results`, auth: false })
      },
      /** Get raw sticker responses (OWNER-ONLY) */
      stickerResponses(storyId: string, stickerId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/stories/${storyId}/sticker/${stickerId}/responses` })
      },
      /** Get own archived/expired stories */
      archive() {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: '/me/stories/archive' })
      },
      /** Get a specific user's active stories */
      userStories(userId: string) {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: `/users/${userId}/stories`, auth: false })
      },
      /** Report a story */
      report(id: string, body: { reason: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/report`, body })
      },

      // ── Close Friends ──
      /** List close friends */
      closeFriends() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/me/close-friends' })
      },
      /** Add a close friend */
      addCloseFriend(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/me/close-friends/${userId}` })
      },
      /** Remove a close friend */
      removeCloseFriend(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/close-friends/${userId}` })
      },

      // ── Highlights ──
      /** Create a highlight (max 50 per user) */
      createHighlight(body: { name: string; coverStoryId?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/me/highlights', body })
      },
      /** Get a user's highlights */
      userHighlights(userId: string) {
        return r<{ data: { highlights: Array<Record<string, unknown>> } }>({ method: 'GET', path: `/users/${userId}/highlights`, auth: false })
      },
      /** Update a highlight (add/remove stories, rename, change cover) */
      updateHighlight(id: string, body: { name?: string; addStoryIds?: string[]; removeStoryIds?: string[]; coverStoryId?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/me/highlights/${id}`, body })
      },
      /** Delete a highlight */
      deleteHighlight(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/highlights/${id}` })
      },

      // ── Settings ──
      /** Get story privacy/reply settings */
      getSettings() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/story-settings' })
      },
      /** Update story settings */
      updateSettings(body: { defaultPrivacy?: string; replyPrivacy?: string; autoArchive?: boolean; hideStoryFrom?: string[] }) {
        return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: '/me/story-settings', body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // BLOCKS (3 routes)
    // ══════════════════════════════════════════════════════════════

    blocks: {
      /** List blocked users */
      list() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/me/blocks' })
      },
      /** Block a user */
      block(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/me/blocks/${userId}` })
      },
      /** Unblock a user */
      unblock(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/blocks/${userId}` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // REELS (32 routes)
    // ══════════════════════════════════════════════════════════════

    reels: {
      /** Create a reel (draft or published). Requires uploaded video mediaId. */
      create(body: { mediaId: string; caption?: string; audioId?: string; isRemixOf?: string; tags?: string[]; draft?: boolean }) {
        return r<{ data: Reel }>({ method: 'POST', path: '/reels', body })
      },
      /** Reels discovery feed. Cursor paginated. */
      feed(params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: '/reels/feed', query: params, auth: false })
      },
      /** Reels from users you follow. Offset paginated. */
      following(params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: '/reels/following', query: params })
      },
      /** Get a specific user's published reels */
      userReels(userId: string, params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: `/users/${userId}/reels`, query: params, auth: false })
      },
      /** Get a single reel by ID */
      get(id: string) {
        return r<{ data: Reel }>({ method: 'GET', path: `/reels/${id}`, auth: false })
      },
      /** Edit reel caption/tags (owner only) */
      update(id: string, body: { caption?: string; tags?: string[] }) {
        return r<{ data: Reel }>({ method: 'PATCH', path: `/reels/${id}`, body })
      },
      /** Delete a reel (owner only) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}` })
      },
      /** Publish a draft reel */
      publish(id: string) {
        return r<{ data: Reel }>({ method: 'POST', path: `/reels/${id}/publish` })
      },
      /** Archive a published reel */
      archive(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/archive` })
      },
      /** Restore an archived reel */
      restore(id: string) {
        return r<{ data: Reel }>({ method: 'POST', path: `/reels/${id}/restore` })
      },
      /** Pin reel to profile */
      pin(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/pin` })
      },
      /** Unpin reel from profile */
      unpin(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/pin` })
      },
      /** Like a reel */
      like(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/like` })
      },
      /** Unlike a reel */
      unlike(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/like` })
      },
      /** Save/bookmark a reel */
      save(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/save` })
      },
      /** Unsave a reel */
      unsave(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/save` })
      },
      /**
       * Comment on a reel.
       * ⚠️ KNOWN BUG: Currently returns 400 (scheduled fix in Stage B6)
       */
      comment(id: string, body: { text: string; parentId?: string }) {
        return r<{ data: Comment }>({ method: 'POST', path: `/reels/${id}/comment`, body })
      },
      /** List comments on a reel. Cursor paginated. */
      comments(id: string, params?: CursorParams) {
        return r<{ data: { comments: Comment[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/reels/${id}/comments`, query: params, auth: false })
      },
      /**
       * Report a reel.
       * ⚠️ KNOWN BUG: Currently returns 400 (scheduled fix in Stage B6)
       */
      report(id: string, body: { reason: string; details?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/report`, body })
      },
      /** Hide reel from your feed */
      hide(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/hide` })
      },
      /** Mark reel as not interested (affects algorithm) */
      notInterested(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/not-interested` })
      },
      /** Track reel share (for analytics) */
      share(id: string, body?: { platform?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/share`, body })
      },
      /** Record watch time for engagement scoring (public, no auth required) */
      recordWatch(id: string, body: { watchTimeMs: number; completionRate?: number }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/watch`, body, auth: false })
      },
      /** Record a view (public, no auth required) */
      recordView(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/view`, auth: false })
      },
      /** Get all reels using a specific audio track */
      audioReels(audioId: string) {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: `/reels/audio/${audioId}`, auth: false })
      },
      /** Get remixes of a specific reel */
      remixes(id: string) {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: `/reels/${id}/remixes`, auth: false })
      },
      /** Create a reel series */
      createSeries(body: { name: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/me/reels/series', body })
      },
      /** Get a user's reel series */
      userSeries(userId: string) {
        return r<{ data: { series: Array<Record<string, unknown>> } }>({ method: 'GET', path: `/users/${userId}/reels/series`, auth: false })
      },
      /** Get own archived reels */
      myArchive() {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: '/me/reels/archive' })
      },
      /** Get own reel analytics (views, likes, watch time breakdowns) */
      myAnalytics() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/reels/analytics' })
      },
      /** Update processing status (internal, for video pipeline) */
      updateProcessing(id: string, body: Record<string, unknown>) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/reels/${id}/processing`, body })
      },
      /** Get processing status */
      getProcessing(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/reels/${id}/processing` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // TRIBES (9 routes)
    // ══════════════════════════════════════════════════════════════

    tribes: {
      /** List all tribes */
      list() {
        return r<{ data: { tribes: Tribe[] } }>({ method: 'GET', path: '/tribes', auth: false })
      },
      /** Current season standings */
      standings() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribes/standings/current', auth: false })
      },
      /** Get a tribe by ID */
      get(id: string) {
        return r<{ data: Tribe }>({ method: 'GET', path: `/tribes/${id}`, auth: false })
      },
      /** List tribe members. Offset paginated. */
      members(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/tribes/${id}/members`, query: params, auth: false })
      },
      /** Get tribe board members */
      board(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/board`, auth: false })
      },
      /** Get tribe fund details */
      fund(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/fund`, auth: false })
      },
      /** Get tribe salutes */
      salutes(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/salutes`, auth: false })
      },
      /** Get current user's tribe info */
      myTribe() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/tribe' })
      },
      /** Get a user's tribe info */
      userTribe(userId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/users/${userId}/tribe`, auth: false })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // TRIBE CONTESTS (13 routes)
    // ══════════════════════════════════════════════════════════════

    contests: {
      /** List all contests */
      list() {
        return r<{ data: { contests: TribeContest[] } }>({ method: 'GET', path: '/tribe-contests', auth: false })
      },
      /** Live feed of active contests. Cursor paginated. */
      liveFeed(params?: CursorParams) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribe-contests/live-feed', query: params, auth: false })
      },
      /** Get contest detail */
      get(id: string) {
        return r<{ data: { contest: TribeContest } }>({ method: 'GET', path: `/tribe-contests/${id}`, auth: false })
      },
      /** Get live contest data (real-time scores) */
      live(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/live`, auth: false })
      },
      /** List contest entries */
      entries(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/entries`, auth: false })
      },
      /** Get contest leaderboard */
      leaderboard(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/leaderboard`, auth: false })
      },
      /** Get contest results (after resolution) */
      results(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/results`, auth: false })
      },
      /** Enter a contest */
      enter(id: string, body: { entryData: Record<string, unknown> }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/tribe-contests/${id}/enter`, body })
      },
      /** Vote for a contest entry */
      vote(id: string, body: { entryId: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/tribe-contests/${id}/vote`, body })
      },
      /** Withdraw from a contest */
      withdraw(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/tribe-contests/${id}/withdraw` })
      },
      /** List all seasons */
      seasons() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribe-contests/seasons', auth: false })
      },
      /** Get season standings */
      seasonStandings(seasonId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/seasons/${seasonId}/standings`, auth: false })
      },
      /** Get live season standings */
      seasonLiveStandings(seasonId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/seasons/${seasonId}/live-standings`, auth: false })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // EVENTS (18 routes)
    // ══════════════════════════════════════════════════════════════

    events: {
      /** Create an event */
      create(body: { title: string; description?: string; eventType?: string; startDate: string; endDate?: string; location?: string; collegeId?: string; maxAttendees?: number; coverMediaId?: string; tags?: string[] }) {
        return r<{ data: Event }>({ method: 'POST', path: '/events', body })
      },
      /** Event feed. Cursor paginated. */
      feed(params?: CursorParams) {
        return r<{ data: CursorPage<Event> }>({ method: 'GET', path: '/events/feed', query: params, auth: false })
      },
      /** Search events */
      search(params: { q?: string; eventType?: string; collegeId?: string }) {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/events/search', query: params, auth: false })
      },
      /** Get events for a college */
      collegeEvents(collegeId: string) {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: `/events/college/${collegeId}`, auth: false })
      },
      /** Get event detail */
      get(id: string) {
        return r<{ data: Event }>({ method: 'GET', path: `/events/${id}`, auth: false })
      },
      /** Update event (organizer only) */
      update(id: string, body: Partial<{ title: string; description: string; startDate: string; endDate: string; location: string; maxAttendees: number }>) {
        return r<{ data: Event }>({ method: 'PATCH', path: `/events/${id}`, body })
      },
      /** Delete event (organizer only) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/events/${id}` })
      },
      /** Publish a draft event */
      publish(id: string) {
        return r<{ data: Event }>({ method: 'POST', path: `/events/${id}/publish` })
      },
      /** Cancel an event */
      cancel(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/cancel` })
      },
      /** Archive an event */
      archive(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/archive` })
      },
      /** RSVP to an event */
      rsvp(id: string, body: { status: 'GOING' | 'INTERESTED' | 'NOT_GOING' }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/rsvp`, body })
      },
      /** Cancel RSVP */
      cancelRsvp(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/events/${id}/rsvp` })
      },
      /** Get event attendees */
      attendees(id: string) {
        return r<{ data: { attendees: UserSnippet[] } }>({ method: 'GET', path: `/events/${id}/attendees`, auth: false })
      },
      /** Report an event */
      report(id: string, body: { reason: string; details?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/report`, body })
      },
      /** Set reminder for an event */
      remind(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/remind` })
      },
      /** Cancel reminder */
      cancelReminder(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/events/${id}/remind` })
      },
      /** Get own created events */
      myEvents() {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/me/events' })
      },
      /** Get events I've RSVP'd to */
      myRsvps() {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/me/events/rsvps' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // BOARD NOTICES (10 routes)
    // ══════════════════════════════════════════════════════════════

    notices: {
      /** Create a board notice (board member of college only) */
      create(body: { title: string; body: string; priority?: 'NORMAL' | 'IMPORTANT' | 'URGENT'; collegeId: string }) {
        return r<{ data: BoardNotice }>({ method: 'POST', path: '/board/notices', body })
      },
      /** Get a notice by ID */
      get(id: string) {
        return r<{ data: BoardNotice }>({ method: 'GET', path: `/board/notices/${id}`, auth: false })
      },
      /** Update a notice (author only) */
      update(id: string, body: { title?: string; body?: string; priority?: string }) {
        return r<{ data: BoardNotice }>({ method: 'PATCH', path: `/board/notices/${id}`, body })
      },
      /** Delete a notice (author or admin) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/board/notices/${id}` })
      },
      /** Pin a notice */
      pin(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/board/notices/${id}/pin` })
      },
      /** Unpin a notice */
      unpin(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/board/notices/${id}/pin` })
      },
      /** Acknowledge a notice */
      acknowledge(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/board/notices/${id}/acknowledge` })
      },
      /** Get acknowledgments for a notice */
      acknowledgments(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/board/notices/${id}/acknowledgments`, auth: false })
      },
      /** List notices for a college. Cursor paginated. */
      collegeNotices(collegeId: string, params?: CursorParams) {
        return r<{ data: { notices: BoardNotice[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/colleges/${collegeId}/notices`, query: params, auth: false })
      },
      /** Get own created notices */
      myNotices() {
        return r<{ data: { notices: BoardNotice[] } }>({ method: 'GET', path: '/me/board/notices' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // RESOURCES (10 routes)
    // ══════════════════════════════════════════════════════════════

    resources: {
      /** Upload a resource (notes, PYQ, lab manual, etc.). Rate limited: 10/hr. Same-college guard. */
      create(body: { kind: string; collegeId: string; title: string; subject?: string; branch?: string; semester?: number; year?: number; description?: string; fileAssetId: string }) {
        return r<{ data: Resource }>({ method: 'POST', path: '/resources', body })
      },
      /** Search resources with filters. Cursor paginated. */
      search(params: { collegeId?: string; branch?: string; subject?: string; semester?: number; kind?: string; year?: number; q?: string; sort?: 'recent' | 'popular' | 'most_downloaded' } & CursorParams) {
        return r<{ data: { resources: Resource[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: '/resources/search', query: params, auth: false })
      },
      /** Get resource detail */
      get(id: string) {
        return r<{ data: Resource }>({ method: 'GET', path: `/resources/${id}`, auth: false })
      },
      /** Update resource metadata (owner only) */
      update(id: string, body: Partial<{ title: string; subject: string; branch: string; semester: number; year: number; description: string }>) {
        return r<{ data: Resource }>({ method: 'PATCH', path: `/resources/${id}`, body })
      },
      /** Delete a resource (owner only) */
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/resources/${id}` })
      },
      /** Report a resource */
      report(id: string, body: { reason: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/resources/${id}/report`, body })
      },
      /** Vote on a resource (duplicate same-direction returns 409) */
      vote(id: string, body: { vote: 'UP' | 'DOWN' }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/resources/${id}/vote`, body })
      },
      /** Remove vote from a resource */
      removeVote(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/resources/${id}/vote` })
      },
      /** Download a resource (increments download count, returns URL) */
      download(id: string) {
        return r<{ data: { url: string } }>({ method: 'POST', path: `/resources/${id}/download`, auth: false })
      },
      /** Get own uploaded resources */
      myResources() {
        return r<{ data: { resources: Resource[] } }>({ method: 'GET', path: '/me/resources' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // GOVERNANCE (7 routes)
    // ══════════════════════════════════════════════════════════════

    governance: {
      /** Get governance board for a college */
      board(collegeId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/board`, auth: false })
      },
      /** Apply for governance board membership */
      apply(collegeId: string, body?: { statement?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/college/${collegeId}/apply`, body })
      },
      /** List governance applications for a college */
      applications(collegeId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/applications`, auth: false })
      },
      /** Vote on a governance application */
      voteApplication(appId: string, body: { vote: 'APPROVE' | 'REJECT' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/applications/${appId}/vote`, body })
      },
      /** Create a governance proposal */
      createProposal(collegeId: string, body: { title: string; description: string; category?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/college/${collegeId}/proposals`, body })
      },
      /** List proposals for a college */
      proposals(collegeId: string, params?: { status?: 'OPEN' | 'PASSED' | 'REJECTED' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/proposals`, query: params, auth: false })
      },
      /** Vote on a proposal */
      voteProposal(proposalId: string, body: { vote: 'FOR' | 'AGAINST' | 'ABSTAIN' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/proposals/${proposalId}/vote`, body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // AUTHENTICITY (3 routes)
    // ══════════════════════════════════════════════════════════════

    authenticity: {
      /** Tag content as AI-generated/synthetic */
      tag(body: { targetType: string; targetId: string; declaration: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/authenticity/tag', body })
      },
      /** Get authenticity tags for a target */
      getTags(type: string, id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/authenticity/tags/${type}/${id}`, auth: false })
      },
      /** Remove an authenticity tag */
      removeTag(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/authenticity/tags/${id}` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // REPORTS (1 route)
    // ══════════════════════════════════════════════════════════════

    reports: {
      /** Create a report against any target (content, user, comment, story, reel, event) */
      create(body: { targetType: string; targetId: string; reasonCode: string; details?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/reports', body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // APPEALS (2 user routes)
    // ══════════════════════════════════════════════════════════════

    appeals: {
      /** Create an appeal against moderation action */
      create(body: { targetType: string; targetId: string; reason: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/appeals', body })
      },
      /** List own appeals */
      list() {
        return r<{ data: { appeals: Array<Record<string, unknown>> } }>({ method: 'GET', path: '/appeals' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // NOTIFICATIONS (2 routes)
    // ══════════════════════════════════════════════════════════════

    notifications: {
      /** List notifications. Cursor paginated. Includes unread count. */
      list(params?: CursorParams) {
        return r<{ data: { notifications: Notification[]; unreadCount: number; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: '/notifications', query: params })
      },
      /** Mark notifications as read. Empty ids = mark all. */
      markRead(body?: { ids?: string[] }) {
        return r<{ data: { message: string } }>({ method: 'PATCH', path: '/notifications/read', body })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // LEGAL (2 routes)
    // ══════════════════════════════════════════════════════════════

    legal: {
      /** Get current consent document */
      consent() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/legal/consent', auth: false })
      },
      /** Accept terms/consent */
      accept() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/legal/accept', body: {} })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // GRIEVANCES (2 routes)
    // ══════════════════════════════════════════════════════════════

    grievances: {
      /** Submit a grievance ticket */
      create(body: { ticketType: string; subject: string; description: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/grievances', body })
      },
      /** List own grievance tickets */
      list() {
        return r<{ data: { grievances: Array<Record<string, unknown>> } }>({ method: 'GET', path: '/grievances' })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // COLLEGE CLAIMS (3 user routes)
    // ══════════════════════════════════════════════════════════════

    claims: {
      /** Submit a college verification claim */
      submit(collegeId: string, body: { claimType: string; evidence: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/colleges/${collegeId}/claim`, body })
      },
      /** List own claims */
      myClaims() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/college-claims' })
      },
      /** Withdraw a pending claim */
      withdraw(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/college-claims/${id}` })
      },
    },

    // ══════════════════════════════════════════════════════════════
    // ADMIN — All routes behind role guard (admin/mod)
    // ══════════════════════════════════════════════════════════════

    admin: {
      /** Platform-wide stats (admin only) */
      stats() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stats' })
      },
      /** Seed colleges from static data (admin only) */
      seedColleges() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/admin/colleges/seed' })
      },

      // ── Moderation ──
      moderation: {
        /** Get moderation queue (held content, reports, appeals) */
        queue(params?: { bucket?: 'held' | 'reports' | 'appeals' } & OffsetParams) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/moderation/queue', query: params })
        },
        /** Take moderation action on content */
        action(contentId: string, body: { action: 'APPROVE' | 'REMOVE' | 'SHADOW_LIMIT' | 'HOLD' | 'STRIKE'; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/moderation/${contentId}/action`, body })
        },
        /** Decide on an appeal */
        decideAppeal(id: string, body: { action: 'APPROVE' | 'REJECT' | 'REQUEST_MORE_INFO'; reasonCodes?: string[]; notes?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/appeals/${id}/decide`, body })
        },
      },

      // ── Stories Admin ──
      stories: {
        /** List stories for moderation */
        list(params?: { status?: string; authorId?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stories', query: params })
        },
        /** Moderate a story */
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/stories/${id}/moderate`, body })
        },
        /** Story analytics */
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stories/analytics' })
        },
        /** Cleanup expired stories */
        cleanup() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/stories/cleanup' })
        },
        /** Recompute story counters */
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/stories/${id}/recompute-counters` })
        },
      },

      // ── Reels Admin ──
      reels: {
        /** List reels for moderation */
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/reels' })
        },
        /** Moderate a reel */
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/reels/${id}/moderate`, body })
        },
        /** Reel analytics */
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/reels/analytics' })
        },
        /** Recompute reel counters */
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/reels/${id}/recompute-counters` })
        },
      },

      // ── Events Admin ──
      events: {
        /** List events for moderation */
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/events' })
        },
        /** Moderate an event */
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/events/${id}/moderate`, body })
        },
        /** Event analytics */
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/events/analytics' })
        },
        /** Recompute event counters */
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/events/${id}/recompute-counters` })
        },
      },

      // ── Distribution Engine Admin ──
      distribution: {
        /** Evaluate all pending content for distribution */
        evaluate() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/evaluate' })
        },
        /** Evaluate a single content item */
        evaluateOne(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/distribution/evaluate/${contentId}` })
        },
        /** Get distribution engine config */
        config() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/distribution/config' })
        },
        /** Emergency kill switch for distribution */
        killSwitch() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/kill-switch' })
        },
        /** Inspect distribution state for a content item */
        inspect(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/distribution/inspect/${contentId}` })
        },
        /** Override distribution stage for a content item */
        override(body: { contentId: string; stage: number; reason: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/override', body })
        },
        /** Remove a distribution override */
        removeOverride(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'DELETE', path: `/admin/distribution/override/${contentId}` })
        },
      },

      // ── College Claims Admin ──
      collegeClaims: {
        /** List college claims for review */
        list(params?: { status?: string; fraudOnly?: boolean }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/college-claims', query: params })
        },
        /** Get claim detail */
        get(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/college-claims/${id}` })
        },
        /** Flag a claim as potentially fraudulent */
        flagFraud(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/college-claims/${id}/flag-fraud` })
        },
        /** Approve or reject a claim */
        decide(id: string, body: { approve: boolean; reasonCodes?: string[]; notes?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/college-claims/${id}/decide`, body })
        },
      },

      // ── Resources Admin ──
      resources: {
        /** List resources for moderation */
        list(params?: { status?: string; collegeId?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/resources', query: params })
        },
        /** Moderate a resource */
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/resources/${id}/moderate`, body })
        },
        /** Recompute resource counters */
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/resources/${id}/recompute-counters` })
        },
        /** Reconcile resource state with storage */
        reconcile() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/resources/reconcile' })
        },
      },

      // ── Board Notices Admin ──
      boardNotices: {
        /** Get board notice moderation queue */
        modQueue() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/moderation/board-notices' })
        },
        /** Decide on a board notice moderation case */
        decide(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/moderation/board-notices/${id}/decide`, body })
        },
        /** Board notice analytics */
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/board-notices/analytics' })
        },
      },

      // ── Tribes Admin ──
      tribes: {
        /** Get tribe member distribution stats */
        distribution() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribes/distribution' })
        },
        /** Reassign users between tribes */
        reassign(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribes/reassign', body })
        },
        /** Create a new season */
        createSeason(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-seasons', body })
        },
        /** List all seasons */
        seasons() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-seasons' })
        },
        /** Adjust tribe salutes (admin only) */
        adjustSalutes(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-salutes/adjust', body })
        },
        /** Resolve tribe awards (admin only) */
        resolveAwards(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-awards/resolve', body })
        },
        /** Migrate tribe data (admin only) */
        migrate(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribes/migrate', body })
        },
        /** Manage tribe boards (admin only) */
        boards(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribes/boards', body })
        },
      },

      // ── Contests Admin ──
      contests: {
        /** Create a new contest */
        create(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-contests', body })
        },
        /** List all contests (admin view) */
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-contests' })
        },
        /** Get contest detail (admin view) */
        get(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/tribe-contests/${id}` })
        },
        /** Publish a contest */
        publish(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/publish` })
        },
        /** Open entries for a contest */
        openEntries(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/open-entries` })
        },
        /** Close entries for a contest */
        closeEntries(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/close-entries` })
        },
        /** Lock a contest for judging */
        lock(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/lock` })
        },
        /** Resolve a contest (declare winners) */
        resolve(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/resolve` })
        },
        /** Cancel a contest */
        cancel(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/cancel` })
        },
        /** Disqualify a contest entry */
        disqualify(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/disqualify`, body })
        },
        /** Submit a judge score */
        judgeScore(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/judge-score`, body })
        },
        /** Compute scores for a contest */
        computeScores(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/compute-scores` })
        },
        /** Recompute and broadcast contest results */
        recomputeBroadcast(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/recompute-broadcast` })
        },
        /** Set/update contest rules */
        rules(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-contests/rules', body })
        },
        /** Contest dashboard (overview of all contests) */
        dashboard() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-contests/dashboard' })
        },
      },

      // ── Authenticity Admin ──
      authenticity: {
        /** Get authenticity stats platform-wide */
        stats() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/authenticity/stats' })
        },
      },

      // ── Governance Admin ──
      governance: {
        /** Seed governance board for a college (admin only) */
        seedBoard(collegeId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/college/${collegeId}/seed-board` })
        },
      },
    },
  }
}

// ════════════════════════════════════════════════════════════════════
// §9  EXPORTED TYPE ALIASES
// ════════════════════════════════════════════════════════════════════

/** The full client instance type */
export type TribeClient = ReturnType<typeof createTribeClient>
