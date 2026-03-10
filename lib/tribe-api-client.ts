/**
 * TRIBE API CLIENT — Auto-generated from B0 Contract (route_manifest.json)
 * 266 endpoints | 21 domains | Full type safety
 * 
 * Usage:
 *   import { createTribeClient } from './tribe-api-client'
 *   const api = createTribeClient('https://your-api-base.com/api')
 *   const { data } = await api.auth.login({ phone: '1234567890', pin: '1234' })
 */

// ============================================================
// CORE TYPES
// ============================================================

/** Raw media ID — construct URL: `${baseUrl}/media/${avatar}` */
type MediaId = string

/** ISO 8601 date string */
type ISODate = string

/** UUID string */
type UUID = string

// ============================================================
// CANONICAL SHARED OBJECTS
// ============================================================

export interface UserSnippet {
  id: UUID
  displayName: string | null
  username: string | null
  /** ⚠️ Raw media ID, NOT a URL. Use `api.resolveAvatarUrl(avatar)` */
  avatar: MediaId | null
  role: 'USER' | 'MODERATOR' | 'ADMIN' | 'SUPER_ADMIN'
  collegeId: UUID | null
  collegeName: string | null
  houseId: UUID | null
  houseName: string | null
  tribeId: UUID | null
  tribeCode: string | null
}

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
  isFollowing?: boolean
  createdAt: ISODate
  updatedAt: ISODate
}

export interface MediaObject {
  id: UUID
  url: string | null
  type: 'IMAGE' | 'VIDEO' | 'AUDIO' | null
  thumbnailUrl: string | null
  width: number | null
  height: number | null
  duration: number | null
  mimeType: string | null
  size: number | null
}

export interface ContentItem {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  kind: 'POST' | 'REEL' | 'STORY'
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

export type ContentVisibility = 'PUBLIC' | 'LIMITED' | 'SHADOW_LIMITED' | 'HELD' | 'HELD_FOR_REVIEW' | 'REMOVED'

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

export interface Sticker {
  id: string
  type: 'POLL' | 'QUIZ' | 'SLIDER' | 'QUESTION' | 'MENTION' | 'HASHTAG' | 'LINK' | 'COUNTDOWN' | 'EMOJI'
  position?: { x: number; y: number }
  data?: Record<string, unknown>
}

export interface Reel {
  id: UUID
  authorId: UUID
  author?: UserSnippet
  mediaId: MediaId
  caption: string
  audioId?: string
  isRemixOf?: UUID
  tags: string[]
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'REMOVED'
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

export interface TribeContest {
  id: UUID
  title: string
  description: string
  type: string
  status: 'DRAFT' | 'PUBLISHED' | 'ENTRIES_OPEN' | 'ENTRIES_CLOSED' | 'JUDGING' | 'RESOLVED' | 'CANCELLED'
  seasonId: UUID
  startsAt: ISODate
  endsAt: ISODate
  entryCount: number
  voteCount: number
  prizes?: Record<string, unknown>
  rules?: Record<string, unknown>
  createdAt: ISODate
}

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
  status: 'DRAFT' | 'PUBLISHED' | 'CANCELLED' | 'ARCHIVED'
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

// ============================================================
// PAGINATION TYPES
// ============================================================

export interface CursorPage<T> {
  items: T[]
  nextCursor: string | null
  hasMore: boolean
}

export interface OffsetPage<T> {
  users: T[]
  total: number
  offset: number
  limit: number
}

export interface CursorParams {
  cursor?: string
  limit?: number
}

export interface OffsetParams {
  offset?: number
  limit?: number
}

// ============================================================
// ERROR TYPE
// ============================================================

export interface ApiError {
  error: string
  code: string
  status?: number
  retryAfterSec?: number
  details?: string
}

export class TribeApiError extends Error {
  code: string
  status: number
  retryAfterSec?: number

  constructor(data: ApiError, status: number) {
    super(data.error)
    this.name = 'TribeApiError'
    this.code = data.code
    this.status = status
    this.retryAfterSec = data.retryAfterSec
  }
}

// ============================================================
// AUTH TOKEN TYPES
// ============================================================

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresIn: number
  user: UserProfile
}

// ============================================================
// HTTP CLIENT CORE
// ============================================================

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT'

interface RequestConfig {
  method: HttpMethod
  path: string
  body?: Record<string, unknown>
  query?: Record<string, string | number | boolean | undefined>
  auth?: boolean
  stream?: boolean
}

export interface TribeClientConfig {
  baseUrl: string
  getToken?: () => string | null
  onTokenExpired?: () => Promise<string | null>
  onError?: (error: TribeApiError) => void
}

async function request<T>(config: TribeClientConfig, req: RequestConfig): Promise<T> {
  const url = new URL(req.path, config.baseUrl)

  if (req.query) {
    Object.entries(req.query).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }

  if (req.auth !== false && config.getToken) {
    const token = config.getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(url.toString(), {
    method: req.method,
    headers,
    body: req.body ? JSON.stringify(req.body) : undefined,
  })

  if (res.status === 401 && config.onTokenExpired) {
    const newToken = await config.onTokenExpired()
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`
      const retry = await fetch(url.toString(), {
        method: req.method,
        headers,
        body: req.body ? JSON.stringify(req.body) : undefined,
      })
      if (!retry.ok) {
        const errData = await retry.json().catch(() => ({ error: 'Request failed', code: 'UNKNOWN' }))
        throw new TribeApiError(errData, retry.status)
      }
      return retry.json() as Promise<T>
    }
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ error: 'Request failed', code: 'UNKNOWN' }))
    if (config.onError) config.onError(new TribeApiError(errData, res.status))
    throw new TribeApiError(errData, res.status)
  }

  if (res.status === 204) return {} as T
  return res.json() as Promise<T>
}

// ============================================================
// API CLIENT FACTORY
// ============================================================

export function createTribeClient(config: TribeClientConfig) {
  const r = <T>(req: RequestConfig) => request<T>(config, req)

  return {
    /** Resolve avatar media ID to full URL */
    resolveAvatarUrl(avatar: string | null): string | null {
      return avatar ? `${config.baseUrl}/media/${avatar}` : null
    },

    /** Resolve any media ID to full URL */
    resolveMediaUrl(mediaId: string): string {
      return `${config.baseUrl}/media/${mediaId}`
    },

    // ========== AUTH (9 routes) ==========
    auth: {
      register(body: { phone: string; pin: string; displayName: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/register', body, auth: false })
      },
      login(body: { phone: string; pin: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/login', body, auth: false })
      },
      refresh(body: { refreshToken: string }) {
        return r<{ data: AuthTokens }>({ method: 'POST', path: '/auth/refresh', body, auth: false })
      },
      logout() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/auth/logout' })
      },
      me() {
        return r<{ data: { user: UserProfile } }>({ method: 'GET', path: '/auth/me' })
      },
      sessions() {
        return r<{ data: { sessions: Session[] } }>({ method: 'GET', path: '/auth/sessions' })
      },
      revokeAllSessions() {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: '/auth/sessions' })
      },
      revokeSession(sessionId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/auth/sessions/${sessionId}` })
      },
      changePin(body: { currentPin: string; newPin: string }) {
        return r<{ data: { message: string } }>({ method: 'PATCH', path: '/auth/pin', body })
      },
    },

    // ========== ME / PROFILE (4 routes) ==========
    me: {
      updateProfile(body: { displayName?: string; username?: string; bio?: string; avatarMediaId?: string }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/profile', body })
      },
      setAge(body: { birthYear: number }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/age', body })
      },
      setCollege(body: { collegeId: string | null }) {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/college', body })
      },
      completeOnboarding() {
        return r<{ data: { user: UserProfile } }>({ method: 'PATCH', path: '/me/onboarding', body: {} })
      },
    },

    // ========== CONTENT (3 routes) ==========
    content: {
      create(body: { caption?: string; mediaIds?: string[]; kind?: 'POST' | 'REEL' | 'STORY'; syntheticDeclaration?: boolean }) {
        return r<{ data: ContentItem }>({ method: 'POST', path: '/content/posts', body })
      },
      get(id: string) {
        return r<{ data: ContentItem }>({ method: 'GET', path: `/content/${id}` })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${id}` })
      },
    },

    // ========== FEED (6 routes) ==========
    feed: {
      public(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/public', query: params })
      },
      following(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/following', query: params })
      },
      college(collegeId: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/feed/college/${collegeId}`, query: params })
      },
      house(houseId: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/feed/house/${houseId}`, query: params })
      },
      stories() {
        return r<{ data: { storyGroups: Array<{ user: UserSnippet; stories: ContentItem[]; hasUnviewed: boolean }> } }>({ method: 'GET', path: '/feed/stories' })
      },
      reels(params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: '/feed/reels', query: params })
      },
    },

    // ========== SOCIAL (10 routes) ==========
    social: {
      follow(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/follow/${userId}` })
      },
      unfollow(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/follow/${userId}` })
      },
      like(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/like` })
      },
      dislike(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/dislike` })
      },
      removeReaction(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${contentId}/reaction` })
      },
      save(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/content/${contentId}/save` })
      },
      unsave(contentId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/content/${contentId}/save` })
      },
      comment(contentId: string, body: { body: string; parentId?: string }) {
        return r<{ data: Comment }>({ method: 'POST', path: `/content/${contentId}/comments`, body })
      },
      getComments(contentId: string, params?: CursorParams) {
        return r<{ data: { comments: Comment[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/content/${contentId}/comments`, query: params })
      },
    },

    // ========== USERS (5 routes) ==========
    users: {
      get(id: string) {
        return r<{ data: { user: UserProfile } }>({ method: 'GET', path: `/users/${id}` })
      },
      posts(id: string, params?: CursorParams & { kind?: 'POST' | 'REEL' | 'STORY' }) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/users/${id}/posts`, query: params })
      },
      followers(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/users/${id}/followers`, query: params })
      },
      following(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/users/${id}/following`, query: params })
      },
      saved(id: string, params?: CursorParams) {
        return r<{ data: CursorPage<ContentItem> }>({ method: 'GET', path: `/users/${id}/saved`, query: params })
      },
    },

    // ========== DISCOVERY (11 routes) ==========
    discovery: {
      searchColleges(params: { q?: string; state?: string; type?: string } & OffsetParams) {
        return r<{ data: { colleges: College[]; total: number } }>({ method: 'GET', path: '/colleges/search', query: params })
      },
      collegeStates() {
        return r<{ data: { states: string[] } }>({ method: 'GET', path: '/colleges/states', auth: false })
      },
      collegeTypes() {
        return r<{ data: { types: string[] } }>({ method: 'GET', path: '/colleges/types', auth: false })
      },
      getCollege(id: string) {
        return r<{ data: College }>({ method: 'GET', path: `/colleges/${id}`, auth: false })
      },
      collegeMembers(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/colleges/${id}/members`, query: params })
      },
      houses() {
        return r<{ data: { houses: House[] } }>({ method: 'GET', path: '/houses', auth: false })
      },
      houseLeaderboard() {
        return r<{ data: { houses: House[] } }>({ method: 'GET', path: '/houses/leaderboard', auth: false })
      },
      getHouse(idOrSlug: string) {
        return r<{ data: House }>({ method: 'GET', path: `/houses/${idOrSlug}`, auth: false })
      },
      houseMembers(idOrSlug: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/houses/${idOrSlug}/members`, query: params })
      },
      search(params: { q: string; type?: 'all' | 'users' | 'colleges' | 'houses' } & OffsetParams) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/search', query: params, auth: false })
      },
      suggestions() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/suggestions/users' })
      },
    },

    // ========== MEDIA (2 routes) ==========
    media: {
      upload(body: { data: string; mimeType: string; type?: 'IMAGE' | 'VIDEO' | 'AUDIO'; width?: number; height?: number; duration?: number }) {
        return r<{ data: MediaObject }>({ method: 'POST', path: '/media/upload', body })
      },
      /** Returns the URL to fetch binary media. Use in <img src> or fetch directly. */
      url(id: string): string {
        return `${config.baseUrl}/media/${id}`
      },
    },

    // ========== STORIES (33 routes) ==========
    stories: {
      create(body: { type: 'TEXT' | 'IMAGE' | 'VIDEO'; text?: string; mediaId?: string; caption?: string; stickers?: Sticker[]; privacy?: 'EVERYONE' | 'CLOSE_FRIENDS' | 'CUSTOM'; background?: Record<string, unknown> }) {
        return r<{ data: Story }>({ method: 'POST', path: '/stories', body })
      },
      feed() {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: '/stories/feed' })
      },
      get(id: string) {
        return r<{ data: Story }>({ method: 'GET', path: `/stories/${id}` })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/stories/${id}` })
      },
      views(id: string) {
        return r<{ data: { views: UserSnippet[] } }>({ method: 'GET', path: `/stories/${id}/views` })
      },
      react(id: string, body: { emoji: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/react`, body })
      },
      removeReaction(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/stories/${id}/react` })
      },
      reply(id: string, body: { text: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/reply`, body })
      },
      replies(id: string) {
        return r<{ data: { replies: Array<{ id: string; text: string; author: UserSnippet; createdAt: ISODate }> } }>({ method: 'GET', path: `/stories/${id}/replies` })
      },
      respondToSticker(storyId: string, stickerId: string, body: { response: string | number }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${storyId}/sticker/${stickerId}/respond`, body })
      },
      stickerResults(storyId: string, stickerId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/stories/${storyId}/sticker/${stickerId}/results` })
      },
      stickerResponses(storyId: string, stickerId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/stories/${storyId}/sticker/${stickerId}/responses` })
      },
      archive() {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: '/me/stories/archive' })
      },
      userStories(userId: string) {
        return r<{ data: { stories: Story[] } }>({ method: 'GET', path: `/users/${userId}/stories` })
      },
      report(id: string, body: { reason: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/stories/${id}/report`, body })
      },
      // Close Friends
      closeFriends() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/me/close-friends' })
      },
      addCloseFriend(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/me/close-friends/${userId}` })
      },
      removeCloseFriend(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/close-friends/${userId}` })
      },
      // Highlights
      createHighlight(body: { name: string; coverStoryId?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/me/highlights', body })
      },
      userHighlights(userId: string) {
        return r<{ data: { highlights: Array<Record<string, unknown>> } }>({ method: 'GET', path: `/users/${userId}/highlights` })
      },
      updateHighlight(id: string, body: { name?: string; addStoryIds?: string[]; removeStoryIds?: string[]; coverStoryId?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/me/highlights/${id}`, body })
      },
      deleteHighlight(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/highlights/${id}` })
      },
      // Settings
      getSettings() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/story-settings' })
      },
      updateSettings(body: { defaultPrivacy?: string; replyPrivacy?: string; autoArchive?: boolean; hideStoryFrom?: string[] }) {
        return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: '/me/story-settings', body })
      },
    },

    // ========== BLOCKS (3 routes) ==========
    blocks: {
      list() {
        return r<{ data: { users: UserSnippet[] } }>({ method: 'GET', path: '/me/blocks' })
      },
      block(userId: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/me/blocks/${userId}` })
      },
      unblock(userId: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/blocks/${userId}` })
      },
    },

    // ========== REELS (36 routes) ==========
    reels: {
      create(body: { mediaId: string; caption?: string; audioId?: string; isRemixOf?: string; tags?: string[]; draft?: boolean }) {
        return r<{ data: Reel }>({ method: 'POST', path: '/reels', body })
      },
      feed(params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: '/reels/feed', query: params })
      },
      following(params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: '/reels/following', query: params })
      },
      userReels(userId: string, params?: CursorParams) {
        return r<{ data: CursorPage<Reel> }>({ method: 'GET', path: `/users/${userId}/reels`, query: params })
      },
      get(id: string) {
        return r<{ data: Reel }>({ method: 'GET', path: `/reels/${id}` })
      },
      update(id: string, body: { caption?: string; tags?: string[] }) {
        return r<{ data: Reel }>({ method: 'PATCH', path: `/reels/${id}`, body })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}` })
      },
      publish(id: string) {
        return r<{ data: Reel }>({ method: 'POST', path: `/reels/${id}/publish` })
      },
      archive(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/archive` })
      },
      restore(id: string) {
        return r<{ data: Reel }>({ method: 'POST', path: `/reels/${id}/restore` })
      },
      pin(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/pin` })
      },
      unpin(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/pin` })
      },
      like(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/like` })
      },
      unlike(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/like` })
      },
      save(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/save` })
      },
      unsave(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/reels/${id}/save` })
      },
      comment(id: string, body: { text: string; parentId?: string }) {
        return r<{ data: Comment }>({ method: 'POST', path: `/reels/${id}/comment`, body })
      },
      comments(id: string, params?: CursorParams) {
        return r<{ data: { comments: Comment[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/reels/${id}/comments`, query: params })
      },
      report(id: string, body: { reason: string; details?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/report`, body })
      },
      hide(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/hide` })
      },
      notInterested(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/not-interested` })
      },
      share(id: string, body?: { platform?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/share`, body })
      },
      recordWatch(id: string, body: { watchTimeMs: number; completionRate?: number }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/watch`, body, auth: false })
      },
      recordView(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/reels/${id}/view`, auth: false })
      },
      audioReels(audioId: string) {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: `/reels/audio/${audioId}`, auth: false })
      },
      remixes(id: string) {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: `/reels/${id}/remixes`, auth: false })
      },
      createSeries(body: { name: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/me/reels/series', body })
      },
      userSeries(userId: string) {
        return r<{ data: { series: Array<Record<string, unknown>> } }>({ method: 'GET', path: `/users/${userId}/reels/series`, auth: false })
      },
      myArchive() {
        return r<{ data: { reels: Reel[] } }>({ method: 'GET', path: '/me/reels/archive' })
      },
      myAnalytics() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/reels/analytics' })
      },
      updateProcessing(id: string, body: Record<string, unknown>) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/reels/${id}/processing`, body })
      },
      getProcessing(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/reels/${id}/processing` })
      },
    },

    // ========== TRIBES (9 public routes) ==========
    tribes: {
      list() {
        return r<{ data: { tribes: Tribe[] } }>({ method: 'GET', path: '/tribes', auth: false })
      },
      standings() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribes/standings/current', auth: false })
      },
      get(id: string) {
        return r<{ data: Tribe }>({ method: 'GET', path: `/tribes/${id}`, auth: false })
      },
      members(id: string, params?: OffsetParams) {
        return r<{ data: OffsetPage<UserSnippet> }>({ method: 'GET', path: `/tribes/${id}/members`, query: params, auth: false })
      },
      board(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/board`, auth: false })
      },
      fund(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/fund`, auth: false })
      },
      salutes(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribes/${id}/salutes`, auth: false })
      },
      myTribe() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/tribe' })
      },
      userTribe(userId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/users/${userId}/tribe`, auth: false })
      },
    },

    // ========== TRIBE CONTESTS (13 public routes) ==========
    contests: {
      list() {
        return r<{ data: { contests: TribeContest[] } }>({ method: 'GET', path: '/tribe-contests', auth: false })
      },
      liveFeed() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribe-contests/live-feed', auth: false })
      },
      get(id: string) {
        return r<{ data: { contest: TribeContest } }>({ method: 'GET', path: `/tribe-contests/${id}` })
      },
      live(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/live`, auth: false })
      },
      entries(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/entries` })
      },
      leaderboard(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/leaderboard` })
      },
      results(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/${id}/results` })
      },
      enter(id: string, body: { entryData: Record<string, unknown> }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/tribe-contests/${id}/enter`, body })
      },
      vote(id: string, body: { entryId: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/tribe-contests/${id}/vote`, body })
      },
      withdraw(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/tribe-contests/${id}/withdraw` })
      },
      seasons() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/tribe-contests/seasons', auth: false })
      },
      seasonStandings(seasonId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/seasons/${seasonId}/standings`, auth: false })
      },
      seasonLiveStandings(seasonId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/tribe-contests/seasons/${seasonId}/live-standings`, auth: false })
      },
    },

    // ========== EVENTS (18 user routes) ==========
    events: {
      create(body: { title: string; description?: string; eventType?: string; startDate: string; endDate?: string; location?: string; collegeId?: string; maxAttendees?: number }) {
        return r<{ data: Event }>({ method: 'POST', path: '/events', body })
      },
      feed(params?: CursorParams) {
        return r<{ data: CursorPage<Event> }>({ method: 'GET', path: '/events/feed', query: params })
      },
      search(params: { q?: string; eventType?: string; collegeId?: string }) {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/events/search', query: params, auth: false })
      },
      collegeEvents(collegeId: string) {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: `/events/college/${collegeId}`, auth: false })
      },
      get(id: string) {
        return r<{ data: Event }>({ method: 'GET', path: `/events/${id}` })
      },
      update(id: string, body: Partial<{ title: string; description: string; startDate: string; endDate: string; location: string; maxAttendees: number }>) {
        return r<{ data: Event }>({ method: 'PATCH', path: `/events/${id}`, body })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/events/${id}` })
      },
      publish(id: string) {
        return r<{ data: Event }>({ method: 'POST', path: `/events/${id}/publish` })
      },
      cancel(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/cancel` })
      },
      rsvp(id: string, body: { status: 'GOING' | 'INTERESTED' | 'NOT_GOING' }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/rsvp`, body })
      },
      cancelRsvp(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/events/${id}/rsvp` })
      },
      attendees(id: string) {
        return r<{ data: { attendees: UserSnippet[] } }>({ method: 'GET', path: `/events/${id}/attendees` })
      },
      report(id: string, body: { reason: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/events/${id}/report`, body })
      },
      myEvents() {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/me/events' })
      },
      myRsvps() {
        return r<{ data: { events: Event[] } }>({ method: 'GET', path: '/me/events/rsvps' })
      },
    },

    // ========== BOARD NOTICES (13 routes) ==========
    notices: {
      create(body: { title: string; body: string; priority?: 'NORMAL' | 'IMPORTANT' | 'URGENT'; collegeId: string }) {
        return r<{ data: BoardNotice }>({ method: 'POST', path: '/board/notices', body })
      },
      get(id: string) {
        return r<{ data: BoardNotice }>({ method: 'GET', path: `/board/notices/${id}` })
      },
      update(id: string, body: { title?: string; body?: string; priority?: string }) {
        return r<{ data: BoardNotice }>({ method: 'PATCH', path: `/board/notices/${id}`, body })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/board/notices/${id}` })
      },
      pin(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/board/notices/${id}/pin` })
      },
      unpin(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/board/notices/${id}/pin` })
      },
      acknowledge(id: string) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/board/notices/${id}/acknowledge` })
      },
      acknowledgments(id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/board/notices/${id}/acknowledgments` })
      },
      collegeNotices(collegeId: string, params?: CursorParams) {
        return r<{ data: { notices: BoardNotice[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: `/colleges/${collegeId}/notices`, query: params })
      },
      myNotices() {
        return r<{ data: { notices: BoardNotice[] } }>({ method: 'GET', path: '/me/board/notices' })
      },
    },

    // ========== RESOURCES (10 user routes) ==========
    resources: {
      create(body: { kind: string; collegeId: string; title: string; subject?: string; branch?: string; semester?: number; year?: number; description?: string; fileAssetId: string }) {
        return r<{ data: Resource }>({ method: 'POST', path: '/resources', body })
      },
      search(params: { collegeId?: string; branch?: string; subject?: string; semester?: number; kind?: string; year?: number; q?: string; sort?: 'recent' | 'popular' | 'most_downloaded' } & CursorParams) {
        return r<{ data: { resources: Resource[]; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: '/resources/search', query: params, auth: false })
      },
      get(id: string) {
        return r<{ data: Resource }>({ method: 'GET', path: `/resources/${id}` })
      },
      update(id: string, body: Partial<{ title: string; subject: string; branch: string; semester: number; year: number; description: string }>) {
        return r<{ data: Resource }>({ method: 'PATCH', path: `/resources/${id}`, body })
      },
      delete(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/resources/${id}` })
      },
      report(id: string, body: { reason: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/resources/${id}/report`, body })
      },
      vote(id: string, body: { vote: 'UP' | 'DOWN' }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: `/resources/${id}/vote`, body })
      },
      removeVote(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/resources/${id}/vote` })
      },
      download(id: string) {
        return r<{ data: { url: string } }>({ method: 'POST', path: `/resources/${id}/download` })
      },
      myResources() {
        return r<{ data: { resources: Resource[] } }>({ method: 'GET', path: '/me/resources' })
      },
    },

    // ========== GOVERNANCE (8 routes) ==========
    governance: {
      board(collegeId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/board`, auth: false })
      },
      apply(collegeId: string, body?: { statement?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/college/${collegeId}/apply`, body })
      },
      applications(collegeId: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/applications`, auth: false })
      },
      voteApplication(appId: string, body: { vote: 'APPROVE' | 'REJECT' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/applications/${appId}/vote`, body })
      },
      createProposal(collegeId: string, body: { title: string; description: string; category?: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/college/${collegeId}/proposals`, body })
      },
      proposals(collegeId: string, params?: { status?: 'OPEN' | 'PASSED' | 'REJECTED' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/governance/college/${collegeId}/proposals`, query: params, auth: false })
      },
      voteProposal(proposalId: string, body: { vote: 'FOR' | 'AGAINST' | 'ABSTAIN' }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/governance/proposals/${proposalId}/vote`, body })
      },
    },

    // ========== NOTIFICATIONS (2 routes) ==========
    notifications: {
      list(params?: CursorParams) {
        return r<{ data: { notifications: Notification[]; unreadCount: number; nextCursor: string | null; hasMore: boolean } }>({ method: 'GET', path: '/notifications', query: params })
      },
      markRead(body?: { ids?: string[] }) {
        return r<{ data: { message: string } }>({ method: 'PATCH', path: '/notifications/read', body })
      },
    },

    // ========== REPORTS (1 route) ==========
    reports: {
      create(body: { targetType: string; targetId: string; reasonCode: string; details?: string }) {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/reports', body })
      },
    },

    // ========== APPEALS (3 routes) ==========
    appeals: {
      create(body: { targetType: string; targetId: string; reason: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/appeals', body })
      },
      list() {
        return r<{ data: { appeals: Array<Record<string, unknown>> } }>({ method: 'GET', path: '/appeals' })
      },
    },

    // ========== LEGAL (2 routes) ==========
    legal: {
      consent() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/legal/consent', auth: false })
      },
      accept() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/legal/accept', body: {} })
      },
    },

    // ========== GRIEVANCES (2 routes) ==========
    grievances: {
      create(body: { ticketType: string; subject: string; description: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/grievances', body })
      },
      list() {
        return r<{ data: { grievances: Array<Record<string, unknown>> } }>({ method: 'GET', path: '/grievances' })
      },
    },

    // ========== COLLEGE CLAIMS (3 user routes) ==========
    claims: {
      submit(collegeId: string, body: { claimType: string; evidence: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/colleges/${collegeId}/claim`, body })
      },
      myClaims() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/me/college-claims' })
      },
      withdraw(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/me/college-claims/${id}` })
      },
    },

    // ========== AUTHENTICITY (3 user routes) ==========
    authenticity: {
      tag(body: { targetType: string; targetId: string; declaration: string }) {
        return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/authenticity/tag', body })
      },
      getTags(type: string, id: string) {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/authenticity/tags/${type}/${id}` })
      },
      removeTag(id: string) {
        return r<{ data: { message: string } }>({ method: 'DELETE', path: `/authenticity/tags/${id}` })
      },
    },

    // ========== ADMIN (all admin routes behind role guard) ==========
    admin: {
      stats() {
        return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stats' })
      },
      seedColleges() {
        return r<{ data: { message: string } }>({ method: 'POST', path: '/admin/colleges/seed' })
      },
      moderation: {
        queue(params?: { bucket?: 'held' | 'reports' | 'appeals' } & OffsetParams) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/moderation/queue', query: params })
        },
        action(contentId: string, body: { action: 'APPROVE' | 'REMOVE' | 'SHADOW_LIMIT' | 'HOLD' | 'STRIKE'; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/moderation/${contentId}/action`, body })
        },
        decideAppeal(id: string, body: { action: 'APPROVE' | 'REJECT' | 'REQUEST_MORE_INFO'; reasonCodes?: string[]; notes?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/appeals/${id}/decide`, body })
        },
      },
      stories: {
        list(params?: { status?: string; authorId?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stories', query: params })
        },
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/stories/${id}/moderate`, body })
        },
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/stories/analytics' })
        },
        cleanup() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/stories/cleanup' })
        },
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/stories/${id}/recompute-counters` })
        },
      },
      reels: {
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/reels' })
        },
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/reels/${id}/moderate`, body })
        },
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/reels/analytics' })
        },
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/reels/${id}/recompute-counters` })
        },
      },
      events: {
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/events' })
        },
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/events/${id}/moderate`, body })
        },
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/events/analytics' })
        },
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/events/${id}/recompute-counters` })
        },
      },
      distribution: {
        evaluate() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/evaluate' })
        },
        evaluateOne(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/distribution/evaluate/${contentId}` })
        },
        config() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/distribution/config' })
        },
        killSwitch() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/kill-switch' })
        },
        inspect(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/distribution/inspect/${contentId}` })
        },
        override(body: { contentId: string; stage: number; reason: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/distribution/override', body })
        },
        removeOverride(contentId: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'DELETE', path: `/admin/distribution/override/${contentId}` })
        },
      },
      collegeClaims: {
        list(params?: { status?: string; fraudOnly?: boolean }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/college-claims', query: params })
        },
        get(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/college-claims/${id}` })
        },
        flagFraud(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/college-claims/${id}/flag-fraud` })
        },
        decide(id: string, body: { approve: boolean; reasonCodes?: string[]; notes?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/college-claims/${id}/decide`, body })
        },
      },
      resources: {
        list(params?: { status?: string; collegeId?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/resources', query: params })
        },
        moderate(id: string, body: { action: string; reason?: string }) {
          return r<{ data: Record<string, unknown> }>({ method: 'PATCH', path: `/admin/resources/${id}/moderate`, body })
        },
        recomputeCounters(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/resources/${id}/recompute-counters` })
        },
        reconcile() {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/resources/reconcile' })
        },
      },
      boardNotices: {
        modQueue() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/moderation/board-notices' })
        },
        decide(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/moderation/board-notices/${id}/decide`, body })
        },
        analytics() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/board-notices/analytics' })
        },
      },
      tribes: {
        distribution() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribes/distribution' })
        },
        reassign(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribes/reassign', body })
        },
        createSeason(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-seasons', body })
        },
        seasons() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-seasons' })
        },
      },
      contests: {
        create(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-contests', body })
        },
        list() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-contests' })
        },
        get(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: `/admin/tribe-contests/${id}` })
        },
        publish(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/publish` })
        },
        openEntries(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/open-entries` })
        },
        closeEntries(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/close-entries` })
        },
        lock(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/lock` })
        },
        resolve(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/resolve` })
        },
        cancel(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/cancel` })
        },
        disqualify(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/disqualify`, body })
        },
        judgeScore(id: string, body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/judge-score`, body })
        },
        computeScores(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/compute-scores` })
        },
        recomputeBroadcast(id: string) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: `/admin/tribe-contests/${id}/recompute-broadcast` })
        },
        rules(body: Record<string, unknown>) {
          return r<{ data: Record<string, unknown> }>({ method: 'POST', path: '/admin/tribe-contests/rules', body })
        },
        dashboard() {
          return r<{ data: Record<string, unknown> }>({ method: 'GET', path: '/admin/tribe-contests/dashboard' })
        },
      },
    },
  }
}

// ============================================================
// CONVENIENCE: Pre-configured client type
// ============================================================
export type TribeClient = ReturnType<typeof createTribeClient>
