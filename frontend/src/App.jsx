import { useState, useCallback, useEffect } from 'react'
import UploadZone from './components/UploadZone'
import ScanningState from './components/ScanningState'
import ResumeSummary from './components/ResumeSummary'
import JobCard from './components/JobCard'
import ErrorBanner from './components/ErrorBanner'
import { matchResume, checkHealth } from './utils/api'
import styles from './App.module.css'

const STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  RESULTS: 'results',
  ERROR: 'error',
}

export default function App() {
  const [status, setStatus] = useState(STATUS.IDLE)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [backendUp, setBackendUp] = useState(null)

  useEffect(() => {
    checkHealth().then((health) => {
      setBackendUp(!!health?.index_loaded)
    })
  }, [])

  const handleFileSelected = useCallback(async (file) => {
    setStatus(STATUS.LOADING)
    setError(null)
    try {
      const data = await matchResume(file, 10)
      setResult(data)
      setStatus(STATUS.RESULTS)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
      setStatus(STATUS.ERROR)
    }
  }, [])

  const handleReset = useCallback(() => {
    setStatus(STATUS.IDLE)
    setResult(null)
    setError(null)
  }, [])

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Semantic Job Match</p>
        <h1 className={styles.headline}>
          Find the roles your resume<br />actually fits.
        </h1>
        <p className={styles.subhead}>
          Upload a resume. A Sentence-BERT model embeds it and searches a FAISS index
          of job postings for the closest semantic matches — with a breakdown of which
          skills matched and which are missing.
        </p>
      </header>

      <main className={styles.main}>
        {backendUp === false && (
          <ErrorBanner
            message="Can't reach the matching server, or the job index hasn't been built yet. Make sure the backend is running on port 8000."
            onDismiss={() => setBackendUp(null)}
          />
        )}

        {status === STATUS.ERROR && (
          <ErrorBanner message={error} onDismiss={handleReset} />
        )}

        {(status === STATUS.IDLE || status === STATUS.ERROR) && (
          <UploadZone onFileSelected={handleFileSelected} disabled={false} />
        )}

        {status === STATUS.LOADING && <ScanningState />}

        {status === STATUS.RESULTS && result && (
          <>
            <ResumeSummary
              skills={result.resume_skills}
              jobCount={result.total_jobs_searched}
              onReset={handleReset}
            />
            <div className={styles.results}>
              {result.matches.length === 0 ? (
                <p className={styles.empty}>
                  No strong matches found in the current index. Try a different resume,
                  or expand the job dataset.
                </p>
              ) : (
                result.matches.map((job, i) => (
                  <JobCard key={job.job_id} job={job} rank={i + 1} />
                ))
              )}
            </div>
          </>
        )}
      </main>

      <footer className={styles.footer}>
        <p>Built with Sentence-BERT, FAISS, and FastAPI · by Tanisha Dhopeshwar</p>
      </footer>
    </div>
  )
}
