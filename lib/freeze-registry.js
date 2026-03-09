/**
 * B0 Freeze Registry — Canonical Source of Truth
 * 
 * This module is the CODE-LEVEL enforcement of the Backend Freeze.
 * Every route is mapped to its freeze label. Headers are injected automatically.
 * 
 * RULES:
 * - No endpoint can exist without a freeze label
 * - DEPRECATED endpoints return 410
 * - LEGACY endpoints get X-Deprecated: true
 * - All responses get X-Contract-Version: v1
 * - Modifying this file requires explicit permission
 * 
 * FREEZE STATUS: LOCKED
 */

// ========== FREEZE LABELS ==========
export const FreezeLabel = {
  CANONICAL: 'canonical',
  ANDROID_V1_USE: 'android_v1_use',
  ADMIN_ONLY: 'admin_only',
  BOARD_ONLY: 'board_only',
  INTERNAL_ONLY: 'internal_only',
  LEGACY: 'legacy',
  DEPRECATED: 'deprecated',
}

// ========== CONTRACT VERSION ==========
export const CONTRACT_VERSION = 'v2'

// ========== FREEZE REGISTRY ==========
// Each entry: { pattern: RegExp, method: string|'*', label: string }
const FREEZE_ROUTES = [
  // ---- AUTH ----
  { pattern: /^\/auth\/register$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/login$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/logout$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/me$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/sessions$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/sessions$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/auth\/pin$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },

  // ---- ONBOARDING & PROFILE ----
  { pattern: /^\/me\/profile$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/age$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/college$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/onboarding$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },

  // ---- CONTENT ----
  { pattern: /^\/content\/posts$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },

  // ---- FEEDS ----
  { pattern: /^\/feed\/public$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/feed\/following$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/feed\/college\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/feed\/house\/[^/]+$/, method: 'GET', label: FreezeLabel.LEGACY },
  { pattern: /^\/feed\/stories$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/feed\/reels$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },

  // ---- SOCIAL ----
  { pattern: /^\/follow\/[^/]+$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/follow\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/like$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/dislike$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/reaction$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/save$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/save$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/comments$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/content\/[^/]+\/comments$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },

  // ---- USERS & DISCOVERY ----
  { pattern: /^\/users\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/posts$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/followers$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/following$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/saved$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/search$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/suggestions\/users$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/colleges\/search$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/colleges\/states$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/colleges\/types$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/colleges\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/colleges\/[^/]+\/members$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },

  // ---- HOUSES (LEGACY) ----
  { pattern: /^\/houses$/, method: 'GET', label: FreezeLabel.LEGACY },
  { pattern: /^\/houses\/leaderboard$/, method: 'GET', label: FreezeLabel.LEGACY },
  { pattern: /^\/houses\/[^/]+$/, method: 'GET', label: FreezeLabel.LEGACY },

  // ---- HOUSE POINTS (DEPRECATED) ----
  { pattern: /^\/house-points$/, method: '*', label: FreezeLabel.DEPRECATED },

  // ---- MEDIA ----
  { pattern: /^\/media\/upload$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/media\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },

  // ---- COLLEGE CLAIMS ----
  { pattern: /^\/colleges\/[^/]+\/claim$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/college-claims$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/college-claims\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/college-claims/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- DISTRIBUTION (ADMIN) ----
  { pattern: /^\/admin\/distribution/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- RESOURCES ----
  { pattern: /^\/resources$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/resources\/search$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/resources\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/resources\/[^/]+\/vote$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/resources\/[^/]+\/download$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/resources\/[^/]+\/report$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/resources$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/resources/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- EVENTS ----
  { pattern: /^\/events$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/search$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/feed$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/college\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/publish$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/cancel$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/rsvp$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/rsvp$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/attendees$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/report$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/remind$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/events\/[^/]+\/remind$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/events$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/events\/rsvps$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/events/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- BOARD NOTICES ----
  { pattern: /^\/board\/notices$/, method: 'POST', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/board\/notices\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/board\/notices\/[^/]+$/, method: 'PATCH', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/board\/notices\/[^/]+$/, method: 'DELETE', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/board\/notices\/[^/]+\/pin$/, method: 'POST', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/board\/notices\/[^/]+\/pin$/, method: 'DELETE', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/board\/notices\/[^/]+\/acknowledge$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/board\/notices\/[^/]+\/acknowledgments$/, method: 'GET', label: FreezeLabel.CANONICAL },
  { pattern: /^\/colleges\/[^/]+\/notices$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/board\/notices$/, method: 'GET', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/moderation\/board-notices/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/board-notices/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/authenticity/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- AUTHENTICITY TAGS ----
  { pattern: /^\/authenticity\/tag$/, method: 'POST', label: FreezeLabel.BOARD_ONLY },
  { pattern: /^\/authenticity\/tags\/[^/]+\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/authenticity\/tags\/[^/]+$/, method: 'DELETE', label: FreezeLabel.BOARD_ONLY },

  // ---- STORIES ----
  { pattern: /^\/stories$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/feed$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/views$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/react$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/react$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/reply$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/replies$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/sticker\/[^/]+\/respond$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/sticker\/[^/]+\/results$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/[^/]+\/sticker\/[^/]+\/responses$/, method: 'GET', label: FreezeLabel.CANONICAL },
  { pattern: /^\/stories\/[^/]+\/report$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/stories\/events\/stream$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/stories\/archive$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/stories$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/close-friends/, method: '*', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/highlights/, method: '*', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/highlights$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/story-settings$/, method: '*', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/blocks/, method: '*', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/stories/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- REELS ----
  { pattern: /^\/reels$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/feed$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/following$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/publish$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/archive$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/restore$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/pin$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/pin$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/like$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/like$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/save$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/save$/, method: 'DELETE', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/comment$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/comments$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/report$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/audio\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/remixes$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/reels\/series$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/reels\/series$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/reels\/archive$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/reels\/analytics$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/reels$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/reels\/[^/]+\/processing$/, method: 'POST', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/reels\/[^/]+\/processing$/, method: 'GET', label: FreezeLabel.CANONICAL },
  { pattern: /^\/admin\/reels/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- TRIBES ----
  { pattern: /^\/tribes$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/standings\/current$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/[^/]+\/members$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/[^/]+\/board$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/[^/]+\/fund$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribes\/[^/]+\/salutes$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/me\/tribe$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/users\/[^/]+\/tribe$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/tribes/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/tribe-seasons/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/tribe-awards/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/tribe-salutes/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- TRIBE CONTESTS (public) ----
  { pattern: /^\/tribe-contests$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/seasons$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/live-feed$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/seasons\/[^/]+\/standings$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/seasons\/[^/]+\/live-standings$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/enter$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/entries$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/leaderboard$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/results$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/vote$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/withdraw$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/tribe-contests\/[^/]+\/live$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },

  // ---- TRIBE CONTESTS (admin) ----
  { pattern: /^\/admin\/tribe-contests/, method: '*', label: FreezeLabel.ADMIN_ONLY },

  // ---- GOVERNANCE ----
  { pattern: /^\/governance\/college\/[^/]+\/board$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/college\/[^/]+\/apply$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/college\/[^/]+\/applications$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/applications\/[^/]+\/vote$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/college\/[^/]+\/proposals$/, method: '*', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/proposals\/[^/]+\/vote$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/governance\/college\/[^/]+\/seed-board$/, method: 'POST', label: FreezeLabel.ADMIN_ONLY },

  // ---- MODERATION / REPORTS / ADMIN ----
  { pattern: /^\/reports$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/moderation\/queue$/, method: 'GET', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/moderation\/[^/]+\/action$/, method: 'POST', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/appeals$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/appeals$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/appeals\/[^/]+\/decide$/, method: '*', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/grievances$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/grievances$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/admin\/colleges\/seed$/, method: 'POST', label: FreezeLabel.ADMIN_ONLY },
  { pattern: /^\/admin\/stats$/, method: 'GET', label: FreezeLabel.ADMIN_ONLY },

  // ---- NOTIFICATIONS & LEGAL ----
  { pattern: /^\/notifications$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/notifications\/read$/, method: 'PATCH', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/legal\/consent$/, method: 'GET', label: FreezeLabel.ANDROID_V1_USE },
  { pattern: /^\/legal\/accept$/, method: 'POST', label: FreezeLabel.ANDROID_V1_USE },

  // ---- OPS / HEALTH ----
  { pattern: /^\/$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/healthz$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/readyz$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/ops\/health$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/ops\/metrics$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/ops\/backup-check$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/cache\/stats$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/moderation\/config$/, method: 'GET', label: FreezeLabel.INTERNAL_ONLY },
  { pattern: /^\/moderation\/check$/, method: 'POST', label: FreezeLabel.INTERNAL_ONLY },
]

/**
 * Get freeze label for a given route and method
 * Returns { label, isCanonical, isLegacy, isDeprecated }
 */
export function getFreezeStatus(route, method) {
  for (const entry of FREEZE_ROUTES) {
    if (entry.pattern.test(route) && (entry.method === '*' || entry.method === method)) {
      return {
        label: entry.label,
        isCanonical: entry.label === FreezeLabel.CANONICAL || entry.label === FreezeLabel.ANDROID_V1_USE,
        isLegacy: entry.label === FreezeLabel.LEGACY,
        isDeprecated: entry.label === FreezeLabel.DEPRECATED,
        isAdmin: entry.label === FreezeLabel.ADMIN_ONLY,
        isBoard: entry.label === FreezeLabel.BOARD_ONLY,
        isInternal: entry.label === FreezeLabel.INTERNAL_ONLY,
      }
    }
  }
  // Unknown route — flag it
  return {
    label: 'unknown',
    isCanonical: false,
    isLegacy: false,
    isDeprecated: false,
    isAdmin: false,
    isBoard: false,
    isInternal: false,
  }
}

/**
 * Apply freeze headers to a response
 */
export function applyFreezeHeaders(response, route, method) {
  const status = getFreezeStatus(route, method)

  // Always: contract version
  response.headers.set('X-Contract-Version', CONTRACT_VERSION)

  // Freeze status
  response.headers.set('X-Freeze-Status', status.label)

  // Deprecation markers
  if (status.isLegacy) {
    response.headers.set('X-Deprecated', 'true')
    response.headers.set('X-Deprecation-Notice', 'This endpoint is legacy. Use tribe-based endpoints instead.')
  }

  if (status.isDeprecated) {
    response.headers.set('X-Deprecated', 'true')
    response.headers.set('X-Deprecation-Notice', 'This endpoint is permanently deprecated and will be removed.')
  }

  return response
}

/**
 * Validate that all registered routes are accounted for
 * Used by contract test suite
 */
export function getRegisteredRouteCount() {
  return FREEZE_ROUTES.length
}

/**
 * Export full registry for testing
 */
export function getFullRegistry() {
  return FREEZE_ROUTES.map(r => ({
    pattern: r.pattern.toString(),
    method: r.method,
    label: r.label,
  }))
}
