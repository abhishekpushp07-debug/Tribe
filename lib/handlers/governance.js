import { v4 as uuidv4 } from 'uuid'
import { requireAuth, writeAudit, sanitizeUser, parsePagination } from '../auth-utils.js'
import { ErrorCode } from '../constants.js'

/**
 * Board Governance System
 * 
 * Each college has an 11-member board. Members can:
 * - Apply for a seat (open applications)
 * - Create proposals (rule changes, events, etc.)
 * - Vote on proposals (majority required)
 * 
 * Collections: board_seats, board_applications, board_proposals
 */

const BOARD_SIZE = 11
const APPLICATION_WINDOW_DAYS = 7
const PROPOSAL_VOTING_DAYS = 3

export async function handleGovernance(path, method, request, db) {
  const route = path.join('/')

  // ========================
  // GET /governance/college/:collegeId/board — Current board
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'board' && method === 'GET') {
    const collegeId = path[2]

    const seats = await db.collection('board_seats')
      .find({ collegeId, status: 'ACTIVE' })
      .sort({ seatNumber: 1 })
      .toArray()

    const userIds = seats.map(s => s.userId)
    const users = await db.collection('users').find({ id: { $in: userIds } }).toArray()
    const userMap = Object.fromEntries(users.map(u => [u.id, sanitizeUser(u)]))

    const board = seats.map(s => {
      const { _id, ...rest } = s
      return { ...rest, user: userMap[s.userId] || null }
    })

    return {
      data: {
        board,
        collegeId,
        totalSeats: BOARD_SIZE,
        filledSeats: seats.length,
        vacantSeats: BOARD_SIZE - seats.length,
      },
    }
  }

  // ========================
  // POST /governance/college/:collegeId/apply — Apply for a board seat
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'apply' && method === 'POST') {
    const user = await requireAuth(request, db)
    const collegeId = path[2]

    if (user.collegeId !== collegeId) {
      return { error: 'You can only apply for your own college board', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    // Check if already on board
    const existingSeat = await db.collection('board_seats').findOne({
      collegeId, userId: user.id, status: 'ACTIVE',
    })
    if (existingSeat) {
      return { error: 'Already a board member', code: ErrorCode.CONFLICT, status: 409 }
    }

    // Check for pending application
    const existingApp = await db.collection('board_applications').findOne({
      collegeId, userId: user.id, status: 'PENDING',
    })
    if (existingApp) {
      return { error: 'Application already pending', code: ErrorCode.CONFLICT, status: 409 }
    }

    // Check vacancy
    const activeSeats = await db.collection('board_seats').countDocuments({ collegeId, status: 'ACTIVE' })
    if (activeSeats >= BOARD_SIZE) {
      return { error: 'No vacant seats on this board', code: ErrorCode.VALIDATION, status: 400 }
    }

    const body = await request.json()
    const application = {
      id: uuidv4(),
      collegeId,
      userId: user.id,
      statement: (body.statement || '').slice(0, 500),
      status: 'PENDING',
      votes: { approve: 0, reject: 0 },
      voters: [],
      expiresAt: new Date(Date.now() + APPLICATION_WINDOW_DAYS * 24 * 60 * 60 * 1000),
      decidedAt: null,
      createdAt: new Date(),
    }

    await db.collection('board_applications').insertOne(application)
    await writeAudit(db, 'BOARD_APPLICATION_CREATED', user.id, 'COLLEGE', collegeId)

    const { _id, ...clean } = application
    return { data: { application: clean }, status: 201 }
  }

  // ========================
  // GET /governance/college/:collegeId/applications — Pending applications
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'applications' && method === 'GET') {
    const collegeId = path[2]

    const applications = await db.collection('board_applications')
      .find({ collegeId, status: 'PENDING' })
      .sort({ createdAt: -1 })
      .limit(20)
      .toArray()

    const userIds = applications.map(a => a.userId)
    const users = await db.collection('users').find({ id: { $in: userIds } }).toArray()
    const userMap = Object.fromEntries(users.map(u => [u.id, sanitizeUser(u)]))

    const enriched = applications.map(a => {
      const { _id, ...rest } = a
      return { ...rest, applicant: userMap[a.userId] || null }
    })

    return { data: { applications: enriched } }
  }

  // ========================
  // POST /governance/applications/:appId/vote — Vote on application
  // ========================
  if (path[0] === 'governance' && path[1] === 'applications' && path.length === 4 && path[3] === 'vote' && method === 'POST') {
    const user = await requireAuth(request, db)
    const appId = path[2]

    const application = await db.collection('board_applications').findOne({ id: appId })
    if (!application) return { error: 'Application not found', code: ErrorCode.NOT_FOUND, status: 404 }

    // Only board members can vote
    const seat = await db.collection('board_seats').findOne({
      collegeId: application.collegeId, userId: user.id, status: 'ACTIVE',
    })
    if (!seat) {
      return { error: 'Only board members can vote', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    // Check if already voted
    if (application.voters.includes(user.id)) {
      return { error: 'Already voted on this application', code: ErrorCode.CONFLICT, status: 409 }
    }

    const body = await request.json()
    const vote = body.vote // 'APPROVE' or 'REJECT'
    if (!['APPROVE', 'REJECT'].includes(vote)) {
      return { error: 'Vote must be APPROVE or REJECT', code: ErrorCode.VALIDATION, status: 400 }
    }

    const update = {
      $push: { voters: user.id },
      $inc: vote === 'APPROVE' ? { 'votes.approve': 1 } : { 'votes.reject': 1 },
    }

    await db.collection('board_applications').updateOne({ id: appId }, update)

    // Check if enough votes for decision (majority of current board)
    const totalBoardMembers = await db.collection('board_seats').countDocuments({
      collegeId: application.collegeId, status: 'ACTIVE',
    })
    const majority = Math.ceil(totalBoardMembers / 2)
    const updatedApp = await db.collection('board_applications').findOne({ id: appId })

    if (updatedApp.votes.approve >= majority) {
      // Auto-approve: create seat
      const nextSeat = await db.collection('board_seats').countDocuments({ collegeId: application.collegeId }) + 1
      await db.collection('board_seats').insertOne({
        id: uuidv4(),
        collegeId: application.collegeId,
        userId: application.userId,
        seatNumber: nextSeat,
        status: 'ACTIVE',
        joinedAt: new Date(),
        createdAt: new Date(),
      })
      await db.collection('board_applications').updateOne(
        { id: appId },
        { $set: { status: 'APPROVED', decidedAt: new Date() } }
      )
    } else if (updatedApp.votes.reject >= majority) {
      await db.collection('board_applications').updateOne(
        { id: appId },
        { $set: { status: 'REJECTED', decidedAt: new Date() } }
      )
    }

    return { data: { message: 'Vote recorded', vote } }
  }

  // ========================
  // POST /governance/college/:collegeId/proposals — Create proposal
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'proposals' && method === 'POST') {
    const user = await requireAuth(request, db)
    const collegeId = path[2]

    // Only board members can create proposals
    const seat = await db.collection('board_seats').findOne({
      collegeId, userId: user.id, status: 'ACTIVE',
    })
    if (!seat) {
      return { error: 'Only board members can create proposals', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    const body = await request.json()
    const { title, description, category } = body

    if (!title || !description) {
      return { error: 'title and description are required', code: ErrorCode.VALIDATION, status: 400 }
    }

    const proposal = {
      id: uuidv4(),
      collegeId,
      authorId: user.id,
      title: title.slice(0, 200),
      description: description.slice(0, 2000),
      category: category || 'GENERAL', // GENERAL, RULE_CHANGE, EVENT, MODERATION
      status: 'OPEN',
      votes: { for: 0, against: 0, abstain: 0 },
      voters: [],
      votingDeadline: new Date(Date.now() + PROPOSAL_VOTING_DAYS * 24 * 60 * 60 * 1000),
      decidedAt: null,
      createdAt: new Date(),
    }

    await db.collection('board_proposals').insertOne(proposal)
    await writeAudit(db, 'PROPOSAL_CREATED', user.id, 'COLLEGE', collegeId, { proposalId: proposal.id })

    const { _id, ...clean } = proposal
    return { data: { proposal: clean }, status: 201 }
  }

  // ========================
  // GET /governance/college/:collegeId/proposals — List proposals
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'proposals' && method === 'GET') {
    const collegeId = path[2]
    const url = new URL(request.url)
    const status = url.searchParams.get('status') || 'OPEN'

    const proposals = await db.collection('board_proposals')
      .find({ collegeId, status })
      .sort({ createdAt: -1 })
      .limit(20)
      .toArray()

    const authorIds = [...new Set(proposals.map(p => p.authorId))]
    const users = await db.collection('users').find({ id: { $in: authorIds } }).toArray()
    const userMap = Object.fromEntries(users.map(u => [u.id, sanitizeUser(u)]))

    const enriched = proposals.map(p => {
      const { _id, ...rest } = p
      return { ...rest, author: userMap[p.authorId] || null }
    })

    return { data: { proposals: enriched } }
  }

  // ========================
  // POST /governance/proposals/:proposalId/vote — Vote on proposal
  // ========================
  if (path[0] === 'governance' && path[1] === 'proposals' && path.length === 4 && path[3] === 'vote' && method === 'POST') {
    const user = await requireAuth(request, db)
    const proposalId = path[2]

    const proposal = await db.collection('board_proposals').findOne({ id: proposalId })
    if (!proposal) return { error: 'Proposal not found', code: ErrorCode.NOT_FOUND, status: 404 }

    if (proposal.status !== 'OPEN') {
      return { error: 'Proposal is no longer open for voting', code: ErrorCode.VALIDATION, status: 400 }
    }

    // Only board members can vote
    const seat = await db.collection('board_seats').findOne({
      collegeId: proposal.collegeId, userId: user.id, status: 'ACTIVE',
    })
    if (!seat) {
      return { error: 'Only board members can vote on proposals', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    if (proposal.voters.includes(user.id)) {
      return { error: 'Already voted on this proposal', code: ErrorCode.CONFLICT, status: 409 }
    }

    const body = await request.json()
    const vote = body.vote // 'FOR', 'AGAINST', 'ABSTAIN'
    if (!['FOR', 'AGAINST', 'ABSTAIN'].includes(vote)) {
      return { error: 'Vote must be FOR, AGAINST, or ABSTAIN', code: ErrorCode.VALIDATION, status: 400 }
    }

    const voteField = vote === 'FOR' ? 'votes.for' : vote === 'AGAINST' ? 'votes.against' : 'votes.abstain'
    await db.collection('board_proposals').updateOne(
      { id: proposalId },
      { $push: { voters: user.id }, $inc: { [voteField]: 1 } }
    )

    // Check if all board members voted → auto-resolve
    const totalBoard = await db.collection('board_seats').countDocuments({
      collegeId: proposal.collegeId, status: 'ACTIVE',
    })
    const updatedProposal = await db.collection('board_proposals').findOne({ id: proposalId })
    const totalVotes = updatedProposal.voters.length

    if (totalVotes >= totalBoard) {
      const status = updatedProposal.votes.for > updatedProposal.votes.against ? 'PASSED' : 'REJECTED'
      await db.collection('board_proposals').updateOne(
        { id: proposalId },
        { $set: { status, decidedAt: new Date() } }
      )
    }

    return { data: { message: 'Vote recorded', vote } }
  }

  // ========================
  // POST /governance/college/:collegeId/seed-board — Seed initial board (admin)
  // ========================
  if (path[0] === 'governance' && path[1] === 'college' && path.length >= 4 && path[3] === 'seed-board' && method === 'POST') {
    const user = await requireAuth(request, db)
    if (!['ADMIN', 'SUPER_ADMIN'].includes(user.role)) {
      return { error: 'Admin access required', code: ErrorCode.FORBIDDEN, status: 403 }
    }

    const collegeId = path[2]
    const existing = await db.collection('board_seats').countDocuments({ collegeId, status: 'ACTIVE' })
    if (existing > 0) {
      return { error: 'Board already has members', code: ErrorCode.CONFLICT, status: 409 }
    }

    // Auto-seed: top followers from this college
    const topUsers = await db.collection('users')
      .find({ collegeId, onboardingComplete: true })
      .sort({ followersCount: -1 })
      .limit(BOARD_SIZE)
      .toArray()

    const seats = topUsers.map((u, i) => ({
      id: uuidv4(),
      collegeId,
      userId: u.id,
      seatNumber: i + 1,
      status: 'ACTIVE',
      joinedAt: new Date(),
      createdAt: new Date(),
    }))

    if (seats.length > 0) {
      await db.collection('board_seats').insertMany(seats)
    }

    await writeAudit(db, 'BOARD_SEEDED', user.id, 'COLLEGE', collegeId, { seatsCreated: seats.length })

    return { data: { message: `Board seeded with ${seats.length} members`, seats: seats.map(s => { const { _id, ...rest } = s; return rest }) }, status: 201 }
  }

  return null
}
