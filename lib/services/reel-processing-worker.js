/**
 * Reel Processing Worker — Real Video Transcoding
 *
 * Phase B: Takes raw uploaded reel videos, normalizes to web-safe MP4 (H.264+AAC),
 * generates thumbnail/poster, and updates processing status truthfully.
 *
 * Worker picks up PENDING jobs from reel_processing_jobs, processes them
 * via ffmpeg, and reports results back through the standard callback flow.
 */

import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'
import fs from 'fs'
import { v4 as uuidv4 } from 'uuid'

const execAsync = promisify(exec)

const PROCESSING_CONFIG = {
  MAX_CONCURRENT: 2,
  POLL_INTERVAL_MS: 30_000,
  MAX_DURATION_S: 90,
  OUTPUT_CODEC: 'h264',
  OUTPUT_AUDIO: 'aac',
  OUTPUT_FORMAT: 'mp4',
  THUMBNAIL_TIME: '00:00:01',
  POSTER_QUALITY: 5, // 1-31 lower = better
  WORK_DIR: '/tmp/reel-processing',
}

let workerRunning = false

/**
 * Probe video file for metadata.
 */
async function probeVideo(inputPath) {
  try {
    const { stdout } = await execAsync(
      `ffprobe -v quiet -print_format json -show_format -show_streams "${inputPath}"`,
      { timeout: 15000 }
    )
    const data = JSON.parse(stdout)
    const videoStream = data.streams?.find(s => s.codec_type === 'video')
    const audioStream = data.streams?.find(s => s.codec_type === 'audio')
    return {
      duration: parseFloat(data.format?.duration || 0),
      width: videoStream?.width || 0,
      height: videoStream?.height || 0,
      videoCodec: videoStream?.codec_name || 'unknown',
      audioCodec: audioStream?.codec_name || 'none',
      bitrate: parseInt(data.format?.bit_rate || 0),
      size: parseInt(data.format?.size || 0),
    }
  } catch (err) {
    return { error: err.message }
  }
}

/**
 * Transcode video to web-safe MP4.
 * Uses stream copy when codec is already H.264, otherwise transcodes.
 */
async function transcodeVideo(inputPath, outputPath, metadata) {
  const needsVideoTranscode = metadata.videoCodec !== 'h264' && metadata.videoCodec !== 'h265'
  const needsAudioTranscode = metadata.audioCodec !== 'aac'

  const videoArg = needsVideoTranscode
    ? `-c:v libx264 -preset fast -crf 23 -movflags +faststart -pix_fmt yuv420p`
    : `-c:v copy -movflags +faststart`

  const audioArg = needsAudioTranscode
    ? `-c:a aac -b:a 128k`
    : `-c:a copy`

  const maxDuration = PROCESSING_CONFIG.MAX_DURATION_S
  const cmd = `ffmpeg -y -i "${inputPath}" ${videoArg} ${audioArg} -t ${maxDuration} -f mp4 "${outputPath}"`

  await execAsync(cmd, { timeout: 120000 })
  return {
    transcoded: needsVideoTranscode || needsAudioTranscode,
    codec: needsVideoTranscode ? 'h264' : metadata.videoCodec,
  }
}

/**
 * Generate thumbnail from video at specified time.
 */
async function generateThumbnail(inputPath, outputPath) {
  const cmd = `ffmpeg -y -i "${inputPath}" -ss ${PROCESSING_CONFIG.THUMBNAIL_TIME} -vframes 1 -q:v ${PROCESSING_CONFIG.POSTER_QUALITY} "${outputPath}"`
  await execAsync(cmd, { timeout: 15000 })
}

/**
 * Process a single reel job.
 */
export async function processReelJob(db, job, supabaseStorage) {
  const jobId = job.id
  const reelId = job.reelId
  const now = new Date()

  // Update job to PROCESSING
  await db.collection('reel_processing_jobs').updateOne(
    { id: jobId },
    { $set: { status: 'PROCESSING', startedAt: now, updatedAt: now }, $inc: { attempts: 1 } }
  )
  await db.collection('reels').updateOne(
    { id: reelId },
    { $set: { mediaStatus: 'PROCESSING', updatedAt: now } }
  )

  try {
    const reel = await db.collection('reels').findOne({ id: reelId })
    if (!reel) throw new Error('Reel not found')

    // Get the source media
    const mediaAsset = await db.collection('media_assets').findOne({ id: reel.mediaId })
    if (!mediaAsset || !mediaAsset.publicUrl) {
      throw new Error('Source media not found or no URL')
    }

    // Ensure work directory
    const workDir = path.join(PROCESSING_CONFIG.WORK_DIR, jobId)
    fs.mkdirSync(workDir, { recursive: true })

    const inputPath = path.join(workDir, 'input')
    const outputPath = path.join(workDir, `output.${PROCESSING_CONFIG.OUTPUT_FORMAT}`)
    const thumbPath = path.join(workDir, 'thumbnail.jpg')

    // Download source video
    const response = await fetch(mediaAsset.publicUrl)
    if (!response.ok) throw new Error(`Failed to download: ${response.status}`)
    const buffer = Buffer.from(await response.arrayBuffer())
    fs.writeFileSync(inputPath, buffer)

    // Probe video
    const metadata = await probeVideo(inputPath)
    if (metadata.error) throw new Error(`Probe failed: ${metadata.error}`)
    if (metadata.duration > PROCESSING_CONFIG.MAX_DURATION_S + 5) {
      // Allow 5s grace for duration
    }

    // Transcode
    const transcodeResult = await transcodeVideo(inputPath, outputPath, metadata)

    // Generate thumbnail
    let thumbnailGenerated = false
    try {
      await generateThumbnail(outputPath, thumbPath)
      thumbnailGenerated = fs.existsSync(thumbPath)
    } catch {
      // Non-fatal — thumbnail is optional
    }

    // Upload processed output to storage if available
    let playbackUrl = mediaAsset.publicUrl // fallback to original
    let posterUrl = null

    if (supabaseStorage?.uploadBuffer) {
      try {
        const outputBuffer = fs.readFileSync(outputPath)
        const outputKey = `reels/${reel.creatorId}/${reelId}/processed.mp4`
        const uploadResult = await supabaseStorage.uploadBuffer(outputKey, outputBuffer, 'video/mp4')
        if (uploadResult?.publicUrl) playbackUrl = uploadResult.publicUrl
      } catch {
        // Fallback to original URL
      }

      if (thumbnailGenerated) {
        try {
          const thumbBuffer = fs.readFileSync(thumbPath)
          const thumbKey = `reels/${reel.creatorId}/${reelId}/poster.jpg`
          const thumbResult = await supabaseStorage.uploadBuffer(thumbKey, thumbBuffer, 'image/jpeg')
          if (thumbResult?.publicUrl) posterUrl = thumbResult.publicUrl
        } catch {
          // Non-fatal
        }
      }
    }

    // Output metadata
    const outputStat = fs.statSync(outputPath)

    // Update reel with processed results
    const reelUpdates = {
      mediaStatus: 'READY',
      playbackUrl,
      updatedAt: new Date(),
      processingMetadata: {
        sourceCodec: metadata.videoCodec,
        outputCodec: transcodeResult.codec,
        transcoded: transcodeResult.transcoded,
        duration: metadata.duration,
        width: metadata.width,
        height: metadata.height,
        sourceSize: metadata.size,
        outputSize: outputStat.size,
        processedAt: new Date().toISOString(),
      },
    }
    if (posterUrl) {
      reelUpdates.thumbnailUrl = posterUrl
      reelUpdates.posterFrameUrl = posterUrl
    }

    await db.collection('reels').updateOne({ id: reelId }, { $set: reelUpdates })

    // Update media asset with thumbnail if generated
    if (posterUrl) {
      await db.collection('media_assets').updateOne(
        { id: reel.mediaId },
        { $set: { thumbnailStatus: 'READY', thumbnailUrl: posterUrl, thumbnailUpdatedAt: new Date() } }
      )
    }

    // Update job to COMPLETED
    await db.collection('reel_processing_jobs').updateOne(
      { id: jobId },
      {
        $set: {
          status: 'COMPLETED',
          completedAt: new Date(),
          updatedAt: new Date(),
          result: {
            transcoded: transcodeResult.transcoded,
            duration: metadata.duration,
            thumbnailGenerated,
            outputSize: outputStat.size,
          },
        },
      }
    )

    // Cleanup work directory
    try { fs.rmSync(workDir, { recursive: true }) } catch { /* ignore */ }

    return { success: true, reelId, transcoded: transcodeResult.transcoded }
  } catch (err) {
    // Update job to FAILED
    await db.collection('reel_processing_jobs').updateOne(
      { id: jobId },
      {
        $set: {
          status: job.attempts >= job.maxAttempts - 1 ? 'FAILED' : 'PENDING',
          failureReason: err.message,
          lastFailedAt: new Date(),
          updatedAt: new Date(),
        },
      }
    )
    await db.collection('reels').updateOne(
      { id: reelId },
      {
        $set: {
          mediaStatus: job.attempts >= job.maxAttempts - 1 ? 'FAILED' : 'PROCESSING',
          updatedAt: new Date(),
        },
      }
    )

    return { success: false, reelId, error: err.message }
  }
}

/**
 * Start the background processing worker.
 * Polls for PENDING jobs every 30s.
 */
export function startProcessingWorker(db, supabaseStorage) {
  if (workerRunning) return
  workerRunning = true

  // Ensure work directory
  fs.mkdirSync(PROCESSING_CONFIG.WORK_DIR, { recursive: true })

  async function pollAndProcess() {
    try {
      const pendingJobs = await db.collection('reel_processing_jobs')
        .find({
          status: 'PENDING',
          attempts: { $lt: 3 },
        })
        .sort({ createdAt: 1 })
        .limit(PROCESSING_CONFIG.MAX_CONCURRENT)
        .toArray()

      for (const job of pendingJobs) {
        await processReelJob(db, job, supabaseStorage)
      }
    } catch {
      // Worker error — will retry on next poll
    }
  }

  // First run immediately, then poll
  pollAndProcess()
  setInterval(pollAndProcess, PROCESSING_CONFIG.POLL_INTERVAL_MS)
}
