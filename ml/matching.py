from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_student_text(profile):
    return profile.skills.lower()

def build_job_text(job):
    return job.required_skills.lower()

def compute_recommendations(student_profile, open_jobs, top_n=10):
    if not open_jobs: return []
    student_text = build_student_text(student_profile)
    job_texts = [build_job_text(j) for j in open_jobs]
    corpus = [student_text] + job_texts
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,1), min_df=1, max_features=5000)
        tfidf = vectorizer.fit_transform(corpus)
    except ValueError: return []
    scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    ranked = sorted(zip(open_jobs, scores), key=lambda x: x[1], reverse=True)
    # Zero-scoring jobs are kept (just ranked at the bottom), not dropped --
    # a student should see all eligible open jobs in their matches, even
    # ones with a weak/zero raw similarity score.
    return [(job, round(float(s)*100, 1)) for job, s in ranked][:top_n]

def compute_skill_gap(student_profile, job):
    student_skills = {s.lower() for s in student_profile.skills_list()}
    matched, missing, seen = [], [], set()
    for skill in job.skills_list():
        key = skill.lower()
        if key in seen: continue
        seen.add(key)
        (matched if key in student_skills else missing).append(skill)
    return matched, missing

def compute_match_score(student_profile, job, raw_score):
    """A single 0-100 score meant to reflect genuine match quality, not just
    where a job ranks within one student's own recommendation batch. Pure
    batch-relative normalization (old approach: scale the best score in the
    batch to 100) could show "100" for a job the student barely matches, as
    long as it happened to be the least-bad option in a weak batch.

    Blends the directly-explainable skill overlap ratio (matched / total
    required skills for this job) with the TF-IDF cosine similarity,
    weighting skill overlap more heavily since "matched 1 of 3 skills" is
    something a student can actually verify, unlike a raw similarity score."""
    matched, missing = compute_skill_gap(student_profile, job)
    total_required = len(matched) + len(missing)
    skill_overlap_pct = (len(matched) / total_required * 100) if total_required > 0 else 0.0
    return round(0.7 * skill_overlap_pct + 0.3 * raw_score, 1)

def save_recommendations(student_profile, open_jobs):
    from applications.models import Recommendation
    scored = compute_recommendations(student_profile, open_jobs)
    Recommendation.objects.filter(student=student_profile).delete()
    if scored:
        # Store the blended match score (not the raw cosine score) so that
        # Recommendation's -compatibility_score ordering matches what's
        # actually displayed as the match score everywhere it's shown.
        Recommendation.objects.bulk_create([
            Recommendation(student=student_profile, job=job, compatibility_score=compute_match_score(student_profile, job, raw_score))
            for job, raw_score in scored
        ])
    return scored
