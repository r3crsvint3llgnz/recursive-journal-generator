import { useState } from 'react'
import PropTypes from 'prop-types'
import { requestUploadUrl } from '../lib/api.js'

const initialState = { status: 'idle', message: '', importId: null }

const UploadPanel = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null)
  const [feedback, setFeedback] = useState(initialState)

  const resetFeedback = () => setFeedback(initialState)

  const handleFileChange = (event) => {
    resetFeedback()
    const selected = event.target.files?.[0]
    setFile(selected || null)
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    if (!file) {
      setFeedback({ status: 'error', message: 'Select a JSON export before uploading.' })
      return
    }

    setFeedback({ status: 'pending', message: 'Requesting upload slot…' })

    try {
      const presign = await requestUploadUrl({ contentType: file.type || 'application/json' })
      await uploadToS3(presign.presigned, file)
      setFeedback({ status: 'success', message: 'Upload accepted. Import will process shortly.', importId: presign.import_id })
      setFile(null)
      if (typeof onUploadComplete === 'function') {
        onUploadComplete(presign.import_id)
      }
    } catch (error) {
      setFeedback({ status: 'error', message: error.message || 'Upload failed' })
    }
  }

  return (
    <section className="card">
      <h2>Upload Chat Export</h2>
      <p style={{ color: '#cbd5f5' }}>
        Export your ChatGPT or Claude history as JSON, then drop it here to kick off the normalization pipeline.
      </p>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept="application/json,.json"
          onChange={handleFileChange}
          style={{ margin: '1rem 0', display: 'block' }}
        />
        <button className="button primary" type="submit" disabled={!file || feedback.status === 'pending'}>
          {feedback.status === 'pending' ? 'Uploading…' : 'Upload Export'}
        </button>
      </form>
      {feedback.message && (
        <p
          style={{
            marginTop: '1rem',
            color: feedback.status === 'error' ? '#fca5a5' : '#cbd5f5'
          }}
        >
          {feedback.message}
          {feedback.importId && (
            <span style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8' }}>
              Import ID: {feedback.importId}
            </span>
          )}
        </p>
      )}
    </section>
  )
}

async function uploadToS3(presigned, file) {
  const formData = new FormData()
  Object.entries(presigned.fields).forEach(([key, value]) => {
    formData.append(key, value)
  })
  formData.append('file', file)

  const response = await fetch(presigned.url, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error('S3 upload failed. Check file size and try again.')
  }
}

UploadPanel.propTypes = {
  onUploadComplete: PropTypes.func
}

export default UploadPanel
