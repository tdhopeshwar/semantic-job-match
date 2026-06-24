import ScoreBar from './ScoreBar'
import SkillTags from './SkillTags'
import styles from './JobCard.module.css'

export default function JobCard({ job, rank }) {
  return (
    <article className={styles.card}>
      <div className={styles.rank}>{String(rank).padStart(2, '0')}</div>
      <div className={styles.body}>
        <div className={styles.header}>
          <div>
            <h3 className={styles.title}>{job.title}</h3>
            <p className={styles.company}>
              {job.company}
              {job.location && <span className={styles.location}> · {job.location}</span>}
            </p>
          </div>
          <ScoreBar score={job.score} />
        </div>
        <p className={styles.snippet}>{job.description_snippet}…</p>
        <SkillTags matched={job.matched_skills} missing={job.missing_skills} />
      </div>
    </article>
  )
}
